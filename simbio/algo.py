from __future__ import annotations

from typing import Tuple, Union

import numpy as np

from .parameters import BaseParameter, Parameter, Species
from .simulator import Simulator
from .solvers.core import BaseSolver


def _find_steady_state(
    solver: BaseSolver, *, atol=1e-4, rtol=1e-4, max_iter=1000
) -> Tuple[float, np.ndarray]:
    for _ in range(max_iter):
        dy = np.abs(solver.rhs(solver.t, solver.y, solver.p))
        y = np.abs(solver.y)

        adiff = dy.max()
        cond = y > atol
        rdiff = (dy[cond] / y[cond]).max()

        if (adiff < atol) and (rdiff < rtol):
            return solver.t, solver.y
        else:
            solver.step()
    else:
        raise Exception(
            f"Maximum iterations ({max_iter}) reached at time {solver.t:.3f}."
        )


def find_steady_state(simulator: Simulator, **kwargs):
    t, y = _find_steady_state(simulator.create_solver(), **kwargs)
    return t, simulator._to_single_output(y, y_names=simulator.names)


def _dose_response(
    simulator: Simulator, name: Union[str, Species, Parameter], values, **kwargs
):
    values = np.asarray(values)
    response = []
    for solver in Scanner.from_single_value(simulator, name, values):
        _, y = _find_steady_state(solver, **kwargs)
        response.append(y)

    return values, np.asarray(response)


def dose_response(simulator, name: Union[str, Species, Parameter], values, **kwargs):
    return simulator._to_output(
        *_dose_response(simulator, name, values, **kwargs),
        t_name="dose",
        y_names=simulator.names,
    )


class Scanner:
    def __init__(self, simulator, scan_values):
        self.simulator = simulator
        self.scan_values = scan_values

    @classmethod
    def from_single_value(cls, simulator, name, values):
        if isinstance(name, str):
            name = simulator.model[name]
        elif not isinstance(name, BaseParameter):
            raise ValueError(f"{name.name} is neither a Species nor a Parameter.")

        return cls(simulator, ({name: value} for value in values))

    @classmethod
    def from_lhs(cls):
        # TODO:
        pass

    def __iter__(self):
        for scan_value in self.scan_values:
            yield self.simulator.create_solver(values=scan_value)
