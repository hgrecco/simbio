import matplotlib.pyplot as plt
from simbio import Simulator, Universe, algo
from simbio.reactions import Synthesis

##############

cell = Universe("cell")
cell.add_reactant("C", concentration=2)
cell.add_reactant("O2", concentration=1)
cell.add_reactant("CO2", concentration=0)
cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=cell.C, B=cell.O2, AB=cell.CO2, rate=cell.k)
cell.add_reaction(step1)


sim = Simulator(cell)
t_values, y_values = sim.run(100)

plt.plot(t_values, y_values)
plt.legend(sim.names)

t, y = algo.find_steady_state(sim, 200, 1)
for a in y:
    plt.axhline(a, 0, max(t, t_values[-1]), c="k", ls=":")
plt.show()
