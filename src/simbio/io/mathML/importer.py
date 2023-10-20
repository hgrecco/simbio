import functools
import keyword
from collections import ChainMap

import libsbml
from libsbml import ASTNode
from symbolite import Symbol, abstract, scalar
from symbolite.abstract import symbol
from symbolite.core import as_function

from .symbol import MathMLSpecialSymbol, MathMLSymbol


def as_symbol(node: libsbml.ASTNode):
    return MathMLSymbol(node.getName())


def as_special_symbol(node: libsbml.ASTNode):
    return MathMLSpecialSymbol(node.getName())


def get_value(cast_to: type):
    def getter(x: ASTNode):
        value = x.getValue()
        return cast_to(value)

    return getter


def minus(*args):
    if len(args) == 1:
        return symbol.neg(*args)
    elif len(args) == 2:
        return symbol.sub(*args)
    else:
        raise TypeError("Received AST_MINUS with more than 2 children.")


def root(*args):
    match args:
        case (arg,) | (2, arg):
            return scalar.sqrt(arg)
        case (exp, arg):
            return scalar.pow(arg, symbol.truediv(1, exp))
        case _:
            raise TypeError(f"unexpected number of arguments: {len(args)}")


def log(*args):
    match args:
        case (10, x) | (x,):
            return scalar.log10(x)
        case _:
            raise TypeError(f"unexpected arguments for log: {args}")


def reduced(func):
    def impl(*args):
        return functools.reduce(func, args)

    return impl


