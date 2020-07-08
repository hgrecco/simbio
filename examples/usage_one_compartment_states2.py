import matplotlib.pyplot as plt
from simbio import Compartment, DataFrame, Reactant
from simbio.reactions.enzymatic import MichaelisMentenEqApprox

##############

cell = Compartment("cell")
C = Reactant("C", concentration=1, states=dict(a="u p", b="u p"))
cell.add_reactant(C)
cell.add_parameter("K", 0.1)
cell.add_parameter("D", 0.1)
step1 = MichaelisMentenEqApprox(
    S=cell.C.u_u, P=cell.C.p_u, maximum_velocity=cell.K, dissociation_constant=cell.D,
)
step2 = MichaelisMentenEqApprox(
    S=cell.C.u_u, P=cell.C.u_p, maximum_velocity=cell.K, dissociation_constant=cell.D,
)
step3 = MichaelisMentenEqApprox(
    S=cell.C.p_u, P=cell.C.p_p, maximum_velocity=cell.K, dissociation_constant=cell.D,
)
step4 = MichaelisMentenEqApprox(
    S=cell.C.u_p, P=cell.C.p_p, maximum_velocity=cell.K, dissociation_constant=cell.D,
)

cell.add_reaction(step1)
cell.add_reaction(step2)
cell.add_reaction(step3)
cell.add_reaction(step4)


sim = DataFrame(cell)
df = sim.df_run(100)

df.plot(x="time")
plt.show()
