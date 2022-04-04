from pytest import raises

from simbio.model import Compartment, Parameter, Species


def test_add_species():
    class Outer(Compartment):
        """Base model."""

        A: Species = 0

        class Inner(Compartment):
            A: Species = 0

    class ExtendedOuter(Outer):
        """Extends Outer and inherits inner."""

        B: Species = 1

    class ExpectedOuter(Compartment):
        A: Species = 0
        B: Species = 1

        class Inner(Compartment):
            A: Species = 0

    assert ExtendedOuter == ExpectedOuter

    class ExtendedInner(Outer):
        """Inherits Outer and extends inner."""

        class Inner(Outer.Inner):
            B: Species = 1

    class ExtendedInner2(Compartment):
        """Non-inherited Outer and extends inner.

        As inner has no links to Outer, it can be extracted.
        """

        A: Species = 0

        class Inner(Outer.Inner):
            B: Species = 1

    class ExpectedInner(Compartment):
        A: Species = 0

        class Inner(Compartment):
            A: Species = 0
            B: Species = 1

    assert ExtendedInner == ExpectedInner


def test_collision():
    class Outer(Compartment):
        A: Species = 0

        class Inner(Compartment):
            A: Species = 0

    with raises(NameError):

        class Collision(Outer):
            """Inner Compartment collides with inherited Inner."""

            class Inner(Compartment):
                B: Species = 0


def test_override():
    class Outer(Compartment):
        A: Species = 0
        k: Parameter = 0

        class Inner(Compartment):
            A: Species = 0
            k: Parameter = 0

    class OverridenOuter(Outer):
        A: Species.override = 1

        class Inner(Outer.Inner):
            A: Species.override = 1

    class ExpectedOuter(Compartment):
        A: Species = 1
        k: Parameter = 0

        class Inner(Compartment):
            A: Species = 1
            k: Parameter = 0

    assert OverridenOuter == ExpectedOuter


def test_combine():
    class ModelA(Compartment):
        class InnerA(Compartment):
            A: Species = 0

        class InnerC(Compartment):
            A: Species = 0
            C: Species = 0

    class ModelB(Compartment):
        class InnerB(Compartment):
            B: Species = 0

        class InnerC(Compartment):
            B: Species = 0
            C: Species = 0

    class Joint(ModelA, ModelB):
        """Implicitly, there is a merge between
        ModelA.InnerC and ModelB.InnerC"""

        pass

    class Expected(Compartment):
        class InnerA(Compartment):
            A: Species = 0

        class InnerB(Compartment):
            B: Species = 0

        class InnerC(Compartment):
            A: Species = 0
            B: Species = 0
            C: Species = 0

    assert Joint == Expected
