from abc import ABC, abstractmethod
from collections.abc import Collection
from numbers import Real
from typing import Callable, Tuple, Union

import numpy as np


class BaseSolver(ABC):
    """Base class for all solvers.

    Must implement step and interpolate methods.
    Can override private methods _move_to, _run_free, _run_array,
    with optimized implementations.
    """

    t: float
    y: np.ndarray
    p: np.ndarray
    rhs: Callable

    def __init__(self, t: float, y: np.ndarray, p: np.ndarray, rhs: Callable, **kwargs):
        self.t = t
        self.y = y
        self.p = p
        self.rhs = rhs

    @abstractmethod
    def step(self):
        """Advance simulation one time step.

        Saves the result in self.t, self.y
        """
        raise NotImplementedError

    @abstractmethod
    def interpolate(self, t):
        """Interpolate solution at t."""
        raise NotImplementedError

    def _check_time(self, t):
        if t < self.t:
            raise ValueError(
                f"Time {t=} is smaller than current solver time t={self.t}"
            )

    def run(self, t: Union[Real, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """Run solver.

        If t is a scalar, run freely up to t.
        If t is an array-like, return solution evaluated at t.
        """
        if isinstance(t, Real):
            self._check_time(t)
            return self._run_free(t)
        elif isinstance(t, Collection):
            t = np.asarray(t)
            self._check_time(t[0])
            return self._run_array(t)

    def move_to(self, t: float):
        """Advance simulation upto t.

        Saves the result in self.t, self.y
        """
        self._check_time(t)
        self._move_to(t)

    def _move_to(self, t: float):
        """Move solver to time t.

        If input t is current solver time, do nothing.
        """
        while self.t < t:
            self.step()

        # If we overstepped, go back.
        if self.t > t:
            self.y = self.interpolate(t)
            self.t = t

    def _run_free(self, t: float) -> Tuple[np.ndarray, np.ndarray]:
        """Run freely upto t and return (t, y) as arrays."""
        t_out, y_out = [], []

        while self.t < t:
            t_out.append(self.t)
            y_out.append(self.y)
            self.step()

        # If we overstepped, go back.
        if self.t > t:
            self.y = self.interpolate(t)
            self.t = t

        # Save last point
        t_out.append(self.t)
        y_out.append(self.y)

        return np.array(t_out), np.array(y_out)

    def _run_array(self, t: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Run upto t, evualuating y at given t and return (t, y) as arrays."""
        y0 = self.y
        y = np.empty((t.size, y0.size))

        for i, ti in enumerate(t):
            self._move_to(ti)
            y[i] = self.y

        return t, y
