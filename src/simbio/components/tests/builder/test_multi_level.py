from pytest import raises, xfail

from simbio.components import EmptyCompartment, EmptyGroup, Parameter, Species
from simbio.reactions.single import Conversion


def test_multi_level_model():
    """A multi-level model with a shared Parameter."""

    class Static(EmptyCompartment):
        k: Parameter = 1
        A: Species = k

        class Inner(EmptyCompartment):
            k: Parameter = 2
            A: Species = k  # noqa: F821

    Dynamic = EmptyCompartment.to_builder()
    k_outer = Dynamic.add_parameter("k", 1)
    Dynamic.add_species("A", k_outer)
    Inner = Dynamic.add_compartment("Inner")
    k_inner = Inner.add_parameter("k", 2)
    Inner.add_species("A", k_inner)
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_shared_parameter():
    """A multi-level model with a shared Parameter."""
    xfail("Not implemented")

    class Static(EmptyCompartment):
        k: Parameter = 1
        A: Species = k

        class Inner(EmptyCompartment):
            k: Parameter
            A: Species = k  # noqa: F821

    Dynamic = EmptyCompartment.to_builder()
    k = Dynamic.add_parameter("k", 1)
    Dynamic.add_species("A", k)
    Inner = Dynamic.add_compartment("Inner")
    Inner.add_species("A", k)
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_shared_species_compartment():
    """A multi-level model with a shared Species
    between Compartments must raise a TypeError.

    Species must belong to a single Compartment.
    """
    xfail("Not implemented")
    with raises(TypeError):

        class Static(EmptyCompartment):
            A: Species = 0

            class Inner(EmptyCompartment):
                A: Species

    Dynamic = EmptyCompartment.to_builder()
    A = Dynamic.add_species("A", 0)
    Inner = EmptyCompartment.add_compartment("Inner")
    with raises(TypeError):
        Inner.add_species("A", A)


def test_shared_species_group():
    """A multi-level model with a shared Species
    between a Compartment and a Group.
    """
    xfail("Not implemented")

    class Static(EmptyCompartment):
        A: Species = 0

        class Inner(EmptyGroup):
            A: Species

    Dynamic = EmptyCompartment.to_builder()
    A = Dynamic.add_species("A", 0)
    Inner = EmptyCompartment.add_group("Inner")
    Inner.add_species("A", A)
    Dynamic = Dynamic.build()

    assert Static == Dynamic


def test_missing_parameter():
    """A multi-level model with a free Parameter
    which is not available in the parent Comparment
    or Group must raise a NameError.
    """
    xfail("Not implemented")
    with raises(NameError):

        class First(EmptyCompartment):
            class Second(EmptyCompartment):
                k: Parameter
                A: Species = k  # noqa: F821

    with raises(NameError):

        class First(EmptyCompartment):  # noqa: F811
            class Second(EmptyGroup):
                k: Parameter
                A: Species = k  # noqa: F821

    with raises(NameError):

        class First(EmptyGroup):  # noqa: F811
            class Second(EmptyGroup):
                k: Parameter
                A: Species = k  # noqa: F821

    # Can't be replicated dynamically


def test_xfail_level_parameter():
    """A multi-level model with a free Parameter
    which is not available in the parent Comparment
    or Group must raise a NameError.
    """
    xfail("Not implemented")
    with raises(NameError):

        class Static(EmptyCompartment):
            k: Parameter = 1

            class First(EmptyCompartment):
                class Second(EmptyCompartment):
                    k: Parameter
                    A: Species = k  # noqa: F821

    Dynamic = EmptyCompartment.to_builder()
    k = Dynamic.add_parameter("k", 1)
    Second = Dynamic.add_comartment("First").add_compartment("Second")
    with raises(NameError):
        Second.add_species("A", k)


def test_xfail_level_species():
    """A Species can only be "linked" from its first parent."""
    xfail("Not implemented")
    First = EmptyCompartment.to_builder()
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
    xfail("Not implemented")

    class Single(EmptyGroup):
        A: Species
        B: Species = 0

    class Compound(EmptyGroup):
        X: Species = 0
        group_X = Single(A=X)  # outer species
        group_Y = Single(A=1)  # inner species
        group_Z = Single(A=1, B=1)  # replaces inner default

    with raises(ValueError):

        class InexistentOuter(EmptyGroup):
            # It references an outer Species X.
            group_X = Compound.group_X

    with raises(ValueError):

        class ExistentOuter(EmptyGroup):
            X: Species = 0
            # It references an outer Species X.
            group_X = Compound.group_X

    class ReplacedOuter(EmptyGroup):
        X: Species = 0
        group_X = Compound.group_X(A=X)  # Is this allowed?


def test_intergroup_reaction():
    class Model(EmptyCompartment):
        class GroupA(EmptyGroup):
            A: Species = 1

        class GroupB(EmptyGroup):
            B: Species = 0

        A_to_B = Conversion(A=GroupA.A, B=GroupB.B, rate=1)

    assert Model.A_to_B.A.resolve(recursive=True) == Model.GroupA.A.resolve()
