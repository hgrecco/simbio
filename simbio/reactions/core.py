from __future__ import annotations

import inspect
from dataclasses import dataclass
from itertools import chain
from typing import Dict, Generator, Tuple, get_type_hints

from orderedset import OrderedSet

from ..components import InReactionSpecies, Parameter, ReactionBalance, Species


class Reaction:
    """Base class for all reactions.

    A Reaction subclass must specify its Species and Parameters as class annotations.
    Subclasses are automatically instantiated as dataclasses, although it's recommended
    to include the @dataclass decorator, which let static analyzers provide signature
    completition for __init__.

    Reactions must implement the reactions method, which must yield other Reactions,
    or subclasses such as SingleReaction.

    See examples of compound reactions in simbio.reactions.compound.
    """

    # Class attributes
    _species_names: Tuple[str, ...]
    _parameter_names: Tuple[str, ...]

    def reactions(self) -> Generator[Reaction, None, None]:
        """Reactions yields other reactions."""
        raise NotImplementedError

    def single_reactions(self) -> Generator[Reaction, None, None]:
        for reaction in self.reactions():
            yield from reaction.single_reactions()

    def __init_subclass__(cls):
        """Initialize class as a dataclass.

        Set (ordered) tuples of reactions and parameters names from __init__ annotations.
        """
        # Create __init__ with dataclass
        dataclass(cls)

        # Save tuples of names inspecting __init__
        # If we inspect the class directly, we have to remove other unrelated annotations.
        annotations = get_type_hints(cls.__init__)
        cls._species_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Species)
        )
        cls._parameter_names = tuple(
            k for k, v in annotations.items() if issubclass(v, Parameter)
        )

        sig = inspect.signature(cls.reactions)
        if len(sig.parameters) != 1:
            raise ValueError(f"{cls.__qualname__}.reactions should have no parameters.")

    def __post_init__(self):
        """Initializes and validates arguments.

        Validates that instance arguments are Species, or InReactionSpecies
        with only one Species, and Parameters.
        Converts Species to InReactionSpecies with stoichiometry one.
        """

        # Validate expected Species
        for name in self._species_names:
            species = getattr(self, name)
            if isinstance(species, Species):
                setattr(self, name, 1.0 * species)  # Convert to InReactionSpecies
            elif not isinstance(species, InReactionSpecies):
                raise TypeError(f"{species} is not a Species.")
            elif len(species) > 1:
                raise ValueError(
                    f"More than one species assigned to {name}: {species}."
                )

        # Validate expected Parameters
        for parameter in self.parameters:
            if not isinstance(parameter, Parameter):
                raise TypeError(f"{parameter} is not a Parameter.")

    @property
    def species(self) -> Tuple[Species, ...]:
        """Return a tuple of the species in this reaction."""
        return tuple(OrderedSet(chain.from_iterable(self.in_reaction_species.values())))

    @property
    def parameters(self) -> Tuple[Parameter, ...]:
        """Return a tuple of the parameters in this reaction."""
        return tuple(getattr(self, name) for name in self._parameter_names)

    @property
    def in_reaction_species(self) -> Dict[str, InReactionSpecies]:
        """Return a dict of generic name to InReactionSpecies."""
        return {name: getattr(self, name) for name in self._species_names}

    @property
    def in_reaction_parameters(self) -> Dict[str, Parameter]:
        """Return a dict of generic name to Parameter."""
        return {name: getattr(self, name) for name in self._parameter_names}


class SingleReaction(Reaction):
    """Base class for all single reactions.

    As with Reactions, SingleReactions must declare Species and Parameters as class annotations.
    Also, they must implement the reaction_balance method between those species,
    and the reaction_rate function.

    It is recommended to decorate the reaction with @dataclass, which let static analyzers
    provide signature completition for __init__.
    """

    def reaction_balance(self) -> ReactionBalance:
        raise NotImplementedError

    @staticmethod
    def reaction_rate(t, *args) -> float:
        raise NotImplementedError

    def single_reactions(self):
        yield self

    def __init_subclass__(cls):
        """Validates reaction.

        Check if reaction_rate method is well-defined. It must:
        - be a staticmethod
        - have 't' as its first parameter, and the rest must correspond
        to reactant Species or Parameters.
        """
        # Copy eq and hash methods before calling the __init_subclass__ of parent,
        # as @dataclass would override them if not called with @dataclass(eq=False)
        cls.__eq__ = cls.__eq__
        cls.__hash__ = cls.__hash__
        super().__init_subclass__()

        # Check if rate is a staticmethod
        if not isinstance(inspect.getattr_static(cls, "reaction_rate"), staticmethod):
            raise TypeError(
                f"{cls.__qualname__}.reaction_rate must be a staticmethod. Use @staticmethod decorator."
            )

        # Check rate signature
        first, *parameters = inspect.signature(cls.reaction_rate).parameters

        # Check if 't' is the first parameter
        if first != "t":
            raise ValueError(
                f"{cls.__qualname__}.reaction_rate first parameter is not t, but {first}"
            )

        # Create a generic instance to inspect the reaction balance.
        reaction_balance = cls(
            **{name: Species(0, name=name) for name in cls._species_names},
            **{name: Parameter(0, name=name) for name in cls._parameter_names},
        ).reaction_balance()
        reactants = {s.name for s in reaction_balance.reactants}
        products = {s.name for s in reaction_balance.products}

        # Check that all rate parameters are either reactant Species or Parameters
        for parameter in parameters:
            if parameter in cls._species_names:
                if parameter in reactants:
                    continue
                elif parameter in products:
                    raise TypeError(
                        f"{cls.__qualname__}.{parameter} is a Species which is parameter of the rate equation, while being only a product of the reaction, instead of a reactant."
                    )
                else:
                    raise TypeError(
                        f"{cls.__qualname__}.{parameter} is a Species which is parameter of the rate equation, but it is not specified as a reactant in the reaction balance."
                    )
            elif parameter in cls._parameter_names:
                continue
            elif parameter in get_type_hints(cls.__init__):
                raise TypeError(
                    f"{cls.__qualname__}.{parameter} is missing a Species or Parameter class annotation."
                )
            else:
                raise ValueError(
                    f"{cls.__qualname__}.reaction_rate parameter {parameter} is missing from {cls.__qualname__} annotations."
                )

    def __hash__(self) -> int:
        return sum(map(hash, chain(self.species, self.parameters)))

    def __eq__(self, other) -> bool:
        """Reactions are equal if they
        - are equivalent, that is, have the same reaction balance
        - have the same parameters
        - are instances of the same class
        """
        if other.__class__ is not self.__class__:
            return NotImplemented

        return (self.parameters == other.parameters) and self.equivalent(other)

    def equivalent(self, other) -> bool:
        """Check equivalence between reactions.

        Reactions are equivalent if their reaction balances involve
        the same Species with the same stoichiometries as reactants
        and products.
        """
        return self.reaction_balance() == other.reaction_balance()
