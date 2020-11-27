from typing import Type, Union

import numpy as np
from scipy.integrate._ivp import OdeSolver
from scipy.integrate._ivp.ivp import METHODS

from .core import NumpySolver


def _method(method: Union[str, Type[OdeSolver]]) -> Type[OdeSolver]:
    if isinstance(method, str):
        method = METHODS.get(method)

    if issubclass(method, OdeSolver):
        return method
    else:
        raise TypeError(
            f"Method must be a subclass of OdeSolver or one of the following strings: {METHODS}"
        )


class ScipySolver(NumpySolver):
    """Scipy solver.

    method : str or OdeSolver
    **kwargs are passed to OdeSolver.
    """

    def __init__(
        self, rhs, t, y, *, method: Union[str, Type[OdeSolver]] = "RK45", **kwargs,
    ):
        super().__init__(rhs=rhs, t=t, y=y)
        method = _method(method)
        self._solver = method(rhs, t, y, t_bound=np.inf, **kwargs)

    def _step(self):
        self._solver.step()
        self.t, self.y = self._solver.t, self._solver.y

    def _interpolate(self, t):
        if t == self.t:
            return self.y
        return self._solver.dense_output()(t)
