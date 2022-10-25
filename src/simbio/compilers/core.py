from __future__ import annotations

import numbers
from abc import ABC, abstractmethod
from functools import cached_property, partial

import numpy as np
import pandas as pd

from ..components._container import Reference, RelativeReference, get_full_name
from ..components.types import Compartment, Parameter, SingleReaction, Species


class Compiler(ABC):
    def __init__(self, model: Compartment) -> None:
        self.model = model

    @abstractmethod
    def _build_reaction_ip_rhs(
        self, full_name: str, reaction: SingleReaction
    ) -> callable:
        raise NotImplementedError

    @cached_property
    def rhs(self):
        funcs = tuple(
            self._build_reaction_ip_rhs(name, reaction)
            for name, reaction in self.yield_single_reactions()
        )

        def fun(t, y, p):
            out = np.zeros_like(y)
            for func in funcs:
                func(t, y, p, out)
            return out

        return fun

    def build_rhs(self, p):
        return partial(self.rhs, p=p)

    def yield_single_reactions(self):
        yield from self.model._filter_contents(SingleReaction, recursive=True)

    def reactants_stoich(
        self, full_name: str, reaction: SingleReaction
    ) -> dict[int, float]:
        out = {}
        for name, st in reaction.reactants_stoichiometry.items():
            name = self.resolve(f"{full_name}.{name}")
            index = self.get_species_index(name)
            out[index] = st
        return out

    def species_stoich(
        self, full_name: str, reaction: SingleReaction
    ) -> dict[int, float]:
        out = {}
        for name, st in reaction.species_stoichiometry.items():
            name = self.resolve(f"{full_name}.{name}")
            index = self.get_species_index(name)
            out[index] = st
        return out

    def parameter_indexes(self, full_name: str, reaction: SingleReaction) -> tuple[int]:
        indexes = []
        for name in reaction.parameters:
            name = f"{full_name}.{name}"
            index = self.get_parameter_index(name)
            indexes.append(index)
        return tuple(indexes)

    def get_species_index(self, name: str) -> int:
        return self.species.index.get_loc(name)

    def get_parameter_index(self, name: str) -> int:
        return self.parameters.index.get_loc(name)

    def resolve(self, name: str) -> str:
        while isinstance(name, str):
            old_name, name = name, self.values[name]
        return old_name

    @cached_property
    def values(self) -> dict[str, str | Species | Parameter]:
        """Species and Parameters participating in reactions."""

        def resolve(name, content) -> str:
            value = content.value
            if isinstance(value, numbers.Number):
                return content
            elif isinstance(value, RelativeReference):
                return value.resolve_from(name)

        all_contents = {
            k: resolve(k, v)
            for k, v in self.model._filter_contents(Species, Parameter, recursive=True)
        }

        in_reaction_contents = {}
        for full_name, reaction in self.yield_single_reactions():
            for name, value in reaction._filter_contents(Species, Parameter):
                name = f"{full_name}.{name}"
                while True:
                    value = all_contents[name]
                    in_reaction_contents[name] = value
                    if isinstance(value, str):
                        name = value
                    else:
                        break

        return in_reaction_contents

    @cached_property
    def species(self):
        return pd.Series(
            {
                name: species.value
                for name, species in self.values.items()
                if isinstance(species, Species)
            }
        )

    @cached_property
    def parameters(self):
        return pd.Series(
            {
                name: parameter.value
                for name, parameter in self.model._filter_contents(
                    Parameter, recursive=True
                )
                if name in self.values
            }
        )

    def build_value_vectors(
        self,
        values: dict[str | Reference, float] = {},
    ) -> tuple[pd.Series, pd.Series]:
        def resolve(k):
            if isinstance(k, Reference):
                return get_full_name(k, root=self.model)
            elif isinstance(k, str):
                return k
            else:
                raise TypeError

        values = {resolve(k): v for k, v in values.items()}
        species = {k: values.pop(k, v) for k, v in self.species.items()}
        parameters = {}
        for name, value in self.parameters.items():
            value = values.pop(name, value)
            if isinstance(value, RelativeReference):
                value = self.values[name]
            parameters[name] = value
        for name, value in parameters.items():
            while isinstance(value, str):
                value = parameters[value]
            parameters[name] = value

        if len(values) > 0:
            raise ValueError

        return pd.Series(species), pd.Series(parameters)
