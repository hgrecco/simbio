from pytest import mark
from symbolite import scalar

from . import mathMLImporter, to_mathML
from .symbol import MathMLSymbol as Symbol

x, y = map(Symbol, ["x", "y"])


@mark.parametrize(
    "expr",
    [
        1,
        x,
        x * y,
        x + y,
        x * 2,
        2 * x,
        2 * x + y,
        x**2,
        x**0.5,
        scalar.cos(x),
        scalar.sqrt(x),
        x < 1,
        x < y,
        ~x,
    ],
)
def test_mathML_roundtrip(expr: Symbol):
    node = to_mathML(expr)
    expr2 = mathMLImporter().convert(node)
    assert expr2 == expr
