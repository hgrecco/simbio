import matplotlib.pyplot as plt
from simbio import Compartment, Reactant, SimulatorDataFrame
from simbio.reactions.enzymatic import MichaelisMentenEqApprox

##############

cell = Compartment("cell")
C = Reactant("C", concentration=1, states="u p pp")
cell.add_reactant(C)
cell.add_parameter("K", 0.1)
cell.add_parameter("D", 0.1)
step1 = MichaelisMentenEqApprox(
    S=cell.C.u, P=cell.C.p, maximum_velocity=cell.K, dissociation_constant=cell.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.p, P=cell.C.pp, maximum_velocity=cell.K, dissociation_constant=cell.D,
)

cell.add_reaction(step1)
cell.add_reaction(step2)


sim = SimulatorDataFrame(cell)
df = sim.run(100)

df.plot(x="time")
plt.show()
