from pytest import raises

from simbio.components import EmptyCompartment, Override, Parameter, Species


def test_add_species_to_outer():
    class Outer(EmptyCompartment):
        """Base model."""

        A: Species = 0

        class Inner(EmptyCompartment):
            A: Species = 0

    class ExtendedOuter(Outer):
        """Extends Outer and inherits inner."""

        B: Species = 1

    class ExpectedOuter(EmptyCompartment):
        A: Species = 0
        B: Species = 1

        class Inner(EmptyCompartment):
            A: Species = 0

    assert ExtendedOuter == ExpectedOuter


def test_add_species_to_inner():
    class Outer(EmptyCompartment):
        """Base model."""

        A: Species = 0

        class Inner(EmptyCompartment):
            A: Species = 0

    class ExtendedInner(Outer):
        """Inherits Outer and extends inner."""

        class Inner(Outer.Inner):
            B: Species = 1

    class ExtendedInner2(EmptyCompartment):
        """Non-inherited Outer and extends inner.

        As inner has no links to Outer, it can be extracted.
        """

        A: Species = 0

        class Inner(Outer.Inner):
            B: Species = 1

    class ExpectedInner(EmptyCompartment):
        A: Species = 0

        class Inner(EmptyCompartment):
            A: Species = 0
            B: Species = 1

    assert ExtendedInner == ExpectedInner


def test_collision():
    class Outer(EmptyCompartment):
        A: Species = 0

        class Inner(EmptyCompartment):
            A: Species = 0

    with raises(ValueError):

        class Collision(Outer):
            """Inner Compartment collides with inherited Inner."""

            class Inner(EmptyCompartment):
                B: Species = 0


def test_override():
    class Outer(EmptyCompartment):
        A: Species = 0
        k: Parameter = 0

        class Inner(EmptyCompartment):
            A: Species = 0
            k: Parameter = 0

    class OverridenOuter(Outer):
        A: Species[Override] = 1

        class Inner(Outer.Inner):
            A: Species[Override] = 1

    class ExpectedOuter(EmptyCompartment):
        A: Species = 1
        k: Parameter = 0

        class Inner(EmptyCompartment):
            A: Species = 1
            k: Parameter = 0

    assert OverridenOuter == ExpectedOuter


def test_combine():
    class ModelA(EmptyCompartment):
        class InnerA(EmptyCompartment):
            A: Species = 0

        class InnerC(EmptyCompartment):
            A: Species = 0
            C: Species = 0

    class ModelB(EmptyCompartment):
        class InnerB(EmptyCompartment):
            B: Species = 0

        class InnerC(EmptyCompartment):
            B: Species = 0
            C: Species = 0

    class Joint(ModelA, ModelB):
        """Implicitly, there is a merge between
        ModelA.InnerC and ModelB.InnerC"""

        pass

    class Expected(EmptyCompartment):
        class InnerA(EmptyCompartment):
            A: Species = 0

        class InnerB(EmptyCompartment):
            B: Species = 0

        class InnerC(EmptyCompartment):
            A: Species = 0
            B: Species = 0
            C: Species = 0

    assert Joint == Expected
