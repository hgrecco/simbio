from __future__ import annotations

import itertools
import types
from functools import cached_property

import numba

from ..components import SingleReaction
from .core import Compiler


class NumbaCompiler(Compiler):
    def _build_reaction_ip_rhs(self, full_name: str, reaction: SingleReaction):
        reactants_stoich = self.reactants_stoich(full_name, reaction)
        species_stoich = self.species_stoich(full_name, reaction)
        parameter_indexes = self.parameter_indexes(full_name, reaction)

        input = (1 + len(reactants_stoich) + len(parameter_indexes)) * (numba.float64,)
        output = numba.float64
        signature = output(*input)
        rate = numba.cfunc(signature)(reaction.reaction_rate)
        return self._inplace_rhs(
            rate, reactants_stoich, species_stoich, parameter_indexes
        )

    @staticmethod
    def _inplace_rhs(
        reaction_rate, reactants_stoich, species_stoich, parameter_indexes
    ):
        y = (f"y[{ix}] ** {st}" for ix, st in reactants_stoich.items())
        p = (f"p[{ix}]" for ix in parameter_indexes)
        rhs_template = "reaction_rate(t, %s)" % ", ".join(itertools.chain(y, p))

        template = "\n  ".join(
            [
                "def func(t, y, p, out):",
                f"rate = {rhs_template}",
                *(f"out[{ix}] += {st} * rate" for ix, st in species_stoich.items()),
            ]
        )

        code_obj = compile(template, "<string>", "exec")
        func = types.FunctionType(code_obj.co_consts[0], locals())

        t = numba.float64
        y = numba.types.Array(numba.float64, 1, "C", readonly=True)
        p = numba.types.Array(numba.float64, 1, "C", readonly=True)
        out = numba.float64[:]
        return numba.cfunc(numba.void(t, y, p, out))(func)

    @cached_property
    def rhs(self):
        rhs = super().rhs
        t = numba.float64
        y = numba.types.Array(numba.float64, 1, "C", readonly=True)
        p = numba.types.Array(numba.float64, 1, "C", readonly=True)
        return numba.cfunc(numba.float64[::1](t, y, p))(rhs)

    def build_rhs(self, p):
        rhs = self.rhs
        return numba.njit(lambda t, y: rhs(t, y, p))
