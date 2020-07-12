# flake8: noqa

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import RK45
from simbio import Reactant, Universe
from simbio.reactions import Synthesis

################
# explicity reactant (should work)

cell = Universe("cell")
C = Reactant("C", concentration=2)
O2 = Reactant("O2", concentration=1)
CO2 = Reactant("CO2", concentration=0)

cell = Universe("cell")
cell.add_reactant(C)
cell.add_reactant(O2)
cell.add_reactant(CO2)

################
# from_string (not implemented yet)

cell = Universe("cell")
cell.from_string(
    """
C = 3
O2 = 1
CO2 = 0
R = 1
C + O2 -(R)-> CO2 
"""
)


################
# context managers (not implemented yet)

with Universe("cell") as cell:
    cell.add_reactant("C", concentration=2)
    cell.add_reactant("O2", concentration=1)
    cell.add_reactant("CO2", concentration=0)


################
# auto reactants (not implemented yet)

cell = Universe("cell")
react1 = Synthesis(A="C", B="O2", AB="CO2")
cell.add_reaction(react1)
