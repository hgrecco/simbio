import pytest
from pytest import raises, xfail

from simbio.components import EmptyCompartment, Override, Parameter, Species
from simbio.reactions.single import Creation, Destruction


class Base(EmptyCompartment):
    """A base model to use in extension tests."""

    A: Species = 0
    k: Parameter = 0
    create_A = Creation(A=A, rate=k)


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

    class Manual(EmptyCompartment):
        A: Species = 0
        k: Parameter = 0
        create_A = Creation(A=A, rate=k)
        B: Species = 0
        kb: Parameter = 0
        create_B = Creation(A=B, rate=kb)

    class ExtendedStatic(Base):
        B: Species = 0
        kb: Parameter = 0
        create_B = Creation(A=B, rate=kb)

    ExtendedDynamic = Base.to_builder()
    B = ExtendedDynamic.add_species("B", 0)
    kb = ExtendedDynamic.add_parameter("kb", 0)
    ExtendedDynamic.add_reaction("create_B", Creation(A=B, rate=kb))
    ExtendedDynamic = ExtendedDynamic.build()

    for Extended in (ExtendedStatic, ExtendedDynamic):
        # assert Extended > Base
        assert Extended == Manual

        assert Extended.A.resolve() == Base.A.resolve()
        assert Extended.k.resolve() == Base.k.resolve()
        assert Extended.create_A == Base.create_A


def test_extension_using_inherited():
    """Using inherited components requires
    getting a reference to those components.
    """

    class Manual(EmptyCompartment):
        A: Species = 0
        k: Parameter = 0
        create_A = Creation(A=A, rate=k)
        remove_A = Destruction(A=A, rate=k)

    class ExtendedStatic(Base):
        A: Species
        k: Parameter
        remove_A = Destruction(A=A, rate=k)  # noqa: F821

    ExtendedDynamic = Base.to_builder()
    ExtendedDynamic.add_reaction(
        "remove_A", Destruction(A=ExtendedDynamic.A, rate=ExtendedDynamic.k)
    )
    ExtendedDynamic = ExtendedDynamic.build()

    assert ExtendedStatic == Manual
    assert ExtendedDynamic == Manual


def test_collision():
    """Adding a previously existing components
    must raise a NameError.
    """

    with raises(ValueError):

        class Collision(Base):
            A: Species = 1

    with raises(ValueError):

        class Collision(Base):  # noqa: F811
            k: Parameter = 1

    with raises(ValueError):

        class Collision(Base):  # noqa: F811
            create_A = Creation(A=1, rate=1)

    Collision = Base.to_builder()  # noqa: F811
    with raises(ValueError):
        Collision.add_species("A", 1)
    with raises(ValueError):
        Collision.add_parameter("k", 1)
    with raises(ValueError):
        Collision.add_reaction("create_A", Creation(A=1, rate=1))


def test_override():
    """Overriding existing components in the inherited model."""

    class Manual(EmptyCompartment):
        A: Species = 1
        k: Parameter = 1
        create_A = Creation(A=A, rate=k)

    class OverridenStatic(Base):
        A: Species[Override] = 1
        k: Parameter[Override] = 1

    OverridenDynamic = Base.to_builder()
    OverridenDynamic.add_species("A", 1, replace=True)
    OverridenDynamic.add_parameter("k", 1, replace=True)
    OverridenDynamic = OverridenDynamic.build()

    for Overriden in (OverridenStatic, OverridenDynamic):
        assert Overriden != Base
        assert Overriden == Manual

        assert Overriden.A != Base.A
        assert Overriden.k != Base.k

        assert Overriden.create_A == Base.create_A


def test_override_2():
    """Overriding with dependencies.

    Species Base.A is not linked to parameter Base.k.
    We want to modify the model to link them.
    """

    class Base(EmptyCompartment):
        A: Species = 0
        k: Parameter = 0

    class Expected(EmptyCompartment):
        k: Parameter = 1
        A: Species = k

    class Overriden(Base):
        k: Parameter[Override] = 1
        A: Species[Override] = k

    assert Overriden == Expected


def test_cyclic_override():
    """Overriding elements might induce cyclic references.

    Cycles can only happen between components of a particular level,
    as a component cannot depend on a lower level component.
    """
    xfail("Not implemented")

    class Base(EmptyCompartment):
        a: Parameter = 0
        b: Parameter = a

    with raises(ValueError):

        class Direct(Base):
            """A direct cycle: A <-> B"""

            b: Parameter
            a: Parameter[Override] = b  # noqa: F821

    with raises(ValueError):

        class Indirect(Base):
            """A indirect cycle: A -> B -> C -> A"""

            b: Parameter
            c: Parameter = b  # noqa: F821
            a: Parameter[Override] = c


def test_extend_and_override():
    """Extend and override with dependencies.

    We want to add a new Parameter and link a previous Species to it.
    """

    class Base(EmptyCompartment):
        A: Species = 0

    class Expected(EmptyCompartment):
        k: Parameter = 0
        A: Species = k

    class Overriden(Base):
        k: Parameter = 0
        A: Species[Override] = k

    assert Overriden == Expected


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
