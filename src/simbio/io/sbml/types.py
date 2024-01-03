from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import NewType, Sequence

ID = NewType("ID", str)  # Identifier.
SBOTerm = NewType("SBOTerm", str)  # a 7-digit number, such as SBO:0000014


def is_valid_id(id: str) -> bool:
    """(alphanumeric | "_"), starting without a number."""
    raise NotImplementedError


@dataclass(kw_only=True)
class Math:
    pass


@dataclass(kw_only=True)
class Base:
    id: ID | None = None
    name: str | None = None
    meta_id: ID | None = None
    sbo_term: SBOTerm | None = None
    notes: str | None = None
    annotation: str | None = None


@dataclass(kw_only=True)
class Model(Base):
    substance_units: ID | None = None
    time_units: ID | None = None
    volume_units: ID | None = None
    area_units: ID | None = None
    length_units: ID | None = None
    extent_units: ID | None = None
    conversion_factor: ID | None = None
    functions: Sequence[FunctionDefinition] = ()
    units: Sequence[UnitDefinition] = ()
    compartments: Sequence[Compartment] = ()
    species: Sequence[Species] = ()
    parameters: Sequence[Parameter] = ()
    initial_assignments: Sequence[InitialAssignment] = ()
    rules: Sequence[Rule] = ()
    constraints: Sequence[Constraint] = ()
    reactions: Sequence[Reaction] = ()
    events: Sequence[Event] = ()


@dataclass(kw_only=True)
class FunctionDefinition(Base):
    id: ID
    math: Math


@dataclass(kw_only=True)
class Compartment(Base):
    id: ID
    spatial_dimensions: float | None = None
    size: float | None = None
    units: ID | None = None
    constant: bool


@dataclass(kw_only=True)
class Species(Base):
    id: ID
    compartment: ID
    initial_amount: float | None = None
    initial_concentration: float | None = None
    substance_units: ID | None = None
    has_only_substance_units: bool
    boundary_condition: bool
    constant: bool
    conversion_factor: ID | None = None


@dataclass(kw_only=True)
class Parameter(Base):
    id: ID
    value: float | None = None
    units: ID | None = None
    constant: bool


@dataclass(kw_only=True)
class LocalParameter(Base):
    id: ID
    value: float | None = None
    units: ID | None = None


@dataclass(kw_only=True)
class InitialAssignment(Base):
    "Mathematical expression used to determine the initial conditions of a model."

    symbol: ID
    math: Math


@dataclass(kw_only=True)
class Rule(Base):
    """A mathematical expression added to the set of equations."""

    math: Math


@dataclass(kw_only=True)
class AlgebraicRule(Rule):
    pass


@dataclass(kw_only=True)
class AssignmentRule(Rule):
    variable: ID


@dataclass(kw_only=True)
class RateRule(Rule):
    variable: ID


@dataclass(kw_only=True)
class Constraint(Base):
    """Defined by an arbitrary mathematical expression computing
    a True / False value from model symbols."""

    math: Math
    message: str


@dataclass(kw_only=True)
class Reaction(Base):
    id: ID
    reversible: bool
    compartment: ID | None = None
    reactants: Sequence[SpeciesReference]
    products: Sequence[SpeciesReference]
    modifiers: list[ModifierSpeciesReference]
    kinetic_law: KineticLaw


@dataclass(kw_only=True)
class SimpleSpeciesReference(Base):
    species: ID


class ModifierSpeciesReference(SimpleSpeciesReference):
    pass


@dataclass(kw_only=True)
class SpeciesReference(SimpleSpeciesReference):
    stoichiometry: float | None = None
    constant: bool


@dataclass(kw_only=True)
class KineticLaw(Base):
    math: Math
    parameters: Sequence[Parameter]


@dataclass(kw_only=True)
class Event(Base):
    """Instantaneous, discontinuous change in one or more symbols of any type."""

    use_values_from_trigger_time: bool
    trigger: Trigger
    prority: Priority
    delay: Delay
    assignments: Sequence[EventAssignment]


@dataclass(kw_only=True)
class Trigger(Base):
    initial_value: bool
    persistent: bool
    math: Math


@dataclass(kw_only=True)
class Priority(Base):
    math: Math


@dataclass(kw_only=True)
class Delay(Base):
    math: Math


@dataclass(kw_only=True)
class EventAssignment(Base):
    math: Math


@dataclass(kw_only=True)
class UnitDefinition(Base):
    id: ID
    units: Sequence[Unit]

    def __post_init__(self):
        try:
            UnitKind[self.id]
        except KeyError:
            pass
        else:
            raise ValueError(f"{self.id} is the id of a base unit")


@dataclass(kw_only=True)
class Unit:
    """
    (multiplier * 10**scale * kind) ** exponent
    """

    kind: UnitKind
    exponent: float
    scale: int
    multiplier: float


class UnitKind(Enum):
    ampere = auto()
    coulomb = auto()
    gray = auto()
    joule = auto()
    litre = auto()
    mole = auto()
    radian = auto()
    steradian = auto()
    weber = auto()
    avogadro = auto()
    dimensionless = auto()
    henry = auto()
    katal = auto()
    lumen = auto()
    newton = auto()
    second = auto()
    tesla = auto()
    becquerel = auto()
    farad = auto()
    hertz = auto()
    kelvin = auto()
    lux = auto()
    ohm = auto()
    siemens = auto()
    volt = auto()
    candela = auto()
    gram = auto()
    item = auto()
    kilogram = auto()
    metre = auto()
    pascal = auto()
    sievert = auto()
    watt = auto()
