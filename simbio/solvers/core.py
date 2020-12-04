from abc import ABC, abstractmethod
from numbers import Real
from typing import Tuple, Union

import numpy as np


class Solver(ABC):
    """API for all solvers.

    Same API as numbakit-ode solvers.
    """

    t: float
    y: np.ndarray
    t_bound: float = np.inf

    @abstractmethod
    def __init__(self, rhs, t, y, **kwargs):
        pass

    @abstractmethod
    def step(self, *, n: int = None, upto_t: float = None) -> Tuple[np.array, np.array]:
        """Advance simulation `n` steps or until the next timepoint will go beyond `upto_t`.

        It records and output all intermediate steps."""
        pass

    @abstractmethod
    def skip(self, *, n: int = None, upto_t: float = None) -> None:
        """Advance simulation `n` steps or until the next timepoint will go beyond `upto_t`.

        Unlike `step` or `run`, this method does not output the time and state."""

    @abstractmethod
    def run(self, t: Union[Real, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Integrates the ODE interpolating at each of the timepoints `t`."""


class NumpySolver(Solver):
    def __init__(self, rhs, t, y, **kwargs):
        self.rhs = rhs
        self.t = t
        self.y = y

    @abstractmethod
    def _step(self) -> None:
        """Perform one step.

        Saves result in self.t, self.y.
        """

    @abstractmethod
    def _interpolate(self, t: float) -> np.ndarray:
        """Interpolate solution at t."""

    def _check_time(self, t):
        if t > self.t_bound:
            raise ValueError(
                f"Time {t} is larger than solver bound time t_bound={self.t_bound}"
            )

    def skip(self, *, n: int = None, upto_t: float = None) -> None:
        if upto_t is not None:
            if upto_t > self.t_bound:
                raise ValueError(f"{upto_t=} is greater than {self.t_bound=}.")
            elif upto_t < self.t:
                return

        if n is None and upto_t is None:
            # No parameters, make one step.
            self._step()

        elif upto_t is None:
            # Only n is given, make n steps. If t_bound is reached, raise an exception.
            for i in range(n):
                self._step()
                if self.t > self.t_bound:
                    raise RuntimeError("Integrator reached t_bound.")

        elif n is None:
            # Only upto_t is given, move until that value.
            while self.t < upto_t:
                self._step()

        else:
            # Both parameters are given, move until either condition is reached.
            for i in range(n):
                self._step()
                if self.t > upto_t:
                    break

    def step(self, *, n: int = None, upto_t: float = None) -> Tuple[np.array, np.array]:
        if upto_t is not None:
            if upto_t > self.t_bound:
                raise ValueError(f"{upto_t=} is greater than {self.t_bound=}.")
            elif upto_t < self.t:
                return np.array(()), np.array(())

        if n is None and upto_t is None:
            # No parameters, make one step.
            self._step()
            return np.array((self.t,)), self.y

        elif upto_t is None:
            # Only n is given, make n steps. If t_bound is reached, raise an exception.
            ts, ys = np.empty(n), np.empty((n, self.y.size))
            for i in range(n):
                self._step()
                if self.t > self.t_bound:
                    raise RuntimeError("Integrator reached t_bound.")
                ts[i] = self.t
                ys[i] = self.y
            return ts, ys

        elif n is None:
            # Only upto_t is given, move until that value.
            ts, ys = [self.t], [self.y]
            while self.t < upto_t:
                self._step()
                ts.append(self.t)
                ys.append(self.y)
            return np.array(ts), np.array(ys)

        else:
            # Both parameters are given, move until either condition is reached.
            ts, ys = np.empty(n), np.empty((n, self.y.size))
            for i in range(n):
                self._step()
                if self.t > upto_t:
                    return ts[:i], ys[:i]
                ts[i] = self.t
                ys[i] = self.y
            return ts, ys

    def run(self, t: Union[Real, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        ts = np.array(t, copy=False, ndmin=1)
        ys = np.empty((ts.size, self.y.size))
        for i, ti in enumerate(ts):
            while self.t < ti:
                self.step()
            ys[i] = self._interpolate(ti)
        return ts, ys
