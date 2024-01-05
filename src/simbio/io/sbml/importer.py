import keyword
import math
from dataclasses import replace
from functools import reduce, singledispatchmethod
from operator import mul
from os import PathLike
from typing import Callable, Mapping, Sequence, TypeVar

import libsbml
import pint
from symbolite import Symbol
from symbolite.abstract import symbol
from symbolite.core import substitute, substitute_by_name

from ... import (
    Compartment,
    Constant,
    Independent,
    Parameter,
    RateLaw,
    Species,
    initial,
)
from ..mathML.importer import MathMLSpecialSymbol, MathMLSymbol
from . import from_libsbml, types

T = TypeVar("T")


def nan_to_none(x):
    if x is None or math.isnan(x):
        return None
    else:
        return x


class DynamicCompartment:
    def __init__(self, *, name_mapper: Callable[[str], str] = lambda x: x):
        self.name_mapping: dict[str, str] = {}
        self.name_mapper = name_mapper
        self.namespace = Compartment.__prepare__(None, ())
        self._annotations = self.namespace.setdefault("__annotations__", {})

    def build(self, name: str):
        return type(name, (Compartment,), self.namespace)

    def add(self, name: str, value, *, init: bool = True):
        self.name_mapping[name] = new_name = self.name_mapper(name)
        self.namespace[new_name] = value
        if init:
            self._annotations[new_name] = type(value)

    def __getattr__(self, name):
        try:
            new_name = self.name_mapping[name]
            return self.namespace[new_name]
        except KeyError as e:
            raise AttributeError(*e.args)


