from __future__ import annotations

from dataclasses import dataclass, replace
from numbers import Number
from typing import Generic, Iterator, TypeVar

T = TypeVar("T")


class Override:
    pass


Overridable = TypeVar("Overridable", bound=Override)


class Content(Generic[Overridable]):
    value: Number | Reference


class Container(Generic[Overridable]):
    """A Container is a tree-like data structure
    which contains Contents and Containers as children.
    It has an optional parent Container.

    Its children can be accessed as attributes,
    and non-Container ones are returned as References.

    When adding a Content whose value is a Reference to another Content,
    that Reference must be converted to a RelativeReference
    before adding it to the Container._contents dict.
    Therefore, we can check for equality by comparing the _contents.
    """

    name: str | None = None
    parent: Container | None = None
    _contents: dict[str, Content | Container]

    def __copy__(self, new=None, *, name: str = None, parent: Container = None):
        """Recursively copy this Container and its Container children."""
        if new is None:
            new = object.__new__(self.__class__)

        new.name = name
        new.parent = parent
        new._contents = {}
        for name, value in self._contents.items():
            if isinstance(value, Container):
                value = value.__copy__(name=name, parent=new)
            new._contents[name] = value
        return new

    def __getattr__(self, name):
        try:
            value = self._contents[name]
        except KeyError:
            raise AttributeError from None

        if not isinstance(value, Container):
            return Reference(name=name, type=type(value), parent=self)
        else:
            return value

    def _filter_contents(
        self, *types: type[T], recursive: bool = False
    ) -> Iterator[tuple[str, T]]:
        """Yield (name, content) pairs of the given types.

        Optionally, search recursively in its Container children.
        In that case, name is f"{parent}.{child}".
        """
        for k, v in self._contents.items():
            if isinstance(v, types):
                yield k, v

            if recursive and isinstance(v, Container):
                for ks, vs in v._filter_contents(*types, recursive=recursive):
                    yield f"{k}.{ks}", vs

    def __eq__(self, other: Container) -> bool:
        if not isinstance(other, Container):
            return NotImplemented

        return self._contents == other._contents

    def __hash__(self) -> int:
        return hash(frozenset(self._contents.keys()))


@dataclass(frozen=True)
class Reference:
    name: str
    type: Content
    parent: Container
    stoichiometry: float = 1.0

    def resolve(self, *, recursive: bool = False):
        """Returns the referenced Content."""
        content: Content = self.parent._contents[self.name]

        if isinstance(content.value, RelativeReference):
            value = content.value.to_reference_from(self.parent)

            if recursive:
                while isinstance(value, Reference):
                    value = value.resolve().value

            content = content.__class__(value)

        return content

    def relative_to(self, container: Container) -> RelativeReference:
        self_path = list(yield_parents(self))
        container_path = list(yield_parents(container))
        parent = first_common_parent(reversed(self_path), reversed(container_path))
        if parent is None:
            raise ValueError

        self_path = self_path[: self_path.index(parent)]
        self_path = [c.name for c in self_path]
        self_path.append(self.name)
        name = ".".join(self_path)
        level = container_path.index(parent)

        return RelativeReference(
            name=name,
            type=self.type,
            parent=level,
            stoichiometry=self.stoichiometry,
        )

    def __mul__(self, other):
        if not isinstance(other, Number):
            return NotImplemented

        return replace(self, stoichiometry=self.stoichiometry * other)

    __rmul__ = __mul__


@dataclass(frozen=True)
class RelativeReference:
    name: str
    type: Content
    parent: int
    stoichiometry: float = 1.0

    def resolve_from(self, name: str) -> str:
        splits = self.parent + 1
        names = name.rsplit(".", maxsplit=splits)
        if len(names) <= splits:
            return self.name
        else:
            return f"{names[0]}.{self.name}"

    def to_reference_from(self, container: Container) -> Reference:
        parent = container

        for level in range(self.parent):
            parent = parent.parent
            if parent is None:
                raise ValueError

        *names, name = self.name.split(".")
        try:
            for n in names:
                parent = getattr(parent, n)
        except AttributeError:
            raise ValueError

        return Reference(
            name=name,
            type=self.type,
            parent=parent,
            stoichiometry=self.stoichiometry,
        )

    def __mul__(self, other):
        if not isinstance(other, Number):
            return NotImplemented

        return replace(self, stoichiometry=self.stoichiometry * other)

    __rmul__ = __mul__


def is_cyclic_reference(name: str, content: Content, parent: Container) -> bool:
    value = content.value
    reference = Reference(name=name, type=type(content), parent=parent)
    while isinstance(value, Reference):
        value = value.resolve().value
        if value == reference:
            return True
    else:
        return False


def yield_parents(x: Container | Reference, *, up_to: Container = None):
    if isinstance(x, Reference):
        x = x.parent

    while not (x is up_to or x is None):
        yield x
        x = x.parent


def first_common_parent(*paths: list[Container]) -> Container | None:
    common_parent = None
    for parents in zip(*paths):
        if all(p is parents[0] for p in parents):
            common_parent = parents[0]
        else:
            break

    return common_parent


def get_full_name(x: Container | Reference, *, root: Container = None):
    path = []
    if isinstance(x, Reference):
        path.append(x.name)
    path.extend(p.name for p in yield_parents(x, up_to=root))
    return ".".join(reversed(path))
