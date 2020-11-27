import numpy as np
from simbio.simulator.solvers.core import NumpySolver
from ward import fixture, raises, test


@fixture
def solver():
    class Solver(NumpySolver):
        def _step(self):
            self.t += 1
            self.y = self.y + 1

        def _interpolate(self, t):
            return t

    return Solver(rhs=None, t=0, y=np.array([0]))


@test("Must implement abstract methods")
def _():
    class GoodSolver(NumpySolver):
        def _step(self):
            pass

        def _interpolate(self, t):
            pass

    GoodSolver(rhs=None, t=None, y=None)

    class BadSolver(NumpySolver):
        pass

    with raises(TypeError):
        BadSolver(rhs=None, t=None, y=None)


@test("Skip")
def _(solver=solver):
    for t in (2, 3, 4.5):
        solver.skip(upto_t=t)
        assert solver.t == np.ceil(t)
        assert solver.y == np.ceil(t)


@test("Step")
def _(solver=solver):
    t, y = solver.step(upto_t=3)
    assert np.all(t == np.array([0, 1, 2, 3]))
    assert np.all(y == np.array([0, 1, 2, 3])[:, None])

    t, y = solver.step(upto_t=6)
    assert np.all(t == np.array([3, 4, 5, 6]))
    assert np.all(y == np.array([3, 4, 5, 6])[:, None])


@test("Run")
def _(solver=solver):
    t_in = np.array([0, 1, 2, 3])
    t, y = solver.run(t_in)
    assert np.all(t == t_in)
    assert np.all(y == t_in[:, None])

    t_in = np.array([4, 5, 6])
    t, y = solver.run(t_in)
    assert np.all(t == t_in)
    assert np.all(y == t_in[:, None])
