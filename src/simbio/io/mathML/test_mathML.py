from pytest import mark
from symbolite import scalar

from . import mathMLImporter, to_mathML
from .symbol import MathMLSymbol as Symbol


@mark.parametrize(
    "expr",
    [
        1,
        Symbol("x"),
        Symbol("x") * Symbol("y"),
        Symbol("x") + Symbol("y"),
        Symbol("x") * 2,
        2 * Symbol("x"),
        2 * Symbol("x") + Symbol("y"),
        Symbol("x") ** 2,
        Symbol("x") ** 0.5,
        scalar.cos(Symbol("x")),
        scalar.sqrt(Symbol("x")),
    ],
)
def test_mathML_roundtrip(expr: Symbol):
    node = to_mathML(expr)
    expr2 = mathMLImporter().convert(node)
    assert expr2 == expr
