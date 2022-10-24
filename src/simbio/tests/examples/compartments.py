import numpy as np

from simbio.components import EmptyCompartment, Species
from simbio.reactions.single import Conversion, Dissociation, Synthesis
from simbio.simulator import Simulator


class Outer(EmptyCompartment):
    class Inner1(EmptyCompartment):
        H2: Species = 1
        O2: Species = 1
        H2O: Species = 0

        create_water = Synthesis(A=2 * H2, B=O2, AB=2 * H2O, rate=2)

    class Inner2(EmptyCompartment):
        H2: Species = 1
        O2: Species = 1
        H2O: Species = 0

        electrolysis = Dissociation(AB=2 * H2O, A=2 * H2, B=O2, rate=0.5)

    # Transport between compartments
    water_transport = Conversion(A=Inner1.H2O, B=Inner2.H2O, rate=1)
    H2_transport = Conversion(A=Inner2.H2, B=Inner1.H2, rate=1)
    O2_transport = Conversion(A=Inner2.O2, B=Inner1.O2, rate=1)


simulator = Simulator(Outer)

t = np.linspace(0, 10, 100)
df = simulator.run(t)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    df.filter(like="H2O").plot()
    plt.show()
