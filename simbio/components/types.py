from __future__ import annotations

import dataclasses
import numbers
from typing import Union

from plum import Dispatcher
from typing_extensions import dataclass_transform

from ._builder import Builder
from ._container import Container, Content, Overridable, Reference, RelativeReference
from ._dsl import DSL

dispatch = Dispatcher()


@dataclasses.dataclass(frozen=True)
class Parameter(Content[Overridable]):
    value: numbers.Real | Reference


@dataclasses.dataclass(frozen=True)
class Species(Content[Overridable]):
    value: numbers.Real | Reference


class ReactionBuilder(Builder):
    def add_parameter(
        self, name: str, value: float | Parameter, *, replace: bool = False
    ) -> Reference:
        return self.add(name, Parameter(value), replace=replace)

    def add_species(
        self, name: str, value: float | Species, *, replace: bool = False
    ) -> Reference:
        return self.add(name, Species(value), replace=replace)

    def add_reaction(
        self, name: str, value: Reaction, *, replace: bool = False
    ) -> Reaction:
        return self.add(name, value, replace=replace)

    @dispatch
    def _check(self, value):
        raise TypeError

    @dispatch
    def _check(self, value: Parameter):  # noqa: F811
        v = value.value

        if isinstance(v, numbers.Number):
            if v < 0:
                raise ValueError
        elif isinstance(v, RelativeReference):
            if v.type is not Parameter:
                raise TypeError
        elif isinstance(v, Reference):
            if v.type is not Parameter:
                raise TypeError

            if isinstance(self._container, Reaction):
                pass
            else:
                v = v.relative_to(self._container)
                value = value.__class__(v)
        else:
            raise TypeError

        return value

    @dispatch
    def _check(self, value: Species):  # noqa: F811
        v = value.value

        if isinstance(v, numbers.Number):
            if v < 0:
                raise ValueError
        elif isinstance(v, RelativeReference):
            if v.type not in (Parameter, Species):
                raise TypeError
        elif isinstance(v, Reference):
            if v.type not in (Parameter, Species):
                raise TypeError

            if isinstance(self._container, Reaction):
                pass
            else:
                v = v.relative_to(self._container)
                value = value.__class__(v)
        else:
            raise TypeError

        return value

    @dispatch
    def _check(self, value: Reaction):  # noqa: F811
        components = {}
        for k, v in value._filter_contents(Parameter, Species):
            if isinstance(v.value, Reference):
                ref = v.value.relative_to(self._container)
                ref = dataclasses.replace(ref, parent=ref.parent + 1)
                v = v.__class__(ref)
            v = self._check(v)
            if isinstance(v.value, RelativeReference):
                assert v.value.parent <= 1
            components[k] = v

        value = value.__copy__()
        value._contents.update(components)
        return value


class GroupBuilder(ReactionBuilder):
    def add_group(self, name: str, group: Group | None = None) -> GroupBuilder:
        if group is None:
            group = EmptyGroup.to_builder()

        return self.add(name, group)

    @dispatch
    def _check(self, value: Union[Group, GroupBuilder]):
        return value


class CompartmentBuilder(GroupBuilder):
    def add_compartment(
        self, name: str, compartment: Compartment | None = None
    ) -> CompartmentBuilder:
        if compartment is None:
            compartment = EmptyCompartment.to_builder()

        return self.add(name, compartment)

    @dispatch
    def _check(self, value: Union[Compartment, CompartmentBuilder]):
        return value


@dataclass_transform(kw_only_default=True)
class Reaction(Container[Overridable], metaclass=DSL):
    _builder = ReactionBuilder

    @property
    def parameters(self):
        return dict(self._filter_contents(Parameter))

    @property
    def species(self):
        return dict(self._filter_contents(Species))


@dataclass_transform(kw_only_default=True)
class Group(DSL):
    _builder = GroupBuilder

    @property
    def parameters(self):
        return dict(self._filter_contents(Parameter))

    @property
    def species(self):
        return dict(self._filter_contents(Species))

    @property
    def reactions(self):
        return dict(self._filter_contents(Reaction))

    @property
    def groups(self):
        return dict(self._filter_contents(Group, GroupBuilder))


@dataclass_transform(kw_only_default=True)
class Compartment(DSL):
    _builder = CompartmentBuilder
    volume: numbers.Real

    @property
    def parameters(self):
        return dict(self._filter_contents(Parameter))

    @property
    def species(self):
        return dict(self._filter_contents(Species))

    @property
    def reactions(self):
        return dict(self._filter_contents(Reaction))

    @property
    def groups(self):
        return dict(self._filter_contents(Group, GroupBuilder))

    @property
    def compartments(self):
        return dict(self._filter_contents(Compartment, CompartmentBuilder))


class SingleReaction(Reaction):
    @property
    def reactants(self) -> tuple[Reference[Species]]:
        raise NotImplementedError

    @property
    def products(self) -> tuple[Reference[Species]]:
        raise NotImplementedError

    @staticmethod
    def reaction_rate(t, *args):
        raise NotImplementedError

    @property
    def reactants_stoichiometry(self):
        return {r.name: resolve_stoichiometry(r) for r in self.reactants}

    @property
    def species_stoichiometry(self):
        out = dict.fromkeys(self.species, 0)
        for p in self.products:
            out[p.name] += resolve_stoichiometry(p)
        for r in self.reactants:
            out[r.name] -= resolve_stoichiometry(r)
        return out


def resolve_stoichiometry(ref: Reference):
    stoichiometry = 1
    while isinstance(ref, Reference):
        stoichiometry *= ref.stoichiometry
        ref = ref.resolve().value
    return stoichiometry


class ReactionGroup(Reaction):
    @property
    def reactions(self):
        return dict(self._filter_contents(Reaction))


class SubClasser:
    def __new__(cls):
        metacls = cls.__class__
        name = cls.__name__
        bases = (cls,)
        return metacls.__new__(metacls, name, bases, {})


class EmptyGroup(SubClasser, metaclass=Group):
    pass


class EmptyCompartment(SubClasser, metaclass=Compartment):
    pass
