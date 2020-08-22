import matplotlib.pyplot as plt
from simbio import Universe
from simbio.reactions import Dissociation, Synthesis
from simbio.simulator import PandasSimulator as Simulator

##############

cell = Universe("cell")
cytosol = cell.add_compartment("cytosol")
nucleus = cell.add_compartment("nucleus")

cytosol.add_species("C", concentration=2)
cytosol.add_species("O2", concentration=1)
cytosol.add_species("CO2", concentration=0)
cytosol.add_parameter("rate", 0.1)
react1 = Synthesis(A=cytosol.C, B=cytosol.O2, AB=cytosol.CO2, rate=cytosol.rate)
cytosol.add_reaction(react1)

nucleus.add_species("C", concentration=0)
nucleus.add_species("O2", concentration=0)
nucleus.add_species("CO2", concentration=1.5)
nucleus.add_parameter("rate", 0.1)
react2 = Dissociation(A=nucleus.C, B=nucleus.O2, AB=nucleus.CO2, rate=nucleus.rate)
nucleus.add_reaction(react2)


sim = Simulator(cell, observed_names=("nucleus.C", "cytosol.C"))
_, df = sim.run(100)

df.plot(x="time")
plt.show()
