from simbio.model import Compartment, Parameter, Species
from simbio.reactions import Creation, Equilibration


class Outer(Compartment):
    """A multi-level model with a shared Parameter."""

    k: Parameter = 1
    A: Species = k
    create_A = Creation(A, k)

    class Inner(Compartment):
        k: Parameter
        A: Species = k  # noqa: F821
        create_A = Creation(A, k)  # noqa: F821

    equilibration = Equilibration(A, Inner.A, k, k)


def test_add_species():
    class ExtendedOuter(Outer):
        B: Species = 1

    assert ExtendedOuter > Outer

    class ExtendedInner(Outer):
        class Inner(Outer.Inner):
            B: Species = 1

    assert ExtendedInner > Outer


def test_override():
    class ExtendedOuter(Outer(A=2)):
        class Inner(Outer.Inner(A=3, k=4)):
            pass

    assert ExtendedOuter.k == Outer.k

    assert ExtendedOuter.A != Outer.A
    assert ExtendedOuter.Inner.A != Outer.Inner.A
    assert ExtendedOuter.Inner.k != Outer.Inner.k
