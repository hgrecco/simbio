import keyword
import math
from collections import ChainMap
from functools import singledispatchmethod
from typing import Callable, TypeVar

import libsbml
from symbolite import Symbol
from symbolite import abstract as libabstract
from symbolite.core import substitute

from ...core import Compartment, Constant, Parameter, Reaction, Species, initial
from ..mathML.importer import mapper
from . import from_libsbml, types

T = TypeVar("T")


class DynamicCompartment:
    def __init__(self, *, name_mapper: Callable[[str], str] = lambda x: x):
        self.name_mapping = {}
        self.name_mapper = name_mapper
        self.namespace = Compartment.__prepare__(None, ())

    def build(self, name: str):
        return type(name, (Compartment,), self.namespace)

    def add(self, name: str, value):
        self.name_mapping[name] = name = self.name_mapper(name)
        self.namespace[name] = value

    def __getattr__(self, name):
        try:
            name = self.name_mapping[name]
            return self.namespace[name]
        except KeyError as e:
            e.add_note("component not found in Compartment")
            raise


def read_model(
    file: str,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    with open(file) as f:
        text = f.read()
    return parse_model(text, name=name, identity_mapper=identity_mapper)


def parse_model(
    sbml: str,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    document: libsbml.SBMLDocument = libsbml.readSBMLFromString(sbml)
    if document.getNumErrors() != 0:
        raise RuntimeError("error reading the SBML file")

    model: libsbml.Model = document.getModel()
    converted_model = from_libsbml.convert(model)
    return convert_model(converted_model, name=name, identity_mapper=identity_mapper)


def convert_model(
    model: types.Model,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
) -> type[Compartment]:
    if name is None:
        name = model.name
        if name is None:
            raise ValueError("must provide a name for the model")
    return SBMLImporter(model, identity_mapper=identity_mapper).simbio.build(name=name)


def _extra_check(func: Callable[[str], str]):
    def is_python_identifier(x: str) -> str:
        y = func(x)
        if keyword.iskeyword(y):
            raise NameError(
                f"{y} is not a valid name, it is a Python reserved keyword."
            )
        else:
            return y

    return is_python_identifier


class SBMLImporter:
    def __init__(
        self,
        model: types.Model,
        *,
        identity_mapper: Callable[[str], str] = lambda x: x,
    ):
        self.model = model
        self.simbio = DynamicCompartment(name_mapper=_extra_check(identity_mapper))

        self.mapper = ChainMap({}, mapper)
        self.functions = {}
        self.mapper[libsbml.AST_FUNCTION] = self.functions
        for f in model.functions:
            self.functions[f.id] = f.math

        self.initial_assignments = {a.symbol: a.math for a in model.initial_assignments}
        self.assignment_rules = {
            r.variable: r.math
            for r in model.rules
            if isinstance(r, types.AssignmentRule)
        }

        if len(model.compartments) > 1:
            raise NotImplementedError("compartment")

        for p in model.parameters:
            self.add(p)

        for s in model.species:
            self.add(s)

        for r in model.rules:
            self.add(r)

        for r in model.reactions:
            self.add(r)

        for a in model.constraints:
            self.add(a)

        for a in model.events:
            self.add(a)

    def get(self, item, default=None):
        match item:
            case Symbol(name=None):
                return item
            case Symbol(name=name):
                return getattr(self.simbio, name)
            case _:
                return item

    @singledispatchmethod
    def add(self, x):
        raise NotImplementedError(type(x))

    @add.register
    def add_compartment(self, c: types.Compartment):
        raise NotImplementedError(type(c))

    @add.register
    def add_parameter(self, p: types.Parameter):
        try:
            value = self.initial_assignments[p.id]
        except KeyError:
            value = p.value
        else:
            value = substitute(value, self)

        if p.constant:
            self.simbio.add(p.id, Constant(default=value))
        else:
            self.simbio.add(p.id, Parameter(default=value))

    @add.register
    def add_species(self, s: types.Species):
        try:
            value = self.initial_assignments[s.id]
        except KeyError:
            match [s.initial_amount, s.initial_concentration]:
                case [math.nan | None, math.nan | None]:
                    raise ValueError(f"Species {s.id} has no initial condition")
                case [value, math.nan | None]:
                    pass
                case [math.nan | None, value]:
                    # TODO: use units!
                    # raise NotImplementedError("should use units?")
                    pass
                case _:
                    raise ValueError(
                        f"both amount an concentration specified for Species {s.id}"
                    )

        else:
            value = substitute(value, self)

        self.simbio.add(s.id, initial(default=value))

    def get_symbol(self, name: str, expected_type: type[T] = object) -> T:
        value = getattr(self.simbio, name)
        if not isinstance(value, expected_type):
            raise TypeError(f"unexpected type: {type(value)}")
        return value

    def get_species_reference(self, s: types.SpeciesReference) -> Species:
        species = self.get_symbol(s.species, Species)
        st = s.stoichiometry
        if st is None:
            st = 1
        return Species(species.variable, st)

    @add.register
    def add_reaction(self, r: types.Reaction):
        reactants = [self.get_species_reference(s) for s in r.reactants]
        products = [self.get_species_reference(s) for s in r.products]
        kinetic_law = r.kinetic_law
        formula = substitute(kinetic_law.math, GetAsVariable(self.get))
        if not r.reversible:
            self.simbio.add(
                r.id,
                Reaction(reactants=reactants, products=products, rate_law=formula),
            )
        else:
            if formula.expression.func is not libabstract.symbol.sub:
                raise ValueError(
                    f"{r.name} is a reversible formula without minus: {formula}"
                )
            forward, reverse = formula.expression.args
            self.simbio.add(
                f"{r.name}_forward",
                Reaction(reactants=reactants, products=products, rate_law=forward),
            )
            self.simbio.add(
                f"{r.name}_reverse",
                Reaction(reactants=products, products=reactants, rate_law=reverse),
            )

    @add.register
    def add_assignment_rule(self, r: types.AssignmentRule):
        rule = substitute(r.math, GetAsVariable(self.get))
        p = Parameter(default=rule)
        self.simbio.add(r.id, p)

    @add.register
    def add_rate_rule(self, r: types.RateRule):
        species: Species = getattr(self.simbio, r.id)
        formula: Symbol = substitute(r.math, GetAsVariable(self.get))
        eq = species.variable.derive() << formula
        self.simbio.add(f"{r.id}_rate_rule", eq)

    @add.register
    def add_algebraic_rule(self, r: types.AlgebraicRule):
        raise NotImplementedError("algebraic rules are not yet supported")


class GetAsVariable:
    def __init__(self, getter):
        self.getter = getter

    def get(self, key, default=None):
        value = self.getter(key, default=None)
        if isinstance(value, Species):
            return value.variable
        else:
            return value
