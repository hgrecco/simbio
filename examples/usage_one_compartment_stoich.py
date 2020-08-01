import matplotlib.pyplot as plt
from simbio import Universe
from simbio.reactions import Synthesis
from simbio.simulator import PandasSimulator as Simulator

##############

cell = Universe("cell")
cell.add_reactant("C", concentration=2)
cell.add_reactant("O2", concentration=1)
cell.add_reactant("CO2", concentration=0)
cell.add_parameter("rate", 0.1)

step1 = Synthesis(A=2 * cell.C, B=2 * cell.O2, AB=2 * cell.CO2, rate=cell.rate)
cell.add_reaction(step1)


sim = Simulator(cell)
_, df = sim.run(100)

df.plot()
plt.show()
