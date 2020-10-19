from simbio import Compartment, Parameter, Species
from simbio.compartments import DuplicateComponentError
from simbio.reactions import Creation
from ward import raises, test


@test("Duplicate Species")
def _():
    with raises(DuplicateComponentError):

        class ModelA(Compartment):
            x = Species(0)
            x = Species(1)

    with raises(DuplicateComponentError):

        class ModelB(Compartment):
            x = Species(0)
            x = Species(1, override=True)


@test("Duplicate Parameter")
def _():
    with raises(DuplicateComponentError):

        class ModelA(Compartment):
            x = Parameter(0)
            x = Parameter(1)

    with raises(DuplicateComponentError):

        class ModelB(Compartment):
            x = Parameter(0)
            x = Parameter(1, override=True)


@test("Duplicate Compartment")
def _():
    with raises(DuplicateComponentError):

        class ModelA(Compartment):
            class SubModelA(Compartment):
                pass

            class SubModelA(Compartment):  # noqa: F811
                pass

    with raises(TypeError):

        class ModelB(Compartment):
            class SubModelB(Compartment):
                pass

            class SubModelB(Compartment, override=True):  # noqa: F811
                pass


@test("Duplicate identical Reaction")
def _():
    with raises(DuplicateComponentError):

        class ModelA(Compartment):
            x = Species(0)
            k = Parameter(0)

            def add_reactions(self):
                yield Creation(self.x, self.k)
                yield Creation(self.x, self.k)

    with raises(DuplicateComponentError):

        class ModelB(Compartment):
            x = Species(0)
            k = Parameter(0)

            def add_reactions(self):
                yield Creation(self.x, self.k)

            def override_reactions(self):
                yield Creation(self.x, self.k)

    with raises(DuplicateComponentError):

        class ModelC(Compartment):
            x = Species(0)
            k = Parameter(0)

            def override_reactions(self):
                yield Creation(self.x, self.k)
                yield Creation(self.x, self.k)


@test("Duplicate equivalent Reaction")
def _():
    with raises(DuplicateComponentError):

        class ModelA(Compartment):
            x = Species(0)
            k1 = Parameter(0)
            k2 = Parameter(0)

            def add_reactions(self):
                yield Creation(self.x, self.k1)
                yield Creation(self.x, self.k2)

    with raises(DuplicateComponentError):

        class ModelB(Compartment):
            x = Species(0)
            k1 = Parameter(0)
            k2 = Parameter(0)

            def add_reactions(self):
                yield Creation(self.x, self.k1)

            def override_reactions(self):
                yield Creation(self.x, self.k2)

    with raises(DuplicateComponentError):

        class ModelC(Compartment):
            x = Species(0)
            k1 = Parameter(0)
            k2 = Parameter(0)

            def override_reactions(self):
                yield Creation(self.x, self.k1)
                yield Creation(self.x, self.k2)
