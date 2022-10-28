from __future__ import annotations

from numbers import Real
from typing import Type, Union

import numpy as np
from scipy.integrate import odeint
from scipy.integrate._ivp import OdeSolver
from scipy.integrate._ivp.ivp import METHODS

from .core import NumpySolver, Solver


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
        self,
        rhs,
        t,
        y,
        *,
        method: Union[str, Type[OdeSolver]] = "RK45",
        **kwargs,
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


class ODEint(Solver):
    def __init__(self, rhs, t, y, *, atol=None, rtol=None):
        self.rhs = rhs
        self.t = t
        self.y = y
        self.atol = atol
        self.rtol = rtol

    def run(self, t: Union[Real, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        if t[0] < self.t:
            raise ValueError(
                f"t[0]={t[0]} is less than solvers current time self.t={self.t}."
            )

        elif t[0] > self.t:
            # The first value for t must coincide with the initial condition for y.
            t = np.append(self.t, t)

        y = odeint(self.rhs, self.y, t, rtol=self.rtol, atol=self.atol, tfirst=True)
        self.t, self.y = t[-1], y[-1]
        return t, y

    def step(self, *, n: int = None, upto_t: float = None) -> tuple[np.array, np.array]:
        raise NotImplementedError

    def skip(self, *, n: int = None, upto_t: float = None) -> None:
        if n is not None:
            raise NotImplementedError("Method is not implemented when `n` is not None.")

        y = odeint(
            self.rhs,
            self.y,
            (self.t, upto_t),
            rtol=self.rtol,
            atol=self.atol,
            tfirst=True,
        )
        self.t, self.y = upto_t, y
