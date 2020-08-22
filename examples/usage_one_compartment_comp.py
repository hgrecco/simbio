import matplotlib.pyplot as plt
from simbio import Universe
from simbio.reactions import ReversibleSynthesis
from simbio.simulator import Simulator

##############

cell = Universe("cell")
cell.add_species("C", concentration=2)
cell.add_species("O2", concentration=1)
cell.add_species("CO2", concentration=0)
cell.add_parameter("forward_rate", 0.1)
cell.add_parameter("reverse_rate", 0.05)

step1 = ReversibleSynthesis(
    A=cell.C,
    B=cell.O2,
    AB=cell.CO2,
    forward_rate=cell.forward_rate,
    reverse_rate=cell.reverse_rate,
)
cell.add_reaction(step1)

sim = Simulator(cell)
t_values, y_values = sim.run(100)

plt.plot(t_values, y_values)
plt.legend(sim.names)
plt.show()
