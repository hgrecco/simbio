import matplotlib.pyplot as plt
from simbio import Compartment, SimulatorDataFrame
from simbio.reactions import Synthesis

##############

cell = Compartment("cell")
cell.add_reactant("C", concentration=2)
cell.add_reactant("O2", concentration=1)
cell.add_reactant("CO2", concentration=0)
cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=cell.C, B=cell.O2, AB=cell.CO2, rate=cell.k)
cell.add_reaction(step1)


sim = SimulatorDataFrame(cell)
df = sim.run(100)

df.plot(x="time")
plt.show()
