import keyword
import math
from collections import ChainMap
from functools import singledispatchmethod
from typing import Callable, TypeVar

import libsbml
from symbolite import Symbol
from symbolite.abstract import symbol
from symbolite.core import substitute

from ...core import Compartment, Constant, Parameter, Reaction, Species, initial
from ..mathML.importer import mapper
from . import from_libsbml, types

T = TypeVar("T")


class DynamicCompartment:
    def __init__(self, *, name_mapper: Callable[[str], str] = lambda x: x):
        self.name_mapping: dict[str, str] = {}
        self.name_mapper = name_mapper
        self.namespace = Compartment.__prepare__(None, ())

    def build(self, name: str):
        return type(name, (Compartment,), self.namespace)

    def add(self, name: str, value):
        self.name_mapping[name] = new_name = self.name_mapper(name)
        self.namespace[new_name] = value

    def __getattr__(self, name):
        try:
            new_name = self.name_mapping[name]
            return self.namespace[new_name]
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
    converted_model: types.Model = from_libsbml.convert(model)
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

        for c in model.compartments:
            self.add_compartment(c)
        for s in model.species:
            self.add_species(s)
        for p in model.parameters:
            self.add_parameter(p)
        for i in model.initial_assignments:
            self.add_initial_assignment(i)
        for r in model.rules:
            self.add(r)
        for r in model.reactions:
            self.add_reaction(r)
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
        # spatial_dimensions
        # units
        if c.size is None:
            size = 1
        else:
            size = c.size

        if c.constant:
            self.simbio.add(c.id, Constant(default=size))
        else:
            # TODO: or Variable?
            self.simbio.add(c.id, Parameter(default=size))

    @add.register
    def add_parameter(self, p: types.Parameter):
        if p.constant:
            self.simbio.add(p.id, Constant(default=p.value))
        else:
            self.simbio.add(p.id, Parameter(default=p.value))

    @add.register
    def add_species(self, s: types.Species):
        match [s.initial_amount, s.initial_concentration]:
            case [math.nan | None, math.nan | None]:
                value = None
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

        self.simbio.add(s.id, initial(default=value))

    def get_symbol(self, name: str, expected_type: type[T] = object) -> T:
        value = getattr(self.simbio, name)
        if not isinstance(value, expected_type):
            raise TypeError(f"unexpected type: {type(value)}")
        return value

    def get_species_reference(self, s: types.SimpleSpeciesReference) -> Species:
        species = self.get_symbol(s.species, Species)
        if isinstance(s, types.SpeciesReference) and s.stoichiometry is not None:
            return Species(species.variable, s.stoichiometry)
        else:
            return Species(species.variable)

    @add.register
    def add_reaction(self, r: types.Reaction):
        reactants = [self.get_species_reference(s) for s in r.reactants]
        products = [self.get_species_reference(s) for s in r.products]
        modifiers = [self.get_species_reference(s) for s in r.modifiers]
        for m in modifiers:
            reactants.append(m)
            products.append(m)
        kinetic_law = r.kinetic_law
        if len(kinetic_law.parameters) > 0:
            raise NotImplementedError("local parameters are not yet implemented")
        formula = substitute(kinetic_law.math, GetAsVariable(self.get))

        if not r.reversible:
            self.simbio.add(
                r.id,
                Reaction(reactants=reactants, products=products, rate_law=formula),
            )
            return

        match formula:
            case Symbol(
                expression=symbol.Expression(func=symbol.sub, args=(forward, reverse))
            ):
                pass
            case Symbol(
                expression=symbol.Expression(
                    func=symbol.mul,
                    args=(
                        compartment,
                        Symbol(
                            expression=symbol.Expression(
                                func=symbol.sub, args=(forward, reverse)
                            )
                        ),
                    )
                    | (
                        Symbol(
                            expression=symbol.Expression(
                                func=symbol.sub, args=(forward, reverse)
                            )
                        ),
                        compartment,
                    ),
                )
            ):
                forward = compartment * forward
                reverse = compartment * reverse
            case _:
                raise ValueError(
                    f"{r.name} is a reversible formula without minus: {formula}"
                )

        self.simbio.add(
            f"{r.name}_forward",
            Reaction(reactants=reactants, products=products, rate_law=forward),
        )
        self.simbio.add(
            f"{r.name}_reverse",
            Reaction(reactants=products, products=reactants, rate_law=reverse),
        )

    @add.register
    def add_initial_assignment(self, a: types.InitialAssignment):
        value = substitute(a.math, GetAsVariable(self.get))
        component = self.get_symbol(a.id)
        if isinstance(component, Species):
            component.variable.initial = value
        elif isinstance(component, Constant | Parameter):
            component.default = value
        else:
            raise TypeError(
                f"cannot perform initial assignment for {a.id} of type {type(value)}"
            )

    @add.register
    def add_assignment_rule(self, r: types.AssignmentRule):
        value = substitute(r.math, GetAsVariable(self.get))
        component = self.get_symbol(r.id, Parameter)
        component.default = value

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
