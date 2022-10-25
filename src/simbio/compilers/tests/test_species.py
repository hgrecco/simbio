from pytest import raises

from ...components import EmptyCompartment, Species
from ...reactions.single import Creation
from ..core import Compiler


class Compiler(Compiler):
    def _build_reaction_ip_rhs(self, full_name: str, reaction) -> callable:
        raise RuntimeError


class Model(EmptyCompartment):
    A: Species = 1
    r1 = Creation(A=A, rate=0)
    r2 = Creation(A=A, rate=0)
    r3 = Creation(A=3, rate=0)


compiler = Compiler(Model)


def test_number_of_species():
    assert len(compiler.species) == 2


def test_build_initial_conditions():
    y0, _ = compiler.build_value_vectors()
    assert y0.to_dict() == {"A": 1, "r3.A": 3}

    y0, _ = compiler.build_value_vectors({"A": 2, "r3.A": 4})
    assert y0.to_dict() == {"A": 2, "r3.A": 4}

    y0, _ = compiler.build_value_vectors({Model.A: 2, Model.r3.A: 4})
    assert y0.to_dict() == {"A": 2, "r3.A": 4}


def test_error_on_inexistent_species():
    with raises(ValueError):
        y0, _ = compiler.build_value_vectors({"r1.A": 1})

    with raises(ValueError):
        y0, _ = compiler.build_value_vectors({"inexistent": 1})
