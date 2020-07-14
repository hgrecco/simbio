from simbio.parameters import Parameter
from simbio.reactants import Reactant
from simbio.reactions.compound import CompoundReaction
from simbio.reactions.single import SingleReaction
from ward import raises, test


@test("rhs: correctly defined")
def _():
    class Reaction1(SingleReaction):
        @staticmethod
        def rhs(t, A: Reactant, B: Reactant, p: Parameter):
            pass

    class Reaction2(SingleReaction):
        @staticmethod
        def rhs(t, A: Reactant):
            pass


@test("yield_reactions: correctly defined")
def _():
    class Reaction1(CompoundReaction):
        @staticmethod
        def yield_reactions(A: Reactant, B: Reactant, p: Parameter):
            pass

    class Reaction2(CompoundReaction):
        @staticmethod
        def yield_reactions(A: Reactant):
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


@test("yield_reactions: must be staticmethod")
def _():
    with raises(TypeError):

        class Reaction1(CompoundReaction):
            def yield_reactions():
                pass

    with raises(TypeError):

        class Reaction2(CompoundReaction):
            @classmethod
            def yield_reactions():
                pass


@test("rhs: first parameter must be t")
def _():
    with raises(TypeError):

        class Reaction(SingleReaction):
            @staticmethod
            def rhs(A, t):
                pass


@test("rhs: check parameter order")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            @staticmethod
            def rhs(t, p: Parameter, A: Reactant, B: Reactant):
                pass

    with raises(TypeError):

        class Reaction2(SingleReaction):
            @staticmethod
            def rhs(t, A: Reactant, p: Parameter, B: Reactant):
                pass


@test("yield_reactions: check parameter order")
def _():
    with raises(TypeError):

        class Reaction1(CompoundReaction):
            @staticmethod
            def yield_reactions(p: Parameter, A: Reactant, B: Reactant):
                pass

    with raises(TypeError):

        class Reaction2(CompoundReaction):
            @staticmethod
            def yield_reactions(A: Reactant, p: Parameter, B: Reactant):
                pass


@test("rhs: check unannotated parameter")
def _():
    with raises(TypeError):

        class Reaction1(SingleReaction):
            @staticmethod
            def rhs(t, A: Reactant, k, p: Parameter):
                pass

    with raises(TypeError):

        class Reaction2(SingleReaction):
            @staticmethod
            def rhs(t, A: Reactant, p: Parameter, k):
                pass


@test("yield_reactions: check unannotated parameter")
def _():
    with raises(TypeError):

        class Reaction1(CompoundReaction):
            @staticmethod
            def yield_reactions(A: Reactant, k, p: Parameter):
                pass

    with raises(TypeError):

        class Reaction2(CompoundReaction):
            @staticmethod
            def yield_reactions(A: Reactant, p: Parameter, k):
                pass

    with raises(TypeError):

        class Reaction3(CompoundReaction):
            @staticmethod
            def yield_reactions(t, A: Reactant, p: Parameter):
                pass
