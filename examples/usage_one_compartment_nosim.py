from functools import partial

import matplotlib.pyplot as plt
from scipy.integrate import RK45
from simbio import Universe
from simbio.reactions import Synthesis

##############

cell = Universe("cell")
cell.add_species("C", concentration=2)
cell.add_species("O2", concentration=1)
cell.add_species("CO2", concentration=0)
cell.add_parameter("k", value=0.1)

step1 = Synthesis(A=cell.C, B=cell.O2, AB=cell.CO2, rate=cell.k)
cell.add_reaction(step1)

initial = cell._build_concentration_vector()
parameters = cell._build_parameter_vector()
rhs = cell._build_ip_rhs()
names = cell._in_reaction_species_names
# Just a stupid test
assert rhs(0, initial, parameters).shape == initial.shape

solver = RK45(partial(rhs, p=parameters), 0, initial, 100)

print("Starting ...")
t_values = []
y_values = []
for _ in range(100):
    # get solution step state
    solver.step()
    t_values.append(solver.t)
    y_values.append(solver.y)
    # break loop after modeling is finished
    if solver.status == "finished":
        break


plt.plot(t_values, y_values)
plt.legend(names)
plt.show()
