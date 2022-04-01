from pytest import raises

from simbio.model import Compartment, Group, Parameter, Species


def test_shared_parameter():
    """A multi-level model with a shared Parameter."""

    class Static(Compartment):
        k: Parameter = 1
        A: Species = k

        class Inner(Compartment):
            k: Parameter
            A: Species = k  # noqa: F821

    Dynamic = Compartment.to_builder()
    k = Dynamic.add_parameter("k", 1)
    Dynamic.add_species("A", k)
    Inner = Compartment.add_compartment("Inner")
    Inner.add_species("A", k)
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_shared_species_compartment():
    """A multi-level model with a shared Species
    between Compartments must raise a TypeError.

    Species must belong to a single Compartment.
    """
    with raises(TypeError):

        class Static(Compartment):
            A: Species = 0

            class Inner(Compartment):
                A: Species

    Dynamic = Compartment.to_builder()
    A = Dynamic.add_species("A", 0)
    Inner = Compartment.add_compartment("Inner")
    with raises(TypeError):
        Inner.add_species("A", A)


def test_shared_species_group():
    """A multi-level model with a shared Species
    between a Compartment and a Group.
    """

    class Static(Compartment):
        A: Species = 0

        class Inner(Group):
            A: Species

    Dynamic = Compartment.to_builder()
    A = Dynamic.add_species("A", 0)
    Inner = Compartment.add_group("Inner")
    Inner.add_species("A", A)
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_missing_parameter():
    """A multi-level model with a free Parameter
    which is not available in the parent Comparment
    or Group must raise a NameError.
    """
    with raises(NameError):

        class First(Compartment):
            class Second(Compartment):
                k: Parameter
                A: Species = k  # noqa: F821

    with raises(NameError):

        class First(Compartment):  # noqa: F811
            class Second(Group):
                k: Parameter
                A: Species = k  # noqa: F821

    with raises(NameError):

        class First(Group):  # noqa: F811
            class Second(Group):
                k: Parameter
                A: Species = k  # noqa: F821

    # Can't be replicated dynamically


def test_skip_level_parameter():
    """A multi-level model with a free Parameter
    which is not available in the parent Comparment
    or Group must raise a NameError.
    """
    with raises(NameError):

        class Static(Compartment):
            k: Parameter = 1

            class First(Compartment):
                class Second(Compartment):
                    k: Parameter
                    A: Species = k  # noqa: F821

    Dynamic = Compartment.to_builder()
    k = Dynamic.add_parameter("k", 1)
    Second = Dynamic.add_comartment("First").add_compartment("Second")
    with raises(NameError):
        Second.add_species("A", k)


def test_skip_level_species():
    """A Species can only be "linked" from its first parent."""
    First = Compartment.to_builder()
    Second = First.add_group("Second")
    Third = Second.add_group("Third")

    First.add_species("A", 0)

    with raises(ValueError):
        # First.A does not belong to upper compartment.
        Third.add_species("A", First.A)

    Second.add_species("A", First.A)

    with raises(ValueError):
        # First.A does not belong to upper compartment,
        # eventhough it is "in" Second.A
        Third.add_species("A", First.A)


def test_add_group():
    class Single(Group):
        A: Species
        B: Species = 0

    class Compound(Group):
        X: Species = 0
        group_X = Single(A=X)  # outer species
        group_Y = Single(A=1)  # inner species
        group_Z = Single(A=1, B=1)  # replaces inner default

    with raises(ValueError):

        class InexistentOuter(Group):
            # It references an outer Species X.
            group_X = Compound.group_X

    with raises(ValueError):

        class ExistentOuter(Group):
            X: Species = 0
            # It references an outer Species X.
            group_X = Compound.group_X

    class ReplacedOuter(Group):
        X: Species = 0
        group_X = Compound.group_X(A=X)  # Is this allowed?
