from __future__ import annotations

from ..components import SingleReaction
from .core import Compiler


class NumpyCompiler(Compiler):
    def _build_reaction_ip_rhs(self, full_name: str, reaction: SingleReaction):
        reactants_stoich = self.reactants_stoich(full_name, reaction)
        species_stoich = self.species_stoich(full_name, reaction)
        parameter_indexes = self.parameter_indexes(full_name, reaction)

        def ip_rhs(t, y, p, out):
            reactants = (
                y[index] ** stoich for index, stoich in reactants_stoich.items()
            )
            parameters = (p[index] for index in parameter_indexes)
            rate = reaction.reaction_rate(t, *reactants, *parameters)
            for index, stoich in species_stoich.items():
                out[index] += stoich * rate

        return ip_rhs
