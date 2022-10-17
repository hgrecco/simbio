import numpy as np

from simbio.components import EmptyCompartment, Species
from simbio.reactions.enzymatic import MichaelisMenten
from simbio.simulator import Simulator


class Model(EmptyCompartment):
    enzyme: Species = 1
    subtrate: Species = 1
    product: Species = 0

    catalyze = MichaelisMenten(
        E=enzyme,
        S=subtrate,
        ES=0,  # "nameless" intermediate species
        P=product,
        forward_rate=1,
        reverse_rate=1,
        catalytic_rate=1,
    )


simulator = Simulator(Model)

t = np.linspace(0, 10, 100)
df = simulator.run(t)

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    df.plot()
    plt.show()
