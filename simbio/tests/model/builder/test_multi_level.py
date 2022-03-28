from pytest import raises
from simbio.model import Compartment, Group, Parameter, Species


def test_shared_parameter():
    """A multi-level model with a shared Parameter."""

    class Static(Compartment):
        k = Parameter(1)
        A = Species(k)

        class Inner(Compartment):
            k: Parameter
            A = Species(k)  # noqa: F821

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
            A = Species(0)

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
        A = Species(0)

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
                A = Species(k)  # noqa: F821

    with raises(NameError):

        class First(Compartment):  # noqa: F811
            class Second(Group):
                k: Parameter
                A = Species(k)  # noqa: F821

    with raises(NameError):

        class First(Group):  # noqa: F811
            class Second(Group):
                k: Parameter
                A = Species(k)  # noqa: F821

    # Can't be replicated dynamically


def test_skip_level_parameter():
    """A multi-level model with a free Parameter
    which is not available in the parent Comparment
    or Group must raise a NameError.
    """
    with raises(NameError):

        class Static(Compartment):
            k = Parameter(1)

            class First(Compartment):
                class Second(Compartment):
                    k: Parameter
                    A = Species(k)  # noqa: F821

    Dynamic = Compartment.to_builder()
    k = Dynamic.add_parameter("k", 1)
    Second = Dynamic.add_comartment("First").add_compartment("Second")
    with raises(NameError):
        Second.add_species("A", k)
