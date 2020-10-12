import numpy as np
from simbio import Universe
from simbio.reactions import ReversibleSynthesis, Synthesis
from simbio.simulator import Simulator
from ward import fixture, test


@fixture
def universe():
    cell = Universe(name="cell")
    cell.add_species("C", value=2)
    cell.add_species("O2", value=1)
    cell.add_species("CO", value=0)
    cell.add_species("CO2", value=0)
    cell.add_parameter("k", value=0.1)
    return cell


@test("Universe copy with stoichiometric coefficients")
def _(cell=universe):
    C, O2, CO, CO2, k = cell.C, cell.O2, cell.CO, cell.CO2, cell.k

    cell.add_reaction(Synthesis(A=2 * C, B=O2, AB=2 * CO, rate=k))
    cell.add_reaction(
        ReversibleSynthesis(
            A=2 * C, B=2 * O2, AB=2 * CO2, forward_rate=k, reverse_rate=k
        )
    )

    t1, y1 = Simulator(cell).run(10)
    t2, y2 = Simulator(cell.copy()).run(10)

    assert np.allclose(t1, t2)
    assert np.allclose(y1, y2)
