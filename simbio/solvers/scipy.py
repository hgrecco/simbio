from contextlib import contextmanager
from functools import partial
from typing import Callable, Tuple, Type, Union

import numpy as np
from scipy.integrate._ivp import OdeSolver
from scipy.integrate._ivp.ivp import METHODS

from .core import BaseSolver


def _method(method: Union[str, Type[OdeSolver]]) -> Type[OdeSolver]:
    if isinstance(method, str):
        method = METHODS.get(method)

    if issubclass(method, OdeSolver):
        return method
    else:
        raise TypeError(
            f"Method must be a subclass of OdeSolver or one of the following strings: {METHODS}"
        )


class ScipySolver(BaseSolver):
    """Scipy solver.

    method : str or OdeSolver
    **kwargs are passed to OdeSolver.
    """

    def __init__(
        self,
        t: float,
        y: np.ndarray,
        p: np.ndarray,
        rhs: Callable,
        *,
        method="RK45",
        **kwargs,
    ) -> None:
        super().__init__(t=t, y=y, p=p, rhs=rhs)
        method = _method(method)
        rhs = partial(rhs, p=p)
        self._solver = method(rhs, t, y, t_bound=np.inf, **kwargs)

    def step(self):
        self._solver.step()
        self.t, self.y = self._solver.t, self._solver.y

    def interpolate(self, t):
        return self._solver.dense_output()(t)

    @contextmanager
    def _t_bound(self, t: float):
        """Context manager that sets OdeSolver.t_bound to t."""
        self._solver.t_bound = t
        yield
        self._solver.t_bound = np.inf
        self._solver.status = "running"

    def _move_to(self, t: float):
        with self._t_bound(t):
            super()._move_to(t)

    def _run_free(self, t: float) -> Tuple[np.ndarray, np.ndarray]:
        with self._t_bound(t):
            return super()._run_free(t)
