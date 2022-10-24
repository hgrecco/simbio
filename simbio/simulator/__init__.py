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
        values: dict[str | Species | Parameter, float] = None,
        solver: type[Solver] = ODEint,
        solver_kwargs: dict | None = None,
        compiler: type[Compiler] = NumpyCompiler,
    ):
        self.model = model
        # TODO: Validate concentrations and parameters?
        self.values = values or {}
        self.t0 = t0
        self.solver = solver
        self.solver_kwargs = solver_kwargs or {}
        self.compiler = compiler(model)

    def create_solver(
        self,
        *,
        t0: float = None,
        values: dict[str | Species | Parameter, float] = None,
        **kwargs,
    ) -> Solver:
        """Create a solver instance.

        Resolution order for values:
            - Input
            - Simulator defaults
            - Model defaults.
        """
        t = t0 or self.t0
        y, p = self.compiler.build_value_vectors({**self.values, **(values or {})})
        rhs = self.compiler.build_rhs(p)
        return self.solver(rhs, t, y, **{**self.solver_kwargs, **kwargs})

    def run(
        self,
        t: np.ndarray,
        *,
        t0: float = None,
        values: dict[str | Species | Parameter, float] = None,
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
        return pd.DataFrame(
            data=y,
            index=pd.Series(t, name="time"),
            columns=self.compiler.species.index,
        )
