import matplotlib.pyplot as plt
from simbio import Compartment, Simulator, Universe
from simbio.reactions import Dissociation, Synthesis

##############

cytosol = Compartment("cytosol")
cytosol.add_reactant("C", concentration=2)
cytosol.add_reactant("O2", concentration=1)
cytosol.add_reactant("CO2", concentration=0)
cytosol.add_parameter("rate", 0.1)
react1 = Synthesis(A=cytosol.C, B=cytosol.O2, AB=cytosol.CO2, rate=cytosol.rate)
cytosol.add_reaction(react1)

nucleus = Compartment("nucleus")
nucleus.add_reactant("C", concentration=0)
nucleus.add_reactant("O2", concentration=0)
nucleus.add_reactant("CO2", concentration=1.5)
nucleus.add_parameter("rate", 0.1)
react2 = Dissociation(A=nucleus.C, B=nucleus.O2, AB=nucleus.CO2, rate=nucleus.rate)
nucleus.add_reaction(react2)

uni = Universe()
uni.add_compartment(cytosol)
uni.add_compartment(nucleus)


sim = Simulator(uni)
df = sim.df_run(100)

df.plot(x="time")
plt.show()
