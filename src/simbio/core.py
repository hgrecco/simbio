from __future__ import annotations

import inspect
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Iterator, Mapping, Sequence

import numpy as np
import pandas as pd
from numpy.typing import ArrayLike
from poincare import Constant, Parameter, Variable
from poincare._node import Node, NodeMapper, T, _ClassInfo
from poincare._utils import class_and_instance_method
from poincare.simulator import Backend, Components
from poincare.simulator import Simulator as _Simulator
from poincare.types import Equation, EquationGroup, Initial, System, assign
from symbolite import Scalar, Symbol
from symbolite.abstract import symbol
from symbolite.core import substitute
from typing_extensions import Self, dataclass_transform

if TYPE_CHECKING:
    import ipywidgets


def initial(*, default: Initial | None = None, init: bool = True) -> Species:
    """Creates an Species with a default initial condition."""
    return Species(variable=default)


@dataclass_transform(kw_only_default=True, field_specifiers=(initial, assign))
class Compartment(System, abstract=True):
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        signature: inspect.Signature = cls.__signature__
        parameters = dict(signature.parameters)
        for k in cls._annotations.keys():
            v = getattr(cls, k)
            if isinstance(v, Species):
                default = v.variable.initial
                if default is None:
                    cls._required.add(k)
                    default = inspect.Parameter.empty
                parameters[k] = parameters[k].replace(default=default)
        cls.__signature__ = signature.replace(parameters=parameters.values())

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
        variable: Variable | Initial,
        stoichiometry: float = 1,
    ):
        if not isinstance(variable, Variable):
            variable = Variable(initial=variable)
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
                        int(st2)
                        | float(st2),
                        Species(variable=var, stoichiometry=st),
                    )
                    | (
                        Species(variable=var, stoichiometry=st),
                        int(st2)
                        | float(st2),
                    ),
                )
            ):
                return Species(var, st * st2)

            case _:
                raise TypeError


@dataclass
class RateLaw(EquationGroup):
    """A RateLaw reaction contains a set of equations transforming
    reactants into products with a given rate law.

    Given:
        - `x, y: Species`
        - `k: float`

    Then:
        `Reaction(reactants=[2 * x], products=[y], rate_law=k)`

    will contain two equations:
        - `dx/dt = -2 * k`
        - `dy/dt = +k`
    """

    def __init__(
        self,
        *,
        reactants: Sequence[Species],
        products: Sequence[Species],
        rate_law: float | Symbol,
    ):
        self.reactants = tuple(map(Species.from_mul, reactants))
        self.products = tuple(map(Species.from_mul, products))
        self.rate_law = substitute(rate_law, _SpeciesToVariable)
        self.equations = tuple(self._yield_equations())

    def _copy_from(self, parent: System):
        mapper = NodeMapper(parent)
        return self.__class__(
            reactants=[substitute(v, mapper) for v in self.reactants],
            products=[substitute(v, mapper) for v in self.products],
            rate_law=substitute(substitute(self.rate_law, mapper), _SpeciesToVariable),
        )

    def _yield_equations(self) -> Iterator[Equation]:
        species_stoich: dict[Variable, float] = defaultdict(float)
        for r in self.reactants:
            species_stoich[r.variable] -= r.stoichiometry
        for p in self.products:
            species_stoich[p.variable] += p.stoichiometry

        for s, st in species_stoich.items():
            yield s.derive() << st * self.rate_law


class MassAction(RateLaw):
    """A MassAction reaction contains a set of equations transforming
    reactants into products with a given rate.
    The reaction's rate law is the product of the rate
    and the reactants raised to their stoichiometric coefficient.

    Given:
        - `x, y: Species`
        - `k: float`

    Then:
        `Reaction(reactants=[2 * x], products=[y], rate_law=k)`

    will contain two equations:
        - `dx/dt = -2 * k * x**2`
        - `dy/dt = +k * x**2`
    """

    def __init__(
        self,
        *,
        reactants: Sequence[Species],
        products: Sequence[Species],
        rate: float | Symbol,
    ):
        self.reactants = tuple(map(Species.from_mul, reactants))
        self.products = tuple(map(Species.from_mul, products))
        self.rate = substitute(rate, _SpeciesToVariable)
        self.equations = tuple(self._yield_equations())

    @property
    def rate_law(self):
        rate = self.rate
        for r in self.reactants:
            rate *= r.variable**r.stoichiometry
        return rate

    def _copy_from(self, parent: System):
        mapper = NodeMapper(parent)
        return self.__class__(
            reactants=[substitute(v, mapper) for v in self.reactants],
            products=[substitute(v, mapper) for v in self.products],
            rate=substitute(substitute(self.rate, mapper), _SpeciesToVariable),
        )


def _species_to_variable(x):
    if isinstance(x, Species):
        return x.variable
    else:
        return x


class _SpeciesToVariable(dict):
    def get(self, key, default=None):
        return _species_to_variable(key)


class Simulator(_Simulator):
    def __init__(
        self,
        system: Compartment | type[Compartment],
        /,
        *,
        backend: Backend = "numpy",
        transform: Sequence[Symbol] | Mapping[str, Symbol] | None = None,
    ):
        if isinstance(transform, Sequence):
            transform = [substitute(v, _SpeciesToVariable()) for v in transform]
        elif isinstance(transform, Mapping):
            transform = {
                k: substitute(v, _SpeciesToVariable()) for k, v in transform.items()
            }
        super().__init__(system, backend=backend, transform=transform)

    def create_problem(
        self,
        values: dict[Constant | Parameter | Species, Initial | Symbol] = {},
        *,
        t_span: tuple[float, float] = (0, np.inf),
    ):
        return super().create_problem(
            {_species_to_variable(k): v for k, v in values.items()},
            t_span=t_span,
        )

    def interact(
        self,
        values: Mapping[Components, tuple[float, ...] | ipywidgets.Widget]
        | Sequence[Components] = {},
        *,
        t_span: tuple[float, float] = (0, np.inf),
        save_at: ArrayLike,
        func: Callable[[pd.DataFrame], Any] = lambda df: df.plot(),
    ):
        if isinstance(values, Sequence):
            values = [_species_to_variable(v) for v in values]
        elif isinstance(values, Mapping):
            values = {k: _species_to_variable(v) for k, v in values.items()}

        return super().interact(values, t_span=t_span, save_at=save_at, func=func)
