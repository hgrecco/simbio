from __future__ import annotations

from functools import partial, reduce
from typing import Iterator, Protocol

from symbolite import scalar
from symbolite.abstract import symbol

from .symbol import MathMLSpecialSymbol, MathMLSymbol


class Element(Protocol):
    @property
    def tag(self) -> str:
        ...

    @property
    def attrib(self) -> dict[str, str]:
        ...

    @property
    def text(self) -> str:
        ...

    def __iter__(self) -> Iterator[Element]:
        ...


def star_reduce(func, *args):
    return reduce(func, args)


tags = {
    "cn": MathMLSymbol,
    "ci": MathMLSpecialSymbol,
    "csymbol": MathMLSpecialSymbol,
    "sep": NotImplemented,
    "apply": NotImplemented,
    "piecewise": NotImplemented,
    "piece": NotImplemented,
    "otherwise": NotImplemented,
    "lambda": NotImplemented,
    "eq": symbol.eq,
    "neq": symbol.ne,
    "gt": symbol.gt,
    "lt": symbol.lt,
    "geq": symbol.ge,
    "leq": symbol.le,
    "plus": partial(star_reduce, symbol.add),
    "minus": partial(star_reduce, symbol.sub),
    "times": partial(star_reduce, symbol.mul),
    "divide": partial(star_reduce, symbol.truediv),
    "power": symbol.pow,
    "root": NotImplemented,
    "abs": scalar.abs,
    "exp": scalar.exp,
    "ln": scalar.log,
    "log": scalar.log10,
    "floor": scalar.floor,
    "ceiling": scalar.ceil,
    "factorial": scalar.factorial,
    "quotient": NotImplemented,
    "max": NotImplemented,
    "min": NotImplemented,
    "rem": symbol.mod,
    "and": partial(star_reduce, symbol.and_),
    "or": partial(star_reduce, symbol.or_),
    "xor": symbol.xor,
    "not": symbol.invert,
    "implies": NotImplemented,
    "degree": NotImplemented,
    "bvar": NotImplemented,
    "logbase": NotImplemented,
    "sin": scalar.sin,
    "cos": scalar.cos,
    "tan": scalar.tan,
    "sec": NotImplemented,
    "csc": NotImplemented,
    "cot": NotImplemented,
    "sinh": scalar.sinh,
    "cosh": scalar.cosh,
    "tanh": scalar.tanh,
    "sech": NotImplemented,
    "csch": NotImplemented,
    "coth": NotImplemented,
    "arcsin": scalar.asin,
    "arccos": scalar.acos,
    "arctan": scalar.atan,
    "arcsec": NotImplemented,
    "arccsc": NotImplemented,
    "arccot": NotImplemented,
    "arcsinh": scalar.asinh,
    "arccosh": scalar.acosh,
    "arctanh": scalar.atanh,
    "arcsech": NotImplemented,
    "arccsch": NotImplemented,
    "arccoth": NotImplemented,
    "true": True,
    "false": False,
    "notanumber": scalar.nan,
    "pi": scalar.pi,
    "infinity": scalar.inf,
    "exponentiale": scalar.e,
    "semantics": NotImplemented,
    "annotation": NotImplemented,
    "annotation-xml": NotImplemented,
    "math": lambda x: x,
}

ns_map = {"http://www.w3.org/1998/Math/MathML": tags}


def from_element(element: Element) -> symbol.Symbol:
    result = parse(element)
    if isinstance(result, list) and len(result) == 1:
        return result[0]
    raise RuntimeError("unexpected result when parsing mathML")


def _namespace_and_tag(x: str) -> tuple[str, str]:
    if x.startswith("{"):
        ns, _, tag = x[1:].partition("}")
        return ns, tag
    else:
        return "", x


def parse(element: Element):
    ns, tag = _namespace_and_tag(element.tag)
    cls = ns_map[ns][tag]

    if tag == "apply":
        func, *children = (parse(child) for child in element)
        return func(*children)

    children = [parse(child) for child in element]
    if len(children) > 0:
        return children
    elif (text := element.text) is not None:
        return cls(text.strip())
    else:
        return cls
