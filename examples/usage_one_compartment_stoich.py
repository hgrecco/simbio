import matplotlib.pyplot as plt

from simbio.components import EmptyCompartment
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator

cell = EmptyCompartment.to_builder(name="cell")
cell.add_species("C", value=2)
cell.add_species("O2", value=1)
cell.add_species("CO", value=0)
cell.add_parameter("rate", 0.1)

step1 = Synthesis(A=2 * cell.C, B=cell.O2, AB=cell.CO, rate=cell.rate)
cell.add_reaction("synthesize_CO", step1)


sim = Simulator(cell, builder="numba")
_, df = sim.run(range(100))

df.plot()
plt.show()
