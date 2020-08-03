import numpy as np
from simbio.solvers.core import BaseSolver
from ward import fixture, raises, test


@fixture
def solver():
    class Solver(BaseSolver):
        def step(self):
            self.t += 1
            self.y = self.y + 1

        def interpolate(self, t):
            return t

    return Solver(t=0, y=np.array([0]), p=None, rhs=None)


@test("Must implement abstract methods")
def _():
    class GoodSolver(BaseSolver):
        def step(self):
            pass

        def interpolate(self, t):
            pass

    GoodSolver(t=None, y=None, p=None, rhs=None)

    class BadSolver(BaseSolver):
        pass

    with raises(TypeError):
        BadSolver(t=None, y=None, p=None, rhs=None)


@test("Move to")
def _(solver=solver):
    for t in (2, 3, 4.5):
        solver.move_to(t)
        assert solver.t == t
        assert solver.y == t

    with raises(ValueError):
        solver.move_to(3)


@test("Run free")
def _(solver=solver):
    t, y = solver.run(3)
    assert np.all(t == np.array([0, 1, 2, 3]))
    assert np.all(y == np.array([0, 1, 2, 3])[:, None])

    t, y = solver.run(6)
    assert np.all(t == np.array([3, 4, 5, 6]))
    assert np.all(y == np.array([3, 4, 5, 6])[:, None])

    with raises(ValueError):
        solver.run(3)


@test("Run array")
def _(solver=solver):
    t_in = np.array([0, 1, 2, 3])
    t, y = solver.run(t_in)
    assert np.all(t == t_in)
    assert np.all(y == t_in[:, None])

    t_in = np.array([4, 5, 6])
    t, y = solver.run(t_in)
    assert np.all(t == t_in)
    assert np.all(y == t_in[:, None])

    with raises(ValueError):
        solver.run(np.array([0, 1, 2, 3]))
