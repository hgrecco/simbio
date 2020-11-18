from simbio import Compartment
from simbio.compartments import DuplicateComponentError
from simbio.components import Parameter, ReactionBalance, Species
from simbio.reactions import Synthesis
from simbio.reactions.core import Reaction, SingleReaction
from ward import raises, test, xfail


@test("rate: correctly defined")
def _():
    class Reaction1(SingleReaction):
        A: Species
        p: Parameter

        def reaction_balance(self) -> ReactionBalance:
            return self.A >> None

        @staticmethod
        def reaction_rate(t, A, p):
            pass

    class Reaction2(SingleReaction):
        A: Species
        p: Parameter

        def reaction_balance(self) -> ReactionBalance:
            return None >> self.A

        @staticmethod
        def reaction_rate(t, p):
            pass

    class Reaction3(SingleReaction):
        A: Species
        B: Species
        p: Parameter

        def reaction_balance(self) -> ReactionBalance:
            return self.A >> self.B

        @staticmethod
        def reaction_rate(t, A, p):
            pass


@test("reactions: correctly defined")
def _():
    class Reaction1(Reaction):
        def reactions(self):
            pass


@test("rate: must be staticmethod")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            A: Species

            def reaction_balance(self) -> ReactionBalance:
                return None >> self.A

            def reaction_rate(t):
                pass

    with raises(TypeError):

        class Reaction2(SingleReaction):
            A: Species

            def reaction_balance(self) -> ReactionBalance:
                return None >> self.A

            @classmethod
            def reaction_rate(t):
                pass


@test("reactions: must take no parameters")
def _():
    with raises(ValueError):

        class Reaction1(Reaction):
            def reactions(self, A):
                pass


@test("rate: first parameter must be t")
def _():
    with raises(ValueError):

        class Reaction(SingleReaction):
            A: Species

            def reaction_balance(self) -> ReactionBalance:
                return self.A >> None

            @staticmethod
            def reaction_rate(A, t):
                pass


@test("rate: check unannotated parameter")
def _():
    with raises(ValueError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter

            def reaction_balance(self) -> ReactionBalance:
                return self.A >> None

            @staticmethod
            def reaction_rate(t, A, p, k):
                pass


@test("rate: check misannotated parameter")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter
            k: float

            def reaction_balance(self) -> ReactionBalance:
                return self.A >> None

            @staticmethod
            def reaction_rate(t, A, p, k):
                pass


@test("Reaction equivalence")
def _():
    class Reaction(SingleReaction):
        A: Species
        B: Species
        C: Species
        k: Parameter

        def reaction_balance(self) -> ReactionBalance:
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


@xfail("Not implemented yet. Will raise error on simulation.")
@test("Repeated reactant")
def _():
    A, B = (Species(0, name=name) for name in "AB")
    k = Parameter(0, name="k")

    with raises(DuplicateComponentError):

        Synthesis(A, A, B, k)
