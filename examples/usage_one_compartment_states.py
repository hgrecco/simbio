import matplotlib.pyplot as plt
from simbio import Simulator, Universe
from simbio.reactions.enzymatic import MichaelisMentenEqApprox

##############

cell = Universe("cell")
C = cell.add_compartment("C")
C.add_reactant("u", concentration=1)
C.add_reactant("p", concentration=0)
C.add_reactant("pp", concentration=1)

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


sim = Simulator(cell)
df = sim.df_run(100)

df.plot(x="time")
plt.show()
