from __future__ import annotations

import numpy as np
import pandas as pd

from ..compilers.core import Compiler
from ..compilers.numpy import NumpyCompiler
from ..components.types import Compartment, Parameter, Species
from .solvers.core import Solver
from .solvers.scipy import ODEint


class Simulator:
    """Helper class to run a simulation.

    Simulator takes a Compartment as a model, and optional
    concentration and parameter values, overriding the model's defaults.
    """

    model: Compartment
    t0: float
    values: dict[str | Species | Parameter, float]
    solver: type[Solver]
    solver_kwargs: dict
    compiler: type[Compiler]

    current_solver: Solver

    def __init__(
        self,
        model: Compartment,
        *,
        t0: float = 0,
        values: dict[str | Species | Parameter, float] = {},
        solver: type[Solver] = ODEint,
        solver_kwargs: dict = {},
        compiler: type[Compiler] = NumpyCompiler,
    ):
        self.model = model
        # TODO: Validate concentrations and parameters?
        self.values = values
        self.t0 = t0
        self.solver = solver
        self.solver_kwargs = solver_kwargs
        self.compiler = compiler(model)

    def create_solver(
        self,
        *,
        t0: float = None,
        values: dict[str | Species | Parameter, float] = {},
        **solver_kwargs,
    ) -> Solver:
        """Create a solver instance.

        Resolution order for values:
            - Input
            - Simulator defaults
            - Model defaults.
        """
        if t0 is None:
            t0 = self.t0
        y0, p = self.compiler.build_value_vectors({**self.values, **values})
        rhs = self.compiler.build_rhs(p.values)
        return self.solver(
            rhs,
            t0,
            y0.values,
            **{**self.solver_kwargs, **solver_kwargs},
        )

    def run(
        self,
        t: np.ndarray,
        *,
        t0: float = None,
        values: dict[str | Species | Parameter, float] = {},
        resume=False,
    ) -> pd.DataFrame:
        """Run simulation and return solution evaluated at t.

        If resume is False (default), create a new solver instance
        with given t0 and values.

        If resume is True, continue simulation from previous solver;
        t0 and values are ignored.
        """
        if not resume:
            self.current_solver = self.create_solver(t0=t0, values=values)

        t, y = self.current_solver.run(t)
        return self.to_dataframe(t, y)

    def to_dataframe(self, t, y):
        return pd.DataFrame(
            data=y,
            index=pd.Series(t, name="time"),
            columns=self.compiler.species.index,
        )
