import matplotlib.pyplot as plt
from simbio import Compartment
from simbio.reactions import Synthesis
from simbio.simulator import Simulator

##############

cell = Compartment(name="cell")
cell.add_species("C", value=2)
cell.add_species("O2", value=1)
cell.add_species("CO2", value=0)
cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=cell.C, B=cell.O2, AB=cell.CO2, rate=cell.k)
cell.add_reaction(step1)


sim = Simulator(cell)
t_values, y_values = sim.run(range(0, 100, 1))

plt.plot(t_values, y_values)
plt.legend(sim.names)
plt.show()
