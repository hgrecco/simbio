from __future__ import annotations

import itertools
import types
from functools import cached_property, partial

import numba
import numpy as np

from ..reactions.core import SingleReaction
from .core import Builder


class NumpyBuilder(Builder, alias="numpy"):
    def _build_reaction_ip_rhs(self, reaction: SingleReaction):
        ix_y = np.fromiter(map(self.species.index, reaction.species), dtype=int)
        ix_p = np.fromiter(map(self.parameters.index, reaction.parameters), dtype=int)

        reaction_balance = reaction.reaction_balance()
        ix_s = np.fromiter(
            map(self.species.index, reaction_balance.reactants), dtype=int
        )
        orders = np.fromiter(reaction_balance.reactants.values(), dtype=float)

        change = reaction_balance.change
        st_numbers = np.fromiter(map(change.get, reaction.species), dtype=float)

        def ip_rhs(t, y, p, out):
            rate = reaction.reaction_rate(t, *(y[ix_s] ** orders), *p[ix_p])
            for ix, st in zip(ix_y, st_numbers):
                out[ix] += st * rate

        return ip_rhs

    @cached_property
    def rhs(self):
        funcs = tuple(map(self._build_reaction_ip_rhs, self.reactions))

        def fun(t, y, p):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, p, out)
            return out

        return fun

    def build_rhs(self, p):
        return partial(self.rhs, p=p)


class NumbaBuilder(Builder, alias="numba"):
    def _build_reaction_ip_rhs(self, reaction):
        ix_y = np.fromiter(map(self.species.index, reaction.species), dtype=int)
        ix_p = np.fromiter(map(self.parameters.index, reaction.parameters), dtype=int)

        reaction_balance = reaction.reaction_balance()
        ix_s = np.fromiter(
            map(self.species.index, reaction_balance.reactants), dtype=int
        )
        orders = np.fromiter(reaction_balance.reactants.values(), dtype=float)

        change = reaction_balance.change
        st_numbers = np.fromiter(map(change.get, reaction.species), dtype=float)

        def ip_rhs(t, y, p, out):
            rate = reaction.reaction_rate(t, *(y[ix_s] ** orders), *p[ix_p])
            for ix, st in zip(ix_y, st_numbers):
                out[ix] += st * rate

        input = (1 + ix_s.size + ix_p.size) * (numba.float64,)
        rate = numba.cfunc(numba.float64(*input))(reaction.reaction_rate)
        return _inplace_rhs(rate, ix_y, st_numbers, ix_s, orders, ix_p)

    @cached_property
    def rhs(self):
        funcs = tuple(map(self._build_reaction_ip_rhs, self.reactions))

        def fun(t, y, p):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, p, out)
            return out

        t = numba.float64
        y = numba.types.Array(numba.float64, 1, "C", readonly=True)
        p = numba.types.Array(numba.float64, 1, "C", readonly=True)
        return numba.cfunc(numba.float64[::1](t, y, p))(fun)

    def build_rhs(self, p):
        rhs = self.rhs
        return numba.njit(lambda t, y: rhs(t, y, p))


def _inplace_rhs(reaction_rate, ix_y, st_numbers, ix_s, order, ix_p):
    y = (f"y[{i}] ** {k}" for i, k in zip(ix_s, order))
    p = (f"p[{i}]" for i in ix_p)
    rhs_template = "reaction_rate(t, %s)" % ", ".join(itertools.chain(y, p))

    template = "\n  ".join(
        [
            "def func(t, y, p, out):",
            f"rate = {rhs_template}",
            *(f"out[{ix}] += {st} * rate" for ix, st in zip(ix_y, st_numbers)),
        ]
    )

    code_obj = compile(template, "<string>", "exec")
    func = types.FunctionType(code_obj.co_consts[0], locals())

    t = numba.float64
    y = numba.types.Array(numba.float64, 1, "C", readonly=True)
    p = numba.types.Array(numba.float64, 1, "C", readonly=True)
    return numba.cfunc(numba.void(t, y, p, numba.float64[:]))(func)
