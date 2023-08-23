from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Iterator, Self, Sequence, dataclass_transform

import numpy as np
from poincare import Constant, Parameter, Variable
from poincare._node import Node, NodeMapper, T, _ClassInfo
from poincare._utils import class_and_instance_method
from poincare.simulator import Simulator as _Simulator
from poincare.types import Equation, EquationGroup, Initial, System, assign
from symbolite import Scalar, Symbol
from symbolite.abstract import symbol
from symbolite.core import substitute


def initial(*, default: Initial | None = None, init: bool = True) -> Species:
    variable = Variable(initial=default)
    return Species(variable)


@dataclass_transform(kw_only_default=True, field_specifiers=(initial, assign))
class Compartment(System):
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        for k in cls._annotations.keys():
            v = getattr(cls, k)
            if isinstance(v, Species) and v.variable.initial is None:
                cls._required.add(k)

    @class_and_instance_method
    def _yield(
        self,
        type: type[T],
        /,
        *,
        exclude: _ClassInfo = (),
        recursive: bool = True,
    ) -> Iterator[T]:
        if issubclass(Variable, type) and not issubclass(Variable, exclude):
            it = super()._yield(type | Species, exclude=exclude, recursive=recursive)
            if not issubclass(Species, type):
                for v in it:
                    if isinstance(v, Species):
                        yield v.variable
                    else:
                        yield v
            else:
                for v in it:
                    yield v
                    if isinstance(v, Species):
                        yield v.variable
        else:
            yield from super()._yield(type, exclude=exclude, recursive=recursive)


class Species(Node, Scalar):
    def __init__(
        self,
        variable: Variable,
        stoichiometry: float = 1,
    ):
        self.variable = variable
        self.stoichiometry = stoichiometry

    def __set_name__(self, cls: Node, name: str):
        return self.variable.__set_name__(cls, name)

    @property
    def name(self):
        return self.variable.name

    @property
    def parent(self):
        return self.variable.parent

    def _copy_from(self, parent: Node) -> Self:
        variable = self.variable._copy_from(parent)
        return Species(variable, self.stoichiometry)

    def __get__(self, parent, cls):
        if parent is None:
            return self

        species = super().__get__(parent, cls)
        return Species(species.variable, self.stoichiometry * species.stoichiometry)

    def __set__(self, obj, value: Initial | Species):
        if isinstance(value, Initial):
            species = initial(default=value)
        else:
            try:
                species = Species.from_mul(value)
            except TypeError:
                raise TypeError(f"unexpected type {type(value)} for {self.name}")
            else:
                species.stoichiometry *= self.stoichiometry

        super().__set__(obj, species)

    def __repr__(self):
        return f"{self.stoichiometry} * {self.variable}"

    def __str__(self):
        return str(self.variable)

    def __hash__(self):
        return hash((self.variable, self.stoichiometry))

    def __eq__(self, other: Self):
        if other.__class__ is not self.__class__:
            return NotImplemented
        return (self.variable, self.stoichiometry) == (
            other.variable,
            other.stoichiometry,
        )

    @classmethod
    def from_mul(cls, expr: Symbol):
        match expr:
            case Species(variable=var, stoichiometry=st):
                return Species(var, st)

            case Symbol(
                expression=symbol.Expression(
                    func=symbol.mul,
                    args=(
                        int(st2) | float(st2),
                        Species(variable=var, stoichiometry=st),
                    )
                    | (
                        Species(variable=var, stoichiometry=st),
                        int(st2) | float(st2),
                    ),
                )
            ):
                return Species(var, st * st2)

            case _:
                raise TypeError


@dataclass
class Reaction(EquationGroup):
    def __init__(
        self,
        *,
        reactants: Sequence[Species],
        products: Sequence[Species],
        rate_law: Callable | float | Symbol,
    ):
        self.reactants = tuple(map(Species.from_mul, reactants))
        self.products = tuple(map(Species.from_mul, products))
        self.rate_law = rate_law
        self.equations = tuple(self.yield_equations())

    def _copy_from(self, parent: System):
        mapper = NodeMapper(parent)
        return self.__class__(
            reactants=[substitute(v, mapper) for v in self.reactants],
            products=[substitute(v, mapper) for v in self.products],
            rate_law=substitute(self.rate_law, mapper),
        )

    def yield_equations(self) -> Iterator[Equation]:
        if callable(self.rate_law):
            rate = self.rate_law(*self.reactants)
        else:
            rate = self.rate_law
        species_stoich: dict[Variable, float] = defaultdict(float)
        for r in self.reactants:
            species_stoich[r.variable] -= r.stoichiometry
        for p in self.products:
            species_stoich[p.variable] += p.stoichiometry

        for s, st in species_stoich.items():
            yield s.derive() << st * rate


class MassAction(Reaction):
    def __init__(
        self,
        *,
        reactants: Sequence[Species],
        products: Sequence[Species],
        rate: float | Symbol,
    ):
        self.reactants = tuple(map(Species.from_mul, reactants))
        self.products = tuple(map(Species.from_mul, products))
        self.rate = rate
        self.equations = tuple(self.yield_equations())

    def rate_law(self, *reactants: Species):
        rate = self.rate
        for r in reactants:
            rate *= r.variable**r.stoichiometry
        return rate

    def _copy_from(self, parent: System):
        mapper = NodeMapper(parent)
        return self.__class__(
            reactants=[substitute(v, mapper) for v in self.reactants],
            products=[substitute(v, mapper) for v in self.products],
            rate=substitute(self.rate, mapper),
        )


def species_to_variable(x):
    if isinstance(x, Species):
        return x.variable
    else:
        return x


class Simulator(_Simulator):
    def create_problem(
        self,
        values: dict[Constant | Parameter | Species, Initial | Symbol] = {},
        *,
        t_span: tuple[float, float] = (0, np.inf),
    ):
        return super().create_problem(
            {species_to_variable(k): v for k, v in values.items()},
            t_span=t_span,
        )
