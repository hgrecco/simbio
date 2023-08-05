from pytest import mark
from symbolite import Symbol, scalar

from . import from_mathML, mathMLExporter


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
    node = mathMLExporter().to_mathML(expr)
    expr2 = from_mathML(node)
    assert expr2 == expr
