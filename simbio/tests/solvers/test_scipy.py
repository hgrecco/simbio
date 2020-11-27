import numpy as np
from simbio.simulator.solvers.scipy import ScipySolver
from ward import fixture, test


@fixture
def solver():
    def func(t, y):
        return -y

    return ScipySolver(rhs=func, t=0, y=np.array([1]), atol=1e-8, rtol=1e-8)


@test("Skip")
def _(solver=solver):
    for _ in range(10):
        solver.skip()
        assert np.allclose(solver.y, np.exp(-solver.t), rtol=1e-8, atol=1e-8)


@test("Step")
def _(solver=solver):
    t, y = solver.step(upto_t=1)
    assert np.allclose(y, np.exp(-t[:, None]), rtol=1e-8, atol=1e-8)


@test("Run")
def _(solver=solver):
    t_in = np.linspace(0, 1, 10)
    t, y = solver.run(t_in)
    assert np.allclose(t, t_in)
    assert np.allclose(y, np.exp(-t[:, None]), rtol=1e-8, atol=1e-8)
