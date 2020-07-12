"""
    simbio.core
    ~~~~~~~~~~~

    This module provides the definition for:
    - Content: a base class for named objects.
    - Container: a base class for grouping content.

    :copyright: 2020 by SimBio Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Content:
    """Base Content class.

    Content have two protected attributes, name and belongs_to.
    Name must be a valid Python identifier.
    """

    name: str
    belongs_to: Container
    __protected_attrs = ("name", "belongs_to")

    def __post_init__(self) -> None:
        # Validate name
        if not self.name.isidentifier():
            raise ValueError("Name must be a valid Python identifier.")

    def __inmutable_if_assigned(self, name) -> None:
        """If a protected attribute is already assigned, raises AttributeError."""
        if name in self.__protected_attrs:
            try:
                self.__getattribute__(name)
            except AttributeError:
                pass
            else:
                raise AttributeError(f"{self.__class__.__name__}.{name} is inmutable.")

    def __setattr__(self, name: str, value: Any) -> None:
        self.__inmutable_if_assigned(name)
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        self.__inmutable_if_assigned(name)
        super().__delattr__(name)


@dataclass(repr=False)
class Container(Content):
    """Base Container class.

    Container is a Content that stores Content.
    """

    __contents: Dict[str, Content] = field(default_factory=dict)

    def add(self, content: Content) -> Content:
        """Add content to this container.

        Only content belonging to this container may be added,
        and its name must not collide with an already stored content.
        """
        if not isinstance(content, Content):
            raise TypeError(f"{content} is not a Content.")
        elif content.name in self.__contents:
            raise ValueError(f"There is already a Content named {content.name}")
        elif content.belongs_to is not self:
            raise Exception(
                f"{content} can't be added to {self}."
                f"It belongs to {content.belongs_to}."
            )

        self.__contents[content.name] = content
        return content

    @property
    def contents(self) -> Dict[str, Content]:
        """A view of stored content.

        Includes contents from stored Containers.
        """
        out = {}
        for con in self.__contents.values():
            out[con.name] = con
            if isinstance(con, Container):
                for subcon in con.contents.values():
                    out[f"{con.name}.{subcon.name}"] = subcon
        return out

    def relative_name(self, content: Content) -> str:
        """Name relative to this Container."""
        if content is self:
            raise NotImplementedError("Relative name to self is not implemented.")

        names = []
        while True:
            names.append(content.name)
            content = content.belongs_to
            if content is None:
                raise AttributeError(f"{content} does not belong to this Container.")
            elif content is self:
                break

        return ".".join(names[::-1])

    def __contains__(self, item) -> bool:
        """Check if contained in this container or any subcontainers."""
        if not isinstance(item, Content):
            return False

        if item is self:
            return False

        try:
            self.relative_name(item)
            return True
        except AttributeError:
            return False

    def __getitem__(self, item: str) -> Content:
        """If item has dots, search in corresponding sub-container."""

        if "." in item:
            c, item = item.split(".", 1)
            sub = self.__contents[c]
            try:
                return sub[item]
            except TypeError:
                raise ("Content {sub} of {c} is not a Container.")
        else:
            return self.__contents[item]

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"{item} not found in {self}.")

    def __repr__(self):
        return self.name
