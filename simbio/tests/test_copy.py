import numpy as np
from simbio import Compartment, Parameter, Species
from simbio.reactions import ReversibleSynthesis, Synthesis
from simbio.simulator import Simulator
from ward import test


@test("Model copy with stoichometric numbers")
def _():
    class Model(Compartment):
        C = Species(2)
        O2 = Species(1)
        CO = Species(0)
        CO2 = Species(0)

        k = Parameter(0.1)

    Model.add_reaction(Synthesis(A=Model.C, B=Model.O2, AB=Model.CO2, rate=Model.k))
    Model.add_reaction(
        ReversibleSynthesis(
            A=Model.C,
            B=Model.O2,
            AB=2 * Model.CO,
            forward_rate=Model.k,
            reverse_rate=Model.k,
        )
    )

    t1, y1 = Simulator(Model).run(10)
    t2, y2 = Simulator(Model.copy()).run(10)

    assert np.allclose(t1, t2)
    assert np.allclose(y1, y2)
