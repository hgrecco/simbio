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
from symbolite import Symbol
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


@dataclass(frozen=True)
class Species(Node):
    variable: Variable
    stoichiometry: float = 1

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
        elif isinstance(value, Species):
            species = Species(value.variable, self.stoichiometry * value.stoichiometry)
        else:
            raise TypeError(f"unexpected type {type(value)} for {self.name}")

        super().__set__(obj, species)

    def __str__(self):
        return str(self.variable)

    def __mul__(self, other: float) -> Self:
        if not isinstance(other, int | float):
            raise TypeError

        return Species(self.variable, self.stoichiometry * other)

    def __rmul__(self, other: float):
        return self.__mul__(other)


@dataclass
class Reaction(EquationGroup):
    def __init__(
        self,
        *,
        reactants: Sequence[Species],
        products: Sequence[Species],
        rate_law: Callable | float | Symbol,
    ):
        self.reactants = reactants
        self.products = products
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
        self.reactants = reactants
        self.products = products
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
