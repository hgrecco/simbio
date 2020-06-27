from simbio import Parameter, Reactant
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
