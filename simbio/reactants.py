"""
    simbio.reactants
    ~~~~~~~~~~~~~~~~

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


class Reactant:
    def __init__(self, name: str, concentration: float = 0):
        self.name = name
        self.concentration = concentration

    def __mul__(self, other):
        if not isinstance(other, (float, int)):
            raise TypeError("Only floats and ints can multiply a Reactant")

        return InReactionReactant(self, other)

    __rmul__ = __mul__


class InReactionReactant:
    def __init__(self, reactant: Reactant, st_number=1):
        self.reactant = reactant
        self.st_number = st_number

    @property
    def name(self):
        return self.reactant.name

    @property
    def concentration(self):
        return self.reactant.concentration
