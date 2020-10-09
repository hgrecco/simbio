import numpy as np
from simbio import Compartment
from simbio.reactions import ReversibleSynthesis, Synthesis
from simbio.simulator import Simulator
from ward import fixture, test


@fixture
def cell():
    cell = Compartment(name="cell")
    cell.add_species("C", value=2)
    cell.add_species("O2", value=1)
    cell.add_species("CO", value=0)
    cell.add_species("CO2", value=0)
    cell.add_parameter("k", value=0.1)
    return cell


@test("Model copy")
def _(cell=cell):
    C, O2, CO, CO2, k = cell.C, cell.O2, cell.CO, cell.CO2, cell.k

    cell.add_reaction(Synthesis(A=C, B=O2, AB=CO2, rate=k))
    cell.add_reaction(
        ReversibleSynthesis(A=C, B=O2, AB=CO, forward_rate=k, reverse_rate=k)
    )

    t1, y1 = Simulator(cell).run(10)
    t2, y2 = Simulator(cell.copy()).run(10)

    assert np.allclose(t1, t2)
    assert np.allclose(y1, y2)


@test("Model copy with stoichometric numbers")
def _(cell=cell):
    C, O2, CO2, k = cell.C, cell.O2, cell.CO2, cell.k

    cell.add_reaction(Synthesis(A=2 * C, B=3 * O2, AB=4 * CO2, rate=k))
    cell.add_reaction(
        ReversibleSynthesis(
            A=2 * C, B=2 * O2, AB=2 * CO2, forward_rate=k, reverse_rate=k
        )
    )

    t1, y1 = Simulator(cell).run(10)
    t2, y2 = Simulator(cell.copy()).run(10)

    assert np.allclose(t1, t2)
    assert np.allclose(y1, y2)
