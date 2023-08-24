import keyword
import math
from collections import ChainMap
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
    def __init__(self, name: str, *, name_mapper: Callable[[str], str] = lambda x: x):
        self.mapping = {}
        self.name_mapper = name_mapper
        self.compartment = type(name, (Compartment,), {})

    def add(self, name: str, value):
        self.mapping[name] = name = self.name_mapper(name)
        value.__set_name__(self.compartment, name)
        setattr(self.compartment, name, value)

    def __getattr__(self, name):
        try:
            name = self.mapping[name]
            return getattr(self.compartment, name)
        except (KeyError, AttributeError) as e:
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
    return SBMLImporter(
        model, name=name, identity_mapper=identity_mapper
    ).simbio.compartment


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
        name: str | None = None,
        identity_mapper: Callable[[str], str] = lambda x: x,
    ):
        if name is None:
            name = model.name
        self.model = model
        self.simbio = DynamicCompartment(
            name,
            name_mapper=_extra_check(identity_mapper),
        )

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
            self.add_parameter(p)

        for s in model.species:
            self.add_species(s)

        for r in model.rules:
            if isinstance(r, types.AssignmentRule):
                continue
            elif isinstance(r, types.RateRule):
                raise NotImplementedError("rate rules")
            elif isinstance(r, types.AlgebraicRule):
                raise NotImplementedError("algebraic rules are not yet supported")
            else:
                raise NotImplementedError("this rule type is not supported", type(r))

        for r in model.reactions:
            self.add_reaction(r)

        for a in model.constraints:
            raise NotImplementedError("constraints")

        for a in model.events:
            raise NotImplementedError("events")

    def get(self, item, default=None):
        match item:
            case Symbol(name=None):
                return item
            case Symbol(name=name):
                return getattr(self.simbio, name)
            case _:
                return item

    def add_compartment(self, c: types.Compartment):
        raise NotImplementedError

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

    def add_reaction(self, r: types.Reaction):
        reactants = [self.get_species_reference(s) for s in r.reactants]
        products = [self.get_species_reference(s) for s in r.products]
        kinetic_law = r.kinetic_law
        formula = substitute(kinetic_law.math, self)
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
            for k, v in zip(["forward", "reverse"], formula.expression.args):
                self.simbio.add(
                    f"{r.name}_{k}",
                    Reaction(reactants=reactants, products=products, rate_law=v),
                )
