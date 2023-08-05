from functools import singledispatchmethod as dispatch
from typing import Any, Callable

import libsbml
from symbolite import Function, Symbol, scalar
from symbolite.abstract import symbol

mapper: dict[Function, int] = {
    symbol.add: libsbml.AST_PLUS,
    symbol.sub: libsbml.AST_MINUS,
    symbol.neg: libsbml.AST_MINUS,
    symbol.mul: libsbml.AST_TIMES,
    symbol.truediv: libsbml.AST_DIVIDE,
    symbol.pow: libsbml.AST_POWER,
    "libsbml.AST_INTEGER": libsbml.AST_INTEGER,
    "libsbml.AST_REAL": libsbml.AST_REAL,
    "libsbml.AST_REAL_E": libsbml.AST_REAL_E,
    "AST_RATIONAL": libsbml.AST_RATIONAL,
    "libsbml.AST_NAME": libsbml.AST_NAME,
    "AST_NAME_AVOGADRO": libsbml.AST_NAME_AVOGADRO,
    "libsbml.AST_NAME_TIME": libsbml.AST_NAME_TIME,
    scalar.e: libsbml.AST_CONSTANT_E,
    False: libsbml.AST_CONSTANT_FALSE,
    scalar.pi: libsbml.AST_CONSTANT_PI,
    True: libsbml.AST_CONSTANT_TRUE,
    "AST_LAMBDA": libsbml.AST_LAMBDA,
    "AST_FUNCTION": libsbml.AST_FUNCTION,
    scalar.abs: libsbml.AST_FUNCTION_ABS,
    scalar.acos: libsbml.AST_FUNCTION_ARCCOS,
    scalar.acosh: libsbml.AST_FUNCTION_ARCCOSH,
    "AST_FUNCTION_ARCCOT": libsbml.AST_FUNCTION_ARCCOT,
    "AST_FUNCTION_ARCCOTH": libsbml.AST_FUNCTION_ARCCOTH,
    "AST_FUNCTION_ARCCSC": libsbml.AST_FUNCTION_ARCCSC,
    "AST_FUNCTION_ARCCSCH": libsbml.AST_FUNCTION_ARCCSCH,
    "AST_FUNCTION_ARCSEC": libsbml.AST_FUNCTION_ARCSEC,
    "AST_FUNCTION_ARCSECH": libsbml.AST_FUNCTION_ARCSECH,
    scalar.asin: libsbml.AST_FUNCTION_ARCSIN,
    scalar.asinh: libsbml.AST_FUNCTION_ARCSINH,
    scalar.atan: libsbml.AST_FUNCTION_ARCTAN,
    scalar.atanh: libsbml.AST_FUNCTION_ARCTANH,
    scalar.ceil: libsbml.AST_FUNCTION_CEILING,
    scalar.cos: libsbml.AST_FUNCTION_COS,
    scalar.cosh: libsbml.AST_FUNCTION_COSH,
    "AST_FUNCTION_COT": libsbml.AST_FUNCTION_COT,
    "AST_FUNCTION_COTH": libsbml.AST_FUNCTION_COTH,
    "AST_FUNCTION_CSC": libsbml.AST_FUNCTION_CSC,
    "AST_FUNCTION_CSCH": libsbml.AST_FUNCTION_CSCH,
    "AST_FUNCTION_DELAY": libsbml.AST_FUNCTION_DELAY,
    scalar.exp: libsbml.AST_FUNCTION_EXP,
    scalar.factorial: libsbml.AST_FUNCTION_FACTORIAL,
    scalar.floor: libsbml.AST_FUNCTION_FLOOR,
    scalar.log: libsbml.AST_FUNCTION_LN,
    scalar.log10: libsbml.AST_FUNCTION_LOG,
    "AST_FUNCTION_PIECEWISE": libsbml.AST_FUNCTION_PIECEWISE,
    symbol.pow: libsbml.AST_FUNCTION_POWER,
    scalar.sqrt: libsbml.AST_FUNCTION_ROOT,
    "AST_FUNCTION_SEC": libsbml.AST_FUNCTION_SEC,
    "AST_FUNCTION_SECH": libsbml.AST_FUNCTION_SECH,
    scalar.sin: libsbml.AST_FUNCTION_SIN,
    scalar.sinh: libsbml.AST_FUNCTION_SINH,
    scalar.tan: libsbml.AST_FUNCTION_TAN,
    scalar.tanh: libsbml.AST_FUNCTION_TANH,
    symbol.and_: libsbml.AST_LOGICAL_AND,
    "AST_LOGICAL_NOT": libsbml.AST_LOGICAL_NOT,
    symbol.or_: libsbml.AST_LOGICAL_OR,
    "AST_LOGICAL_XOR": libsbml.AST_LOGICAL_XOR,
    symbol.eq: libsbml.AST_RELATIONAL_EQ,
    "AST_RELATIONAL_GEQ": libsbml.AST_RELATIONAL_GEQ,
    "AST_RELATIONAL_GT": libsbml.AST_RELATIONAL_GT,
    "AST_RELATIONAL_LEQ": libsbml.AST_RELATIONAL_LEQ,
    "AST_RELATIONAL_LT": libsbml.AST_RELATIONAL_LT,
    symbol.ne: libsbml.AST_RELATIONAL_NEQ,
    "AST_END_OF_CORE": libsbml.AST_END_OF_CORE,
    "AST_FUNCTION_MAX": libsbml.AST_FUNCTION_MAX,
    "AST_FUNCTION_MIN": libsbml.AST_FUNCTION_MIN,
    "AST_FUNCTION_QUOTIENT": libsbml.AST_FUNCTION_QUOTIENT,
    "AST_FUNCTION_RATE_OF": libsbml.AST_FUNCTION_RATE_OF,
    "AST_FUNCTION_REM": libsbml.AST_FUNCTION_REM,
    "AST_LOGICAL_IMPLIES": libsbml.AST_LOGICAL_IMPLIES,
    "AST_CSYMBOL_FUNCTION": libsbml.AST_CSYMBOL_FUNCTION,
    "AST_DISTRIB_FUNCTION_NORMAL": libsbml.AST_DISTRIB_FUNCTION_NORMAL,
    "AST_DISTRIB_FUNCTION_UNIFORM": libsbml.AST_DISTRIB_FUNCTION_UNIFORM,
    "AST_DISTRIB_FUNCTION_BERNOULLI": libsbml.AST_DISTRIB_FUNCTION_BERNOULLI,
    "AST_DISTRIB_FUNCTION_BINOMIAL": libsbml.AST_DISTRIB_FUNCTION_BINOMIAL,
    "AST_DISTRIB_FUNCTION_CAUCHY": libsbml.AST_DISTRIB_FUNCTION_CAUCHY,
    "AST_DISTRIB_FUNCTION_CHISQUARE": libsbml.AST_DISTRIB_FUNCTION_CHISQUARE,
    "AST_DISTRIB_FUNCTION_EXPONENTIAL": libsbml.AST_DISTRIB_FUNCTION_EXPONENTIAL,
    "AST_DISTRIB_FUNCTION_GAMMA": libsbml.AST_DISTRIB_FUNCTION_GAMMA,
    "AST_DISTRIB_FUNCTION_LAPLACE": libsbml.AST_DISTRIB_FUNCTION_LAPLACE,
    "AST_DISTRIB_FUNCTION_LOGNORMAL": libsbml.AST_DISTRIB_FUNCTION_LOGNORMAL,
    "AST_DISTRIB_FUNCTION_POISSON": libsbml.AST_DISTRIB_FUNCTION_POISSON,
    "AST_DISTRIB_FUNCTION_RAYLEIGH": libsbml.AST_DISTRIB_FUNCTION_RAYLEIGH,
    "AST_LINEAR_ALGEBRA_VECTOR": libsbml.AST_LINEAR_ALGEBRA_VECTOR,
    "AST_LINEAR_ALGEBRA_SELECTOR": libsbml.AST_LINEAR_ALGEBRA_SELECTOR,
    "AST_LINEAR_ALGEBRA_MATRIX": libsbml.AST_LINEAR_ALGEBRA_MATRIX,
    "AST_LINEAR_ALGEBRA_MATRIXROW": libsbml.AST_LINEAR_ALGEBRA_MATRIXROW,
    "AST_LINEAR_ALGEBRA_DETERMINANT": libsbml.AST_LINEAR_ALGEBRA_DETERMINANT,
    "AST_LINEAR_ALGEBRA_TRANSPOSE": libsbml.AST_LINEAR_ALGEBRA_TRANSPOSE,
    "AST_LINEAR_ALGEBRA_VECTOR_PRODUCT": libsbml.AST_LINEAR_ALGEBRA_VECTOR_PRODUCT,
    "AST_LINEAR_ALGEBRA_SCALAR_PRODUCT": libsbml.AST_LINEAR_ALGEBRA_SCALAR_PRODUCT,
    "AST_LINEAR_ALGEBRA_OUTER_PRODUCT": libsbml.AST_LINEAR_ALGEBRA_OUTER_PRODUCT,
    "AST_LOGICAL_EXISTS": libsbml.AST_LOGICAL_EXISTS,
    "AST_LOGICAL_FORALL": libsbml.AST_LOGICAL_FORALL,
    "AST_STATISTICS_MEAN": libsbml.AST_STATISTICS_MEAN,
    "AST_STATISTICS_MEDIAN": libsbml.AST_STATISTICS_MEDIAN,
    "AST_STATISTICS_MODE": libsbml.AST_STATISTICS_MODE,
    "AST_STATISTICS_MOMENT": libsbml.AST_STATISTICS_MOMENT,
    "AST_STATISTICS_SDEV": libsbml.AST_STATISTICS_SDEV,
    "AST_STATISTICS_VARIANCE": libsbml.AST_STATISTICS_VARIANCE,
    "AST_STATISTICS_MOMENTABOUT": libsbml.AST_STATISTICS_MOMENTABOUT,
    "AST_SERIES_PRODUCT": libsbml.AST_SERIES_PRODUCT,
    "AST_SERIES_SUM": libsbml.AST_SERIES_SUM,
    "AST_SERIES_LIMIT": libsbml.AST_SERIES_LIMIT,
    "AST_SERIES_TENDSTO": libsbml.AST_SERIES_TENDSTO,
    "AST_ALGEBRA_GCD": libsbml.AST_ALGEBRA_GCD,
    "AST_ALGEBRA_CONJUGATE": libsbml.AST_ALGEBRA_CONJUGATE,
    "AST_ALGEBRA_ARG": libsbml.AST_ALGEBRA_ARG,
    "AST_ALGEBRA_REAL": libsbml.AST_ALGEBRA_REAL,
    "AST_ALGEBRA_IMAGINARY": libsbml.AST_ALGEBRA_IMAGINARY,
    "AST_ALGEBRA_LCM": libsbml.AST_ALGEBRA_LCM,
    "AST_RELATIONS_EQUIVALENT": libsbml.AST_RELATIONS_EQUIVALENT,
    "AST_RELATIONS_APPROX": libsbml.AST_RELATIONS_APPROX,
    "AST_RELATIONS_FACTOROF": libsbml.AST_RELATIONS_FACTOROF,
    "AST_CALCULUS_INT": libsbml.AST_CALCULUS_INT,
    "AST_CALCULUS_DIFF": libsbml.AST_CALCULUS_DIFF,
    "AST_CALCULUS_PARTIALDIFF": libsbml.AST_CALCULUS_PARTIALDIFF,
    "AST_CALCULUS_LOWLIMIT": libsbml.AST_CALCULUS_LOWLIMIT,
    "AST_CALCULUS_UPLIMIT": libsbml.AST_CALCULUS_UPLIMIT,
    "AST_CALCULUS_DIVERGENCE": libsbml.AST_CALCULUS_DIVERGENCE,
    "AST_CALCULUS_GRAD": libsbml.AST_CALCULUS_GRAD,
    "AST_CALCULUS_CURL": libsbml.AST_CALCULUS_CURL,
    "AST_CALCULUS_LAPLACIAN": libsbml.AST_CALCULUS_LAPLACIAN,
    "AST_SET_THEORY_SET": libsbml.AST_SET_THEORY_SET,
    "AST_SET_THEORY_LIST": libsbml.AST_SET_THEORY_LIST,
    "AST_SET_THEORY_UNION": libsbml.AST_SET_THEORY_UNION,
    "AST_SET_THEORY_INTERSECT": libsbml.AST_SET_THEORY_INTERSECT,
    "AST_SET_THEORY_IN": libsbml.AST_SET_THEORY_IN,
    "AST_SET_THEORY_NOTIN": libsbml.AST_SET_THEORY_NOTIN,
    "AST_SET_THEORY_SUBSET": libsbml.AST_SET_THEORY_SUBSET,
    "AST_SET_THEORY_PRSUBSET": libsbml.AST_SET_THEORY_PRSUBSET,
    "AST_SET_THEORY_NOTSUBSET": libsbml.AST_SET_THEORY_NOTSUBSET,
    "AST_SET_THEORY_NOTPRSUBSET": libsbml.AST_SET_THEORY_NOTPRSUBSET,
    "AST_SET_THEORY_SETDIFF": libsbml.AST_SET_THEORY_SETDIFF,
    "AST_SET_THEORY_CARD": libsbml.AST_SET_THEORY_CARD,
    "AST_SET_THEORY_CARTESIANPRODUCT": libsbml.AST_SET_THEORY_CARTESIANPRODUCT,
    "AST_CONSTANT_IMAGINARYI": libsbml.AST_CONSTANT_IMAGINARYI,
    "AST_CONSTANTS_INTEGERS": libsbml.AST_CONSTANTS_INTEGERS,
    "AST_CONSTANTS_REALS": libsbml.AST_CONSTANTS_REALS,
    "AST_CONSTANTS_RATIONALS": libsbml.AST_CONSTANTS_RATIONALS,
    "AST_CONSTANTS_NATURALNUMBERS": libsbml.AST_CONSTANTS_NATURALNUMBERS,
    "AST_CONSTANTS_COMPLEXES": libsbml.AST_CONSTANTS_COMPLEXES,
    "AST_CONSTANTS_PRIMES": libsbml.AST_CONSTANTS_PRIMES,
    "AST_CONSTANTS_EMPTYSET": libsbml.AST_CONSTANTS_EMPTYSET,
    "AST_CONSTANTS_EULERGAMMA": libsbml.AST_CONSTANTS_EULERGAMMA,
    "AST_BASIC_CONTENT_INTERVAL": libsbml.AST_BASIC_CONTENT_INTERVAL,
    "AST_BASIC_CONTENT_INVERSE": libsbml.AST_BASIC_CONTENT_INVERSE,
    "AST_BASIC_CONTENT_CONDITION": libsbml.AST_BASIC_CONTENT_CONDITION,
    "AST_BASIC_CONTENT_DECLARE": libsbml.AST_BASIC_CONTENT_DECLARE,
    "AST_BASIC_CONTENT_COMPOSE": libsbml.AST_BASIC_CONTENT_COMPOSE,
    "AST_BASIC_CONTENT_IDENT": libsbml.AST_BASIC_CONTENT_IDENT,
    "AST_BASIC_CONTENT_DOMAIN": libsbml.AST_BASIC_CONTENT_DOMAIN,
    "AST_BASIC_CONTENT_CODOMAIN": libsbml.AST_BASIC_CONTENT_CODOMAIN,
    "AST_BASIC_CONTENT_IMAGE": libsbml.AST_BASIC_CONTENT_IMAGE,
    "AST_BASIC_CONTENT_DOMAINOFAPPLICATION": libsbml.AST_BASIC_CONTENT_DOMAINOFAPPLICATION,
    "AST_UNKNOWN": libsbml.AST_UNKNOWN,
}  # type: ignore


class mathMLExporter:
    def __init__(
        self,
        *,
        mapper=mapper,
        namer: Callable[[str], str] = lambda x: x,
        identity: Callable[[Any], str] = str,
    ):
        self.mapper = mapper
        self.namer = namer
        self.identity = identity

    @dispatch
    def to_mathML(self, x):
        raise NotImplementedError(f"got type {type(x)}")

    @to_mathML.register
    def _(self, x: int):
        node = libsbml.ASTNode(libsbml.AST_INTEGER)
        node.setValue(x)
        return node

    @to_mathML.register
    def _(self, x: float):
        node = libsbml.ASTNode(libsbml.AST_REAL)
        node.setValue(x)
        return node

    @to_mathML.register
    def _(self, x: Symbol):
        if x.expression is None:
            node = libsbml.ASTNode(libsbml.AST_NAME)
            node.setId(self.identity(x))
            node.setName(self.namer(x.name))
            return node

        if len(x.expression.kwargs) > 0:
            raise NotImplementedError

        func = x.expression.func
        args = x.expression.args
        node = libsbml.ASTNode(self.mapper[func])
        for arg in args:
            node.addChild(self.to_mathML(arg))
        return node
