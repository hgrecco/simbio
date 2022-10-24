import numpy as np

from simbio.components import EmptyCompartment, Species
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator


class Model(EmptyCompartment):
    H2: Species = 1
    O2: Species = 1
    H2O: Species = 0

    create_water = Synthesis(A=2 * H2, B=O2, AB=2 * H2O, rate=1)


simulator = Simulator(Model)

t = np.linspace(0, 10, 100)
df = simulator.run(t)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    df.plot()
    plt.show()
