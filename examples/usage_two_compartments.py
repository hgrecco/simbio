import matplotlib.pyplot as plt
from scipy.integrate import RK45
from simbio import Compartment, Universe
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

initial = uni.build_concentration_vector()
rhs = uni.build_ip_rhs()
names = uni.names()

# Just a stupid test
assert rhs(0, initial).shape == initial.shape

solver = RK45(rhs, 0, initial, 100)

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
