import matplotlib.pyplot as plt

from simbio.components import EmptyCompartment
from simbio.reactions.single import Synthesis
from simbio.simulator import Simulator

cell = EmptyCompartment.to_builder(name="cell")
C = cell.add_species("C", value=2)
O2 = cell.add_species("O2", value=1)
CO2 = cell.add_species("CO2", value=0)
k = cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=C, B=O2, AB=CO2, rate=k)
cell.add_reaction("synthesize_CO2", step1)
cell = cell.build()

sim = Simulator(cell)
_, df = sim.run(range(100))

df.plot()
plt.show()