mapper = {
    libsbml.AST_PLUS: symbol.add,
    libsbml.AST_MINUS: minus,
    libsbml.AST_TIMES: symbol.mul,
    libsbml.AST_DIVIDE: symbol.truediv,
    libsbml.AST_POWER: symbol.pow,
    libsbml.AST_INTEGER: get_value(int),
    libsbml.AST_REAL: get_value(float),
    libsbml.AST_REAL_E: get_value(float),
    libsbml.AST_RATIONAL: "AST_RATIONAL",
    libsbml.AST_NAME: as_symbol,
    libsbml.AST_NAME_AVOGADRO: "AST_NAME_AVOGADRO",
    libsbml.AST_NAME_TIME: as_special_symbol,
    libsbml.AST_CONSTANT_E: scalar.e,
    libsbml.AST_CONSTANT_FALSE: False,
    libsbml.AST_CONSTANT_PI: scalar.pi,
    libsbml.AST_CONSTANT_TRUE: True,
    libsbml.AST_LAMBDA: "AST_LAMBDA",
    libsbml.AST_FUNCTION: "AST_FUNCTION",
    libsbml.AST_FUNCTION_ABS: scalar.abs,
    libsbml.AST_FUNCTION_ARCCOS: scalar.acos,
    libsbml.AST_FUNCTION_ARCCOSH: scalar.acosh,
    libsbml.AST_FUNCTION_ARCCOT: "AST_FUNCTION_ARCCOT",
    libsbml.AST_FUNCTION_ARCCOTH: "AST_FUNCTION_ARCCOTH",
    libsbml.AST_FUNCTION_ARCCSC: "AST_FUNCTION_ARCCSC",
    libsbml.AST_FUNCTION_ARCCSCH: "AST_FUNCTION_ARCCSCH",
    libsbml.AST_FUNCTION_ARCSEC: "AST_FUNCTION_ARCSEC",
    libsbml.AST_FUNCTION_ARCSECH: "AST_FUNCTION_ARCSECH",
    libsbml.AST_FUNCTION_ARCSIN: scalar.asin,
    libsbml.AST_FUNCTION_ARCSINH: scalar.asinh,
    libsbml.AST_FUNCTION_ARCTAN: scalar.atan,
    libsbml.AST_FUNCTION_ARCTANH: scalar.atanh,
    libsbml.AST_FUNCTION_CEILING: scalar.ceil,
    libsbml.AST_FUNCTION_COS: scalar.cos,
    libsbml.AST_FUNCTION_COSH: scalar.cosh,
    libsbml.AST_FUNCTION_COT: "AST_FUNCTION_COT",
    libsbml.AST_FUNCTION_COTH: "AST_FUNCTION_COTH",
    libsbml.AST_FUNCTION_CSC: "AST_FUNCTION_CSC",
    libsbml.AST_FUNCTION_CSCH: "AST_FUNCTION_CSCH",
    libsbml.AST_FUNCTION_DELAY: "AST_FUNCTION_DELAY",
    libsbml.AST_FUNCTION_EXP: scalar.exp,
    libsbml.AST_FUNCTION_FACTORIAL: scalar.factorial,
    libsbml.AST_FUNCTION_FLOOR: scalar.floor,
    libsbml.AST_FUNCTION_LN: scalar.log,
    libsbml.AST_FUNCTION_LOG: log,
    libsbml.AST_FUNCTION_PIECEWISE: "AST_FUNCTION_PIECEWISE",
    libsbml.AST_FUNCTION_POWER: symbol.pow,
    libsbml.AST_FUNCTION_ROOT: root,
    libsbml.AST_FUNCTION_SEC: "AST_FUNCTION_SEC",
    libsbml.AST_FUNCTION_SECH: "AST_FUNCTION_SECH",
    libsbml.AST_FUNCTION_SIN: scalar.sin,
    libsbml.AST_FUNCTION_SINH: scalar.sinh,
    libsbml.AST_FUNCTION_TAN: scalar.tan,
    libsbml.AST_FUNCTION_TANH: scalar.tanh,
    libsbml.AST_LOGICAL_AND: reduced(symbol.and_),
    libsbml.AST_LOGICAL_NOT: symbol.invert,
    libsbml.AST_LOGICAL_OR: reduced(symbol.or_),
    libsbml.AST_LOGICAL_XOR: symbol.xor,
    libsbml.AST_RELATIONAL_EQ: reduced(symbol.eq),
    libsbml.AST_RELATIONAL_GEQ: symbol.ge,
    libsbml.AST_RELATIONAL_GT: symbol.gt,
    libsbml.AST_RELATIONAL_LEQ: symbol.le,
    libsbml.AST_RELATIONAL_LT: symbol.lt,
    libsbml.AST_RELATIONAL_NEQ: reduced(symbol.ne),
    libsbml.AST_END_OF_CORE: "AST_END_OF_CORE",
    libsbml.AST_FUNCTION_MAX: "AST_FUNCTION_MAX",
    libsbml.AST_FUNCTION_MIN: "AST_FUNCTION_MIN",
    libsbml.AST_FUNCTION_QUOTIENT: "AST_FUNCTION_QUOTIENT",
    libsbml.AST_FUNCTION_RATE_OF: "AST_FUNCTION_RATE_OF",
    libsbml.AST_FUNCTION_REM: "AST_FUNCTION_REM",
    libsbml.AST_LOGICAL_IMPLIES: "AST_LOGICAL_IMPLIES",
    libsbml.AST_CSYMBOL_FUNCTION: "AST_CSYMBOL_FUNCTION",
    libsbml.AST_DISTRIB_FUNCTION_NORMAL: "AST_DISTRIB_FUNCTION_NORMAL",
    libsbml.AST_DISTRIB_FUNCTION_UNIFORM: "AST_DISTRIB_FUNCTION_UNIFORM",
    libsbml.AST_DISTRIB_FUNCTION_BERNOULLI: "AST_DISTRIB_FUNCTION_BERNOULLI",
    libsbml.AST_DISTRIB_FUNCTION_BINOMIAL: "AST_DISTRIB_FUNCTION_BINOMIAL",
    libsbml.AST_DISTRIB_FUNCTION_CAUCHY: "AST_DISTRIB_FUNCTION_CAUCHY",
    libsbml.AST_DISTRIB_FUNCTION_CHISQUARE: "AST_DISTRIB_FUNCTION_CHISQUARE",
    libsbml.AST_DISTRIB_FUNCTION_EXPONENTIAL: "AST_DISTRIB_FUNCTION_EXPONENTIAL",
    libsbml.AST_DISTRIB_FUNCTION_GAMMA: "AST_DISTRIB_FUNCTION_GAMMA",
    libsbml.AST_DISTRIB_FUNCTION_LAPLACE: "AST_DISTRIB_FUNCTION_LAPLACE",
    libsbml.AST_DISTRIB_FUNCTION_LOGNORMAL: "AST_DISTRIB_FUNCTION_LOGNORMAL",
    libsbml.AST_DISTRIB_FUNCTION_POISSON: "AST_DISTRIB_FUNCTION_POISSON",
    libsbml.AST_DISTRIB_FUNCTION_RAYLEIGH: "AST_DISTRIB_FUNCTION_RAYLEIGH",
    libsbml.AST_LINEAR_ALGEBRA_VECTOR: "AST_LINEAR_ALGEBRA_VECTOR",
    libsbml.AST_LINEAR_ALGEBRA_SELECTOR: "AST_LINEAR_ALGEBRA_SELECTOR",
    libsbml.AST_LINEAR_ALGEBRA_MATRIX: "AST_LINEAR_ALGEBRA_MATRIX",
    libsbml.AST_LINEAR_ALGEBRA_MATRIXROW: "AST_LINEAR_ALGEBRA_MATRIXROW",
    libsbml.AST_LINEAR_ALGEBRA_DETERMINANT: "AST_LINEAR_ALGEBRA_DETERMINANT",
    libsbml.AST_LINEAR_ALGEBRA_TRANSPOSE: "AST_LINEAR_ALGEBRA_TRANSPOSE",
    libsbml.AST_LINEAR_ALGEBRA_VECTOR_PRODUCT: "AST_LINEAR_ALGEBRA_VECTOR_PRODUCT",
    libsbml.AST_LINEAR_ALGEBRA_SCALAR_PRODUCT: "AST_LINEAR_ALGEBRA_SCALAR_PRODUCT",
    libsbml.AST_LINEAR_ALGEBRA_OUTER_PRODUCT: "AST_LINEAR_ALGEBRA_OUTER_PRODUCT",
    libsbml.AST_LOGICAL_EXISTS: "AST_LOGICAL_EXISTS",
    libsbml.AST_LOGICAL_FORALL: "AST_LOGICAL_FORALL",
    libsbml.AST_STATISTICS_MEAN: "AST_STATISTICS_MEAN",
    libsbml.AST_STATISTICS_MEDIAN: "AST_STATISTICS_MEDIAN",
    libsbml.AST_STATISTICS_MODE: "AST_STATISTICS_MODE",
    libsbml.AST_STATISTICS_MOMENT: "AST_STATISTICS_MOMENT",
    libsbml.AST_STATISTICS_SDEV: "AST_STATISTICS_SDEV",
    libsbml.AST_STATISTICS_VARIANCE: "AST_STATISTICS_VARIANCE",
    libsbml.AST_STATISTICS_MOMENTABOUT: "AST_STATISTICS_MOMENTABOUT",
    libsbml.AST_SERIES_PRODUCT: "AST_SERIES_PRODUCT",
    libsbml.AST_SERIES_SUM: "AST_SERIES_SUM",
    libsbml.AST_SERIES_LIMIT: "AST_SERIES_LIMIT",
    libsbml.AST_SERIES_TENDSTO: "AST_SERIES_TENDSTO",
    libsbml.AST_ALGEBRA_GCD: "AST_ALGEBRA_GCD",
    libsbml.AST_ALGEBRA_CONJUGATE: "AST_ALGEBRA_CONJUGATE",
    libsbml.AST_ALGEBRA_ARG: "AST_ALGEBRA_ARG",
    libsbml.AST_ALGEBRA_REAL: "AST_ALGEBRA_REAL",
    libsbml.AST_ALGEBRA_IMAGINARY: "AST_ALGEBRA_IMAGINARY",
    libsbml.AST_ALGEBRA_LCM: "AST_ALGEBRA_LCM",
    libsbml.AST_RELATIONS_EQUIVALENT: "AST_RELATIONS_EQUIVALENT",
    libsbml.AST_RELATIONS_APPROX: "AST_RELATIONS_APPROX",
    libsbml.AST_RELATIONS_FACTOROF: "AST_RELATIONS_FACTOROF",
    libsbml.AST_CALCULUS_INT: "AST_CALCULUS_INT",
    libsbml.AST_CALCULUS_DIFF: "AST_CALCULUS_DIFF",
    libsbml.AST_CALCULUS_PARTIALDIFF: "AST_CALCULUS_PARTIALDIFF",
    libsbml.AST_CALCULUS_LOWLIMIT: "AST_CALCULUS_LOWLIMIT",
    libsbml.AST_CALCULUS_UPLIMIT: "AST_CALCULUS_UPLIMIT",
    libsbml.AST_CALCULUS_DIVERGENCE: "AST_CALCULUS_DIVERGENCE",
    libsbml.AST_CALCULUS_GRAD: "AST_CALCULUS_GRAD",
    libsbml.AST_CALCULUS_CURL: "AST_CALCULUS_CURL",
    libsbml.AST_CALCULUS_LAPLACIAN: "AST_CALCULUS_LAPLACIAN",
    libsbml.AST_SET_THEORY_SET: "AST_SET_THEORY_SET",
    libsbml.AST_SET_THEORY_LIST: "AST_SET_THEORY_LIST",
    libsbml.AST_SET_THEORY_UNION: "AST_SET_THEORY_UNION",
    libsbml.AST_SET_THEORY_INTERSECT: "AST_SET_THEORY_INTERSECT",
    libsbml.AST_SET_THEORY_IN: "AST_SET_THEORY_IN",
    libsbml.AST_SET_THEORY_NOTIN: "AST_SET_THEORY_NOTIN",
    libsbml.AST_SET_THEORY_SUBSET: "AST_SET_THEORY_SUBSET",
    libsbml.AST_SET_THEORY_PRSUBSET: "AST_SET_THEORY_PRSUBSET",
    libsbml.AST_SET_THEORY_NOTSUBSET: "AST_SET_THEORY_NOTSUBSET",
    libsbml.AST_SET_THEORY_NOTPRSUBSET: "AST_SET_THEORY_NOTPRSUBSET",
    libsbml.AST_SET_THEORY_SETDIFF: "AST_SET_THEORY_SETDIFF",
    libsbml.AST_SET_THEORY_CARD: "AST_SET_THEORY_CARD",
    libsbml.AST_SET_THEORY_CARTESIANPRODUCT: "AST_SET_THEORY_CARTESIANPRODUCT",
    libsbml.AST_CONSTANT_IMAGINARYI: "AST_CONSTANT_IMAGINARYI",
    libsbml.AST_CONSTANTS_INTEGERS: "AST_CONSTANTS_INTEGERS",
    libsbml.AST_CONSTANTS_REALS: "AST_CONSTANTS_REALS",
    libsbml.AST_CONSTANTS_RATIONALS: "AST_CONSTANTS_RATIONALS",
    libsbml.AST_CONSTANTS_NATURALNUMBERS: "AST_CONSTANTS_NATURALNUMBERS",
    libsbml.AST_CONSTANTS_COMPLEXES: "AST_CONSTANTS_COMPLEXES",
    libsbml.AST_CONSTANTS_PRIMES: "AST_CONSTANTS_PRIMES",
    libsbml.AST_CONSTANTS_EMPTYSET: "AST_CONSTANTS_EMPTYSET",
    libsbml.AST_CONSTANTS_EULERGAMMA: "AST_CONSTANTS_EULERGAMMA",
    libsbml.AST_BASIC_CONTENT_INTERVAL: "AST_BASIC_CONTENT_INTERVAL",
    libsbml.AST_BASIC_CONTENT_INVERSE: "AST_BASIC_CONTENT_INVERSE",
    libsbml.AST_BASIC_CONTENT_CONDITION: "AST_BASIC_CONTENT_CONDITION",
    libsbml.AST_BASIC_CONTENT_DECLARE: "AST_BASIC_CONTENT_DECLARE",
    libsbml.AST_BASIC_CONTENT_COMPOSE: "AST_BASIC_CONTENT_COMPOSE",
    libsbml.AST_BASIC_CONTENT_IDENT: "AST_BASIC_CONTENT_IDENT",
    libsbml.AST_BASIC_CONTENT_DOMAIN: "AST_BASIC_CONTENT_DOMAIN",
    libsbml.AST_BASIC_CONTENT_CODOMAIN: "AST_BASIC_CONTENT_CODOMAIN",
    libsbml.AST_BASIC_CONTENT_IMAGE: "AST_BASIC_CONTENT_IMAGE",
    libsbml.AST_BASIC_CONTENT_DOMAINOFAPPLICATION: "AST_BASIC_CONTENT_DOMAINOFAPPLICATION",
    libsbml.AST_UNKNOWN: "AST_UNKNOWN",
}


