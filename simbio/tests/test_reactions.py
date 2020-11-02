from simbio.parameters import Parameter, Species
from simbio.reactions.compound import CompoundReaction
from simbio.reactions.single import SingleReaction
from ward import raises, test


@test("rhs: correctly defined")
def _():
    class Reaction1(SingleReaction):
        A: Species
        B: Species
        p: Parameter

        @staticmethod
        def rhs(t, A, B, p):
            pass

    class Reaction2(SingleReaction):
        A: Species

        @staticmethod
        def rhs(t, A):
            pass


@test("yield_reactions: correctly defined")
def _():
    class Reaction1(CompoundReaction):
        def yield_reactions(self):
            pass


@test("rhs: must be staticmethod")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            def rhs(t):
                pass

    with raises(TypeError):

        class Reaction2(SingleReaction):
            @classmethod
            def rhs(t):
                pass


@test("yield_reactions: must take no parameters")
def _():
    with raises(ValueError):

        class Reaction1(CompoundReaction):
            def yield_reactions(self, A):
                pass


@test("rhs: first parameter must be t")
def _():
    with raises(ValueError):

        class Reaction(SingleReaction):
            A: Species

            @staticmethod
            def rhs(A, t):
                pass


@test("rhs: check unannotated parameter")
def _():
    with raises(ValueError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter

            @staticmethod
            def rhs(t, A, p, k):
                pass


@test("rhs: check misannotated parameter")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter
            k: float

            @staticmethod
            def rhs(t, A, p, k):
                pass


@test("Reaction equivalence")
def _():
    class Reaction(SingleReaction):
        A: Species
        B: Species
        C: Species
        k: Parameter

        _equivalent_species = ("A", "B"), ("C")

        @staticmethod
        def rhs(t, A, B, C, k):
            pass

    A, B, C = (Species(0, name=name) for name in "ABC")
    k1, k2 = (Parameter(0, name=name) for name in ("k1", "k2"))

    reaction = Reaction(A=A, B=B, C=C, k=k1)
    equivalent = (Reaction(A=A, B=B, C=C, k=k2), Reaction(A=B, B=A, C=C, k=k1))
    non_equivalent = Reaction(A=A, B=C, C=B, k=k1), Reaction(A=C, B=B, C=A, k=k1)

    for r in equivalent:
        assert hash(r) == hash(reaction)
        assert r == reaction

    for r in non_equivalent:
        assert hash(r) != hash(reaction)
        assert r != reaction
