from pytest import raises, xfail

from simbio.components import Parameter, Species
from simbio.components.types import SingleReaction
from simbio.reactions.single import Synthesis


def test_reaction_equivlence():
    xfail("Not implemented")

    class Reaction(SingleReaction):
        A: Species
        B: Species
        C: Species
        k: Parameter

        def reaction_balance(self):
            return self.A + self.B >> self.C

        @staticmethod
        def reaction_rate(t, A, B, k):
            pass

    A, B, C = (Species(0, name=name) for name in "ABC")
    k1, k2 = (Parameter(0, name=name) for name in ("k1", "k2"))

    reaction = Reaction(A=A, B=B, C=C, k=k1)

    equal = Reaction(A=B, B=A, C=C, k=k1)
    equivalent = Reaction(A=A, B=B, C=C, k=k2)
    non_equivalent = Reaction(A=A, B=C, C=B, k=k1), Reaction(A=C, B=B, C=A, k=k1)

    assert hash(equal) == hash(reaction)
    assert equal == reaction

    assert equivalent != reaction
    assert reaction.equivalent(equivalent)

    for r in non_equivalent:
        assert r != reaction
        assert not reaction.equivalent(r)


def test_repeated_reactant():
    xfail("Not implemented")
    A, B = (Species(0, name=name) for name in "AB")
    k = Parameter(0, name="k")

    with raises(ValueError):
        Synthesis(A, A, B, k)
