from __future__ import annotations

from abc import ABC, abstractmethod
from functools import cached_property
from typing import Dict, Tuple, Type, Union

import numpy as np
import pandas as pd
from orderedset import OrderedSet

from ..compartments import Compartment
from ..components import Component, Parameter, Species
from ..solvers.core import Solver
from ..solvers.scipy import ScipySolver


class Output:
    OUTPUTS = {}

    def __init_subclass__(cls, name) -> None:
        cls.OUTPUTS[name] = cls

    @staticmethod
    @abstractmethod
    def to_single_output(y, *, y_names):
        pass

    @staticmethod
    @abstractmethod
    def to_output(t, y, *, t_name="time", y_names):
        pass


class NumpyOutput(Output, name="numpy"):
    @staticmethod
    def to_single_output(y, *, y_names) -> np.ndarray:
        return y

    @staticmethod
    def to_output(t, y, *, t_name="time", y_names) -> Tuple[np.ndarray, np.ndarray]:
        return t, y


class PandasOutput(Output, name="pandas"):
    @staticmethod
    def to_single_output(y, *, y_names) -> pd.Series:
        y = pd.Series(y, index=y_names)
        return y

    @staticmethod
    def to_output(t, y, *, t_name="time", y_names) -> Tuple[pd.Series, pd.DataFrame]:
        t = pd.Series(t, name=t_name)
        y = pd.DataFrame(data=y, index=t, columns=y_names)
        return t, y


class Builder(ABC):
    BUILDERS = {}

    def __init__(self, model: Compartment) -> None:
        self.model = model

    def __init_subclass__(cls, alias) -> None:
        cls.BUILDERS[alias] = cls

    @abstractmethod
    def build_rhs(self, p):
        raise NotImplementedError

    @cached_property
    def reactions(self):
        return self.model.reactions

    @cached_property
    def species(self) -> OrderedSet[Species]:
        """Species participating in reactions."""
        out = OrderedSet()
        for reaction in self.reactions:
            out.update(reaction.species)
        return out

    @cached_property
    def parameters(self) -> OrderedSet[Parameter]:
        """Parameters participating in reactions."""
        out = OrderedSet()
        for reaction in self.reactions:
            out.update(reaction.parameters)
        return out

    def _resolve_values(
        self, values: dict[Union[str, Species, Parameter], float] = None
    ) -> tuple[dict, list]:
        out, unexpected = {}, []
        for name, value in values.items():
            if isinstance(name, str):
                try:
                    name = self.model[name]
                    out[name] = value
                except (KeyError, TypeError):
                    unexpected.append(name)
            elif isinstance(name, Component):
                if name not in self.model:
                    unexpected.append(name)
                else:
                    out[name] = value
            else:
                unexpected.append(name)
        return out, unexpected

    def build_value_vectors(
        self,
        values: dict[Union[str, Species, Parameter], float] = None,
        raise_on_unexpected: bool = True,
    ) -> tuple[np.ndarray, np.ndarray]:
        if values is None:
            values = {}
        else:
            values, unexpected = self._resolve_values(values)

            if raise_on_unexpected and unexpected:
                raise ValueError(
                    f"Received unexpected values not found in Compartment: {unexpected}"
                )

        species = self.species
        species = np.fromiter(
            (values.get(r, r.value) for r in species), dtype=float, count=len(species)
        )

        parameters = self.parameters
        parameters = np.fromiter(
            (values.get(r, r.value) for r in parameters),
            dtype=float,
            count=len(parameters),
        )
        return species, parameters


class Simulator:
    """Helper class to run a simulation.

    Simulator takes a Compartment as a model, and optional
    concentration and parameter values, overriding the model's defaults.
    """

    model: Compartment
    t0: float
    values: Dict[Union[str, Species, Parameter], float]
    solver_factory: Type[Solver]
    builder: Type[Builder]
    output: Type[Output]

    solver: Solver

    def __init__(
        self,
        model: Compartment,
        *,
        t0: float = 0,
        values: Dict[Union[str, Species, Parameter], float] = None,
        solver_factory: Type[Solver] = ScipySolver,
        builder: Union[str, Type[Builder]] = "numpy",
        output: Union[str, Type[Output]] = "pandas",
    ):
        self.model = model
        # TODO: Validate concentrations and parameters?
        self.values = values or {}
        self.t0 = t0
        self.solver_factory = solver_factory

        if isinstance(builder, str):
            builder = Builder.BUILDERS[builder]
        self.builder = builder(model)

        if isinstance(output, str):
            output = Output.OUTPUTS[output]
        self.output = output

    @cached_property
    def names(self) -> tuple[str, ...]:
        """Species names relative to the Compartment."""
        return tuple(map(self.model._relative_name, self.builder.species))

    def create_solver(
        self,
        *,
        t0: float = None,
        values: Dict[Union[str, Species, Parameter], float] = None,
    ) -> Solver:
        """Create a solver instance.

        Resolution order for values:
            - Input
            - Simulator defaults
            - Model defaults.
        """
        t = t0 or self.t0
        y, p = self.builder.build_value_vectors({**self.values, **(values or {})})
        rhs = self.builder.build_rhs(p)
        return self.solver_factory(rhs, t, y)

    def run(
        self,
        t: np.ndarray,
        *,
        t0: float = None,
        values: Dict[Union[str, Species, Parameter], float] = None,
        resume=False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Run simulation and return solution evaluated at t.

        If resume is False (default), create a new solver instance
        with given t0 and values.

        If resume is True, continue simulation from previous solver;
        t0 and values are ignored.
        """
        if not resume:
            self.solver = self.create_solver(t0=t0, values=values)

        t, y = self.solver.run(t)
        return self.output.to_output(t, y, t_name="time", y_names=self.names)
