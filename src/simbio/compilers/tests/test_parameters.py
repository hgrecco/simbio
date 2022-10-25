from ...components import EmptyCompartment, Parameter
from ...reactions.single import Creation
from ..core import Compiler


class Compiler(Compiler):
    def _build_reaction_ip_rhs(self, full_name: str, reaction) -> callable:
        raise RuntimeError


class Model(EmptyCompartment):
    k: Parameter = 1
    r1 = Creation(A=0, rate=k)
    r2 = Creation(A=0, rate=k)


def test_resolve():
    y0, p = Compiler(Model).build_value_vectors()
    assert p.to_dict() == {
        "k": 1,
        "r1.rate": 1,
        "r2.rate": 1,
    }


def test_resolve_with_override_top():
    override = {"k": 2}
    y0, p = Compiler(Model).build_value_vectors(override)
    assert p.to_dict() == {
        "k": 2,
        "r1.rate": 2,
        "r2.rate": 2,
    }


def test_resolve_with_override_bottom():
    override = {"r1.rate": 2}
    y0, p = Compiler(Model).build_value_vectors(override)
    assert p.to_dict() == {
        "k": 1,
        "r1.rate": 2,
        "r2.rate": 1,
    }


def test_resolve_with_override_both():
    override = {"k": 2, "r1.rate": 3}
    y0, p = Compiler(Model).build_value_vectors(override)
    assert p.to_dict() == {
        "k": 2,
        "r1.rate": 3,
        "r2.rate": 2,
    }
