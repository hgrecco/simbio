import matplotlib.pyplot as plt
import simbio.algo
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


sim = Simulator(cell, output="numpy")
t_values, y_values = sim.run(range(100))

plt.plot(t_values, y_values)
plt.legend(sim.names)

t, y = simbio.algo.find_steady_state(sim)
for a in y:
    plt.axhline(a, 0, max(t, t_values[-1]), c="k", ls=":")
plt.show()
