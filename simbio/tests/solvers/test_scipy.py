import numpy as np
from simbio.solvers.scipy import ScipySolver
from ward import fixture, test


@fixture
def solver():
    def func(t, y, p):
        return -y

    return ScipySolver(t=0, y=np.array([1]), p=None, rhs=func, atol=1e-8, rtol=1e-8)


@test("Step")
def _(solver=solver):
    for _ in range(10):
        solver.step()
        assert np.allclose(solver.y, np.exp(-solver.t), rtol=1e-8, atol=1e-8)


@test("Move to")
def _(solver=solver):
    for t in range(10):
        solver.move_to(t)
        assert np.allclose(solver.y, np.exp(-t), rtol=1e-8, atol=1e-8)


@test("Run free")
def _(solver=solver):
    t, y = solver.run(1)
    assert np.allclose(y, np.exp(-t[:, None]), rtol=1e-8, atol=1e-8)


@test("Run array")
def _(solver=solver):
    t_in = np.linspace(0, 1, 10)
    t, y = solver.run(t_in)
    assert np.allclose(t, t_in)
    assert np.allclose(y, np.exp(-t[:, None]), rtol=1e-8, atol=1e-8)
