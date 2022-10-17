from pytest import raises, xfail

from simbio.components import Parameter, Species
from simbio.components.types import SingleReaction


def test_reaction_rate():
    class Reaction1(SingleReaction):
        A: Species
        p: Parameter

        @property
        def reactants(self):
            return (self.A,)

        @property
        def products(self):
            return ()

        @staticmethod
        def reaction_rate(t, A, p):
            pass

    class Reaction2(SingleReaction):
        A: Species
        p: Parameter

        @property
        def reactants(self):
            return ()

        @property
        def products(self):
            return (self.A,)

        @staticmethod
        def reaction_rate(t, p):
            pass

    class Reaction3(SingleReaction):
        A: Species
        B: Species
        p: Parameter

        @property
        def reactants(self):
            return (self.A,)

        @property
        def products(self):
            return (self.B,)

        @staticmethod
        def reaction_rate(t, A, p):
            pass


def test_rate_is_staticmethod():
    xfail("Not implemented")
    with raises(TypeError):

        class Reaction1(SingleReaction):
            A: Species

            @property
            def reactants(self):
                return ()

            @property
            def products(self):
                return (self.A,)

            def reaction_rate(t):
                pass

    with raises(TypeError):

        class Reaction2(SingleReaction):
            A: Species

            @property
            def reactants(self):
                return ()

            @property
            def products(self):
                return (self.A,)

            @classmethod
            def reaction_rate(t):
                pass


def test_t_as_first_parameter():
    xfail("Not implemented")
    with raises(ValueError):

        class Reaction(SingleReaction):
            A: Species

            @property
            def reactants(self):
                return (self.A,)

            @property
            def products(self):
                return ()

            @staticmethod
            def reaction_rate(A, t):
                pass


def test_unannotated_parameter():
    xfail("Not implemented")
    with raises(ValueError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter

            @property
            def reactants(self):
                return (self.A,)

            @property
            def products(self):
                return ()

            @staticmethod
            def reaction_rate(t, A, p, k):
                pass


def test_misannotated_parameter():
    xfail("Not implemented")
    with raises(TypeError):

        class Reaction1(SingleReaction):
            A: Species
            p: Parameter
            k: float

            @property
            def reactants(self):
                return (self.A,)

            @property
            def products(self):
                return ()

            @staticmethod
            def reaction_rate(t, A, p, k):
                pass
