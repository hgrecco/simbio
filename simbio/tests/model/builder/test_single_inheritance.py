import pytest
from pytest import raises
from simbio.model import Compartment, Parameter, Species
from simbio.reactions import Creation, Destruction


class Base(Compartment):
    """A base model to use in extension tests."""

    A: Species = 0
    k: Parameter = 0
    create_A = Creation(A, k)


def test_extension_as_copy():
    """Inheriting a model without adding anything
    results in a copy.
    """

    class StaticCopy(Base):
        pass

    DynamicCopy = Base.to_builder().build()

    for Copy in (StaticCopy, DynamicCopy):
        assert Copy == Base
        assert Copy is not Base


def test_extension():
    """Adding new components in an inheriting model."""

    class ExtendedStatic(Base):
        B: Species = 0
        kb: Parameter = 0
        create_B = Creation(B, kb)

    ExtendedDynamic = Base.to_builder()
    B = ExtendedDynamic.add_species("B", 0)
    kb = ExtendedDynamic.add_parameter("kb", 0)
    ExtendedDynamic.add_reaction(Creation(B, kb))
    ExtendedDynamic = ExtendedDynamic.build()

    assert ExtendedStatic == ExtendedDynamic

    for Extended in (ExtendedStatic, ExtendedDynamic):
        assert Extended > Base

        assert Extended.A == Base.A
        assert Extended.k == Base.k
        assert Extended.create_A == Base.create_A


def test_extension_using_inherited():
    """Using inherited components requires
    getting a reference to those components.
    """

    class ExtendedStatic(Base):
        A: Species
        k: Parameter
        remove_A = Destruction(A, k)  # noqa: F821

    ExtendedDynamic = Base.to_builder()
    ExtendedDynamic.add_reaction(Destruction(ExtendedDynamic.A, ExtendedDynamic.k))
    ExtendedDynamic = ExtendedDynamic.build()

    assert ExtendedStatic == ExtendedDynamic


def test_collision():
    """Adding a previously existing components
    must raise a NameError.
    """

    with raises(NameError):

        class Collision(Base):
            A: Species = 1

    with raises(NameError):

        class Collision(Base):  # noqa: F811
            k: Parameter = 1

    with raises(NameError):

        class Collision(Base):  # noqa: F811
            create_A = Creation(A=1, rate=1)

    Collision = Base.to_builder()  # noqa: F811
    with raises(NameError):
        Collision.add_species("A", 1)
    with raises(NameError):
        Collision.add_parameter("k", 1)
    with raises(NameError):
        Collision.add_reaction("create_A", Creation(A=1, rate=1))


def test_override():
    """Overriding existing components in the inherited model."""

    class OverridenStatic1(Base(A=1, k=1)):
        pass

    OverridenStatic2 = Base(A=1, k=1)

    OverridenDynamic = Base.to_builder()
    OverridenDynamic.replace_species("A", 1)
    OverridenDynamic.replace_parameter("k", 1)
    OverridenDynamic = OverridenDynamic.build()

    assert OverridenStatic1 == OverridenStatic2 == OverridenDynamic

    for Overriden in (OverridenStatic1, OverridenStatic2, OverridenDynamic):
        assert Overriden != Base

        assert Overriden.A != Base.A
        assert Overriden.k != Base.k

        assert Overriden.create_A == Base.create_A


@pytest.mark.xfail(reason="Not implemented")
def test_remove():
    class RemovedStatic(Base):
        A: Species
        del A  # noqa: F821

    RemovedDynamic = Base.to_builder()
    RemovedDynamic.remove_species("A", 1)
    RemovedDynamic = RemovedDynamic.build()

    assert RemovedStatic == RemovedDynamic

    for Removed in (RemovedStatic, RemovedDynamic):
        assert Removed < Base

        assert Removed.k == Base.k

        with raises(NameError):
            assert Removed.A
        with raises(NameError):
            assert Removed.create_A
