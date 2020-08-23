from __future__ import annotations

from typing import Dict, Iterable, Tuple, Type, Union

import numpy as np
import pandas as pd

from .compartments import Compartment
from .parameters import Parameter
from .solvers.core import BaseSolver
from .solvers.scipy import ScipySolver
from .species import Species


class Simulator:
    """Helper class to run a simulation.

    Simulator takes a Compartment as a model, and optional
    concentration and parameter values, overriding the model's defaults.
    """

    model: Compartment
    t0: float
    values: Dict[Union[str, Species, Parameter], float]
    solver_factory: Type[BaseSolver]
    solver: BaseSolver

    def __init__(
        self,
        model: Compartment,
        *,
        t0: float = 0,
        values: Dict[Union[str, Species, Parameter], float] = None,
        solver_factory: BaseSolver = ScipySolver,
    ):
        self.model = model
        # TODO: Validate concentrations and parameters?
        self.values = values or {}
        self.t0 = t0
        self.solver_factory = solver_factory

    @property
    def names(self) -> Tuple[str, ...]:
        """Return species names."""
        return self.model._in_reaction_species_names

    def _initial_parameters(
        self, values: Dict[Union[str, Species, Parameter], float] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Build concentration and parameter vector.

        Resolution order:
            - Input
            - Simulator defaults
            - Model defaults.
        """
        if values is None:
            values = {}
        y, p = self.model._build_value_vectors({**self.values, **values})
        return y, p

    def create_solver(self, *, t0=None, values=None) -> BaseSolver:
        """Create a solver instance.

        Resolution order:
            - Input
            - Simulator defaults
            - Model defaults.
        """
        t = t0 or self.t0
        y, p = self._initial_parameters(values)
        rhs = self.model._build_ip_rhs()
        return self.solver_factory(t=t, y=y, p=p, rhs=rhs,)

    @staticmethod
    def _to_single_output(y, *, y_names) -> np.ndarray:
        return y

    @staticmethod
    def _to_output(t, y, *, t_name="time", y_names) -> Tuple[np.ndarray, np.ndarray]:
        return t, y

    def run(
        self,
        time: Union[float, Iterable],
        *,
        t0: float = None,
        values: Dict[Union[str, Species, Parameter], float] = None,
        resume=False,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Run simulation.

        If t is a scalar, run freely up to t.
        If t is an array-like, return solution evaluated at t.

        If resume is False (default), create a new solver instance
        with given t0, values.
        Resolution order:
        - Input
            - Simulator defaults
            - Model defaults.

        If resume is True, continue simulation from previous solver.
            t0, concentrations and parameters are ignored.
        """
        if not resume:
            self.solver = self.create_solver(t0=t0, values=values)

        t, y = self.solver.run(time)
        return self._to_output(t, y, t_name="time", y_names=self.names)


class PandasSimulator(Simulator):
    @staticmethod
    def _to_single_output(y, *, y_names) -> pd.Series:
        y = pd.Series(y, index=y_names)
        return y

    @staticmethod
    def _to_output(t, y, *, t_name="time", y_names) -> Tuple[pd.Series, pd.DataFrame]:
        t = pd.Series(t, name=t_name)
        y = pd.DataFrame(data=y, index=t, columns=y_names)
        return t, y