def load(
    file: PathLike,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    with open(file) as f:
        text = f.read()
    return loads(text, name=name, identity_mapper=identity_mapper)


def loads(
    sbml: str,
    *,
    name: str | None = None,
    identity_mapper: Callable[[str], str] = lambda x: x,
):
    document: libsbml.SBMLDocument = libsbml.readSBMLFromString(sbml)
    if document.getNumErrors() != 0:
        raise RuntimeError("error reading the SBML file")

    model: libsbml.Model = document.getModel()
    converted_model: types.Model = from_libsbml.Converter().convert(model)
    return convert(converted_model, name=name, identity_mapper=identity_mapper)


def convert(
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
            return f".{y}"
        else:
            return y

    return is_python_identifier


class SBMLImporter:
    def __init__(
        self,
        model: types.Model,
        *,
        identity_mapper: Callable[[str], str] = lambda x: x,
        units: bool = False,
    ):
        self.model = model
        self.simbio = DynamicCompartment(name_mapper=_extra_check(identity_mapper))

        self.use_units = units
        if self.use_units:
            self.unit_registry = pint.get_application_registry()
            self.units = {
                u.id: reduce(mul, map(self.get_unit_from_registry, u.units))
                for u in model.units
            }

        self.species = {s.id: s for s in model.species}
        self.initials = {i.id: i for i in model.initial_assignments}
        self.algebraic_rules: Sequence[types.AlgebraicRule] = []
        self.assignment_rules: Mapping[types.ID, types.AssignmentRule] = {}
        self.rate_rules: Mapping[types.ID, types.RateRule] = {}
        for r in model.rules:
            match r:
                case types.AssignmentRule():
                    self.assignment_rules[r.variable] = r
                case types.RateRule():
                    self.rate_rules[r.variable] = r
                case types.AlgebraicRule():
                    self.algebraic_rules.append(r)
                case _:
                    raise NotImplementedError(type(r))

        for x in model.compartments:
            self.add_compartment(x)
        for x in model.parameters:
            self.add_parameter(x)
        for x in model.species:
            self.add_species(x)
        for x in model.initial_assignments:
            self.add_initial_assignment(x)
        for x in model.reactions:
            self.add_reaction(x)
        for r in model.rules:
            self.add(r)
        for a in model.constraints:
            self.add_constaint(a)
        for a in model.events:
            self.add_event(a)

    def get(self, item, default=None):
        match item:
            case Symbol(name=None):
                return item
            case MathMLSymbol(name=name):
                return getattr(self.simbio, name)
            case MathMLSpecialSymbol(name=name):
                return self.get_or_create_independent(name)
            case _:
                return item

    def get_unit_from_registry(self, u: types.Unit) -> pint.Quantity:
        unit = getattr(self.unit_registry, u.kind.name)
        return (u.multiplier * 10**u.scale * unit) ** u.exponent

    @singledispatchmethod
    def add(self, x):
        raise NotImplementedError(type(x))

    def get_or_create_independent(self, name: str):
        try:
            return getattr(self.simbio, name)
        except AttributeError:
            value = Independent(default=0)
            self.simbio.add(name, value)
            return value

    @add.register
    def add_compartment(self, c: types.Compartment):
        # if c.spatial_dimensions is not None:
        # raise NotImplementedError("spatial_dimensions in compartment")
        size = nan_to_none(c.size)
        if self.use_units and c.units is not None and size is not None:
            size *= self.units[c.units]

        self.simbio.add(c.id, Parameter(default=size))

    @add.register
    def add_parameter(self, p: types.Parameter):
        if p.id in self.initials or p.id in self.assignment_rules:
            default = None  # add assignment later
        else:
            default = nan_to_none(p.value)

        if self.use_units and p.units is not None and default is not None:
            default *= self.units[p.units]

        if p.id in self.rate_rules:
            value = initial(default=default)
        else:
            value = Parameter(default=default)

        self.simbio.add(p.id, value)

    @add.register
    def add_species(self, s: types.Species):
        # compartment: ID
        # has_only_substance_units: bool
        if s.conversion_factor is not None:
            raise NotImplementedError("conversion_factor in species")
        if s.id in self.assignment_rules:
            # Parameter
            value = Parameter(default=None)  # AssignmentRule is set later
            self.simbio.add(s.id, value)
            return

        if s.id in self.initials:
            self.simbio.add(s.id, initial(default=None))  # value set later
            return

        match [nan_to_none(s.initial_amount), nan_to_none(s.initial_concentration)]:
            case [None, None]:
                default = None
            case [default, None]:
                pass
            case [None, default]:
                if self.use_units and s.substance_units is not None:
                    default *= self.units[s.substance_units]
            case _:
                raise ValueError(
                    f"both amount an concentration specified for Species {s.id}"
                )

        value = initial(default=default)
        self.simbio.add(s.id, value)

    def get_symbol(self, name: str, expected_type: type[T] = object) -> T:
        value = getattr(self.simbio, name)
        if not isinstance(value, expected_type):
            raise TypeError(f"unexpected type: {type(value)}")
        return value

    def get_species_reference(self, s: types.SimpleSpeciesReference) -> Species:
        # s.constant: bool
        species = self.get_symbol(s.species, Species)
        if isinstance(s, types.SpeciesReference) and s.stoichiometry is not None:
            return Species(species.variable, s.stoichiometry)
        else:
            return Species(species.variable)

    @add.register
    def add_reaction(self, r: types.Reaction):
        # r.compartment
        def yield_species(references: Sequence[types.SimpleSpeciesReference]):
            for r in references:
                s = self.species[r.species]
                if not (
                    s.boundary_condition or s.constant or s.id in self.assignment_rules
                ):
                    yield self.get_species_reference(r)

        reactants = list(yield_species(r.reactants))
        products = list(yield_species(r.products))
        modifiers = list(yield_species(r.modifiers))
        for m in modifiers:
            reactants.append(m)
            products.append(m)
        kinetic_law = r.kinetic_law
        formula: Symbol = kinetic_law.math
        if len(kinetic_law.parameters) > 0:
            mapping = {}
            for p in kinetic_law.parameters:
                new_id = f"{r.id}__{p.id}"
                self.add_parameter(replace(p, id=new_id))
                mapping[p.id] = MathMLSymbol(new_id)
            formula = substitute_by_name(formula, **mapping)
        formula = substitute(formula, GetAsVariable(self.get))

        self.simbio.add(
            r.id,
            RateLaw(reactants=reactants, products=products, rate_law=formula),
        )
        return

        # Reversible equations
        if not r.reversible:
            self.simbio.add(
                r.id,
                RateLaw(reactants=reactants, products=products, rate_law=formula),
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
                # Cannot split formula into forward and reverse
                self.simbio.add(
                    r.id,
                    RateLaw(reactants=reactants, products=products, rate_law=formula),
                )
                return

    @add.register
    def add_initial_assignment(self, a: types.InitialAssignment):
        component = self.get_symbol(a.symbol)
        value = substitute(a.math, GetAsVariable(self.get))
        if isinstance(component, Species):
            component.variable.initial = value
        elif isinstance(component, Constant | Parameter):
            component.default = value
        else:
            raise TypeError(
                f"cannot perform initial assignment for {a.symbol} of type {type(component)}"
            )

    @add.register
    def add_assignment_rule(self, r: types.AssignmentRule):
        component = self.get_symbol(r.variable, Parameter)
        value = substitute(r.math, GetAsVariable(self.get))
        component.default = value

    @add.register
    def add_rate_rule(self, r: types.RateRule):
        species = self.get_symbol(r.variable, Species)
        value: Symbol = substitute(r.math, GetAsVariable(self.get))
        eq = species.variable.derive() << value

        name = r.id
        if name is None or name == r.variable:
            name = f"{r.variable}__rate_rule"
        self.simbio.add(name, eq)

    @add.register
    def add_algebraic_rule(self, r: types.AlgebraicRule):
        raise NotImplementedError("algebraic rules are not yet supported")

    @add.register
    def add_event(self, r: types.Event):
        raise NotImplementedError("Event")

    @add.register
    def add_constaint(self, r: types.Constraint):
        raise NotImplementedError("Constraint")


class GetAsVariable:
    def __init__(self, getter):
        self.getter = getter

    def get(self, key, default=None):
        value = self.getter(key, default=None)
        if isinstance(value, Species):
            return value.variable
        else:
            return value
