from simbio import Compartment, Parameter, Species
from simbio.compartments import DuplicateComponentError
from simbio.reactions import Conversion
from ward import raises, test


class ModelA(Compartment):
    A = Species(10)
    B = Species(10)
    rate = Parameter(1)

    class Nucleus(Compartment):
        pass

    def add_reactions(self):
        yield Conversion(self.A, self.B, self.rate)


@test("Species collision")
def _():
    class ModelB(ModelA):
        A = Species(20, override=True)

    class ModelC(ModelA):
        A = Species(30, override=True)

    with raises(DuplicateComponentError):

        class WrongModelD(ModelB, ModelC):
            pass

    class ModelD(ModelB, ModelC):
        A = Species(40, override=True)


@test("Parameter collision")
def _():
    class ModelB(ModelA):
        rate = Parameter(2, override=True)

    class ModelC(ModelA):
        rate = Parameter(3, override=True)

    with raises(DuplicateComponentError):

        class WrongModelD(ModelB, ModelC):
            pass

    class ModelD(ModelB, ModelC):
        rate = Parameter(4, override=True)


@test("Compartment collision")
def _():
    class ModelB(ModelA):
        class Nucleus(ModelA.Nucleus):
            A = Species(0)

    class ModelC(ModelA):
        class Nucleus(ModelA.Nucleus):
            A = Species(1)

    with raises(DuplicateComponentError):

        class WrongModelD(ModelB, ModelC):
            pass

    class ModelD(ModelB, ModelC):
        class Nucleus(ModelB.Nucleus, ModelC.Nucleus):
            A = Species(0, override=True)


@test("Compatible sub-Compartments")
def _():
    class ModelB(ModelA):
        class Nucleus(ModelA.Nucleus):
            A = Species(0)

    class ModelC(ModelA):
        class Nucleus(ModelA.Nucleus):
            B = Species(1)

    class WrongModelD(ModelB, ModelC):
        pass


@test("Reaction collision")
def _():
    class ModelB(ModelA):
        rateB = Parameter(1)

        def override_reactions(self):
            yield Conversion(self.A, self.B, self.rateB)

    class ModelC(ModelA):
        rateC = Parameter(2)

        def override_reactions(self):
            yield Conversion(self.A, self.B, self.rateC)

    with raises(DuplicateComponentError):

        class WrongModelD(ModelB, ModelC):
            pass

    class ModelD(ModelB, ModelC):
        rateD = Parameter(3)

        def override_reactions(self):
            yield Conversion(self.A, self.B, self.rateD)
