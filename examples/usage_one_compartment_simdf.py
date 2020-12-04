import matplotlib.pyplot as plt
from simbio import Compartment, Simulator
from simbio.reactions import Synthesis

##############

cell = Compartment(name="cell")
cell.add_species("C", value=2)
cell.add_species("O2", value=1)
cell.add_species("CO2", value=0)
cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=cell.C, B=cell.O2, AB=cell.CO2, rate=cell.k)
cell.add_reaction(step1)


sim = Simulator(cell)
_, df = sim.run(100)

df.plot()
plt.show()