class mathMLImporter:
    def __init__(self) -> None:
        self.mapper = ChainMap({}, mapper)

    def convert(self, node: libsbml.ASTNode):
        func = self.mapper[node.getType()]
        if isinstance(func, str):
            raise NotImplementedError(func)
        elif isinstance(func, dict):
            func = func[node.getName()]

        if node.getNumChildren() > 0:
            return func(*self.yield_children(node))
        elif callable(func):
            return func(node)
        else:
            return func

    def yield_children(self, node: libsbml.ASTNode) -> Symbol:
        for i in range(node.getNumChildren()):
            yield self.convert(node.getChild(i))

    def compile_function(self, func_name: str, node: libsbml.ASTNode):
        *params, body = self.yield_children(node)

        if any(keyword.iskeyword(p.name) for p in params):
            name_mapping = {p.name: p for p in params}
            for name in filter(keyword.iskeyword, name_mapping):
                new_name = name
                while new_name in name_mapping:
                    new_name = f"_{new_name}"
                name_mapping[name] = Symbol(new_name)
            params = name_mapping.values()
            body = body.subs_by_name(**name_mapping)

        func = as_function(body, func_name, tuple(map(str, params)), libsl=abstract)
        self.add_function(func_name, func)
        return func

    def add_function(self, name: str, func):
        if self.mapper[libsbml.AST_FUNCTION] == "AST_FUNCTION":
            self.mapper[libsbml.AST_FUNCTION] = {}

        self.mapper[libsbml.AST_FUNCTION][name] = func
