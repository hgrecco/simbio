from __future__ import annotations

from collections import defaultdict
from typing import Mapping

from ._container import Container, Content, Reference, T
from ._dsl import DSL


class Builder(Container):
    def __init__(
        self,
        container: Container,
        inheriting: tuple[Container] = (),
        namespace: dict[str, Content | Container] = {},
        overrides: set[str] = (),
    ):
        if isinstance(container, DSL) and issubclass(container, Container):
            dsls = container._filter_contents(container, DSL)
        else:
            dsls = container._filter_contents(DSL)

        for name, value in dsls:
            container._contents[name] = value._builder(value)

        self._container = container

        for base in inheriting:
            self._update(base)

        for name, value in namespace.items():
            self._add(name, value)

        check_collisions(self, *inheriting, overrides=overrides)

    def __copy__(self, new=None, *, name: str = None, parent: Container = None):
        container = self._container.__copy__(new, name=name, parent=parent)
        return self.__class__(container)

    @property
    def _contents(self) -> dict[str, Content | Builder]:
        return self._container._contents

    @property
    def name(self) -> str:
        return self._container.name

    @name.setter
    def name(self, value):
        if self.name is not None:
            raise ValueError

        self._container.name = value

    @property
    def parent(self) -> Container:
        return self._container.parent

    @parent.setter
    def parent(self, value):
        if self.parent is not None:
            raise ValueError

        self._container.parent = value

    def __getattr__(self, name):
        return getattr(self._container, name)

    def build(self) -> Container:
        for name, value in self._filter_contents(Builder):
            self._contents[name] = value.build()
        return self._container

    def _check(self, value):
        raise NotImplementedError

    def add(self, name: str, value: T, *, replace: bool = False) -> T | Reference:
        if replace:
            try:
                current = self._contents[name]
            except KeyError:
                raise ValueError(f"{name} does not exist.")

            if type(value) is not type(current):
                raise TypeError(f"{type(value)=} does not match {type(current)=}.")
        elif name in self._contents:
            raise ValueError(f"{name} already exists.")

        self._add(name, value)
        return getattr(self, name)

    def _add(self, name: str, value: T):
        value = self._check(value)
        if isinstance(value, Container):
            value.name = name
            value.parent = self._container
        self._contents[name] = value

    def update(self, value: Container, *, replace: bool = False) -> Builder:
        if type(value) not in (type(self), type(self._container)):
            raise TypeError

        overrides = value._contents.keys() if replace else ()
        check_collisions(self, value, overrides=overrides)
        self._update(value)
        return self

    def _update(self, value: Container):
        for name, value in value._contents.items():
            if isinstance(value, DSL):
                try:
                    self._contents[name]._update(value)
                except KeyError:
                    self._add(name, value.to_builder())
            else:
                self._add(name, value)

    def remove(self, name: str, value: T):
        raise NotImplementedError


def _multidict(*dicts: Mapping[str, T]) -> dict[str, list[T]]:
    """Merges multiple dicts into a key to list of values mapping.

    >>> _multidict(dict(a=1, b=2), dict(a=3))
    {"a": [1, 3], "b": [2]}
    """
    mdict = defaultdict(list)
    for d in dicts:
        for k, v in d.items():
            mdict[k].append(v)
    return dict(mdict)


def find_collisions(
    *containers: Container, overrides: set[str] = ()
) -> tuple[set[str], set[str]]:
    """Returns type and value collisions between multiple Containers."""
    type_collisions = set()
    value_collisions = set()

    if len(containers) == 1:
        return type_collisions, value_collisions

    contents = _multidict(*(c._contents for c in containers))
    for name, values in contents.items():
        if len(values) == 1:
            continue

        values = [v._container if isinstance(v, Builder) else v for v in values]
        types = set(type(v) for v in values)
        if len(types) > 1:
            if name in overrides and all(type(t) is DSL for t in types):
                pass
            else:
                type_collisions.add(name)
            continue

        if name in overrides:
            continue

        t = types.pop()
        if issubclass(t, DSL):
            sub_type_collisions, sub_value_collisions = find_collisions(*values)
            type_collisions.update(f"{name}.{s}" for s in sub_type_collisions)
            value_collisions.update(f"{name}.{s}" for s in sub_value_collisions)
        elif len(set(values)) > 1:
            value_collisions.add(name)

    return type_collisions, value_collisions


def check_collisions(*containers: Container, overrides: set[str] = ()) -> None:
    type_collisions, value_collisions = find_collisions(
        *containers, overrides=overrides
    )

    if len(type_collisions) > 0:
        raise TypeError
    elif len(value_collisions) > 0:
        raise ValueError
