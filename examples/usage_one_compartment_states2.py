import matplotlib.pyplot as plt
from simbio import Universe
from simbio.reactions.enzymatic import MichaelisMentenEqApprox
from simbio.simulator import PandasSimulator as Simulator

##############

cell = Universe("cell")
C = cell.add_compartment("C")
C.add_species("u_u", value=1)
C.add_species("u_p")
C.add_species("p_u")
C.add_species("p_p")
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


sim = Simulator(cell)
_, df = sim.run(100)

df.plot()
plt.show()
