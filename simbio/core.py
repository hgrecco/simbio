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

from typing import Dict, List, Optional, Tuple


class Content:
    """Base Content class.

    Content has two protected attributes, name and parent.
    """

    name: str
    parent: Optional[Container]

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    def __init__(self, *args, name=None, **kwargs):
        self._name = name
        self._parent = None
        super().__init__(*args, **kwargs)

    def __hash__(self) -> int:
        return id(self)

    def copy(self, *, new=None) -> Content:
        if new is None:
            new = self.__class__(name=self.name)
        return new

    def _absolute_path(self) -> List[Content]:
        """List of Contents upto."""
        path, content = [], self
        while content is not None:
            path.append(content)
            content = content.parent
        return path[::-1]

    @staticmethod
    def _common_parent(*contents: Tuple[Content, ...]):
        if len(contents) == 1:
            return contents[0].parent

        common_parent = None
        for parents in zip(*(c._absolute_path() for c in contents)):
            parent = parents[0]
            if all(p is parent for p in parents):
                common_parent = parent
            else:
                break

        if common_parent is None:
            raise ValueError("No common parent found.")

        return common_parent


class Container(Content):
    """Base Container class.

    Container is a Content that stores Content.
    """

    _contents: Dict[str, Content]

    def __init__(self, *args, name=None, contents=None, **kwargs):
        self._contents = contents or {}
        super().__init__(*args, name=name, **kwargs)

    def _add(self, content: Content) -> Content:
        """Add content to this container.

        Only content belonging to this container may be added,
        and its name must not collide with an already stored content.
        """
        if not isinstance(content, Content):
            raise TypeError(f"{content} is not a Content.")

        if content.name in self._contents:
            raise ValueError(f"There is already a Content named {content.name}")

        if content.parent is not None:
            raise Exception(
                f"{content} can't be added to {self}."
                f"It belongs to {content.parent}."
            )

        content._parent = self
        self._contents[content.name] = content
        return content

    @property
    def contents(self) -> Dict[str, Content]:
        """A view of stored content.

        Includes contents from stored Containers.
        """
        out = {}
        for name, content in self._contents.items():
            out[name] = content
            if isinstance(content, Container):
                for subname, subcontent in content.contents.items():
                    out[f"{name}.{subname}"] = subcontent
        return out

    def _filter_contents(self, cls) -> Tuple[Content, ...]:
        return tuple(c for c in self.contents.values() if isinstance(c, cls))

    def _relative_path(self, content: Content) -> List[Content]:
        """Path from this Container to the given Content."""
        path = []
        while content is not self:
            path.append(content)
            content = content.parent
            if content is None:
                raise AttributeError(f"{content} does not belong to this Container.")
        return path[::-1]

    def _relative_name(self, content: Content) -> str:
        """Name relative to this Container."""
        if content is self:
            raise NotImplementedError("Relative name to self is not implemented.")

        return ".".join(c.name for c in self._relative_path(content))

    def __contains__(self, item: Content) -> bool:
        """Check if contained in this container or any subcontainers."""
        if not isinstance(item, Content):
            return False  # Shortcut

        if item is self:
            return False

        try:
            self._relative_name(item)
            return True
        except AttributeError:
            return False

    def __getitem__(self, item: str) -> Content:
        """If item has dots, search in corresponding sub-container."""

        if "." in item:
            c, item = item.split(".", 1)
            sub = self._contents[c]
            try:
                return sub[item]
            except TypeError:
                raise TypeError(f"Content {sub} of {c} is not a Container.")
        else:
            try:
                return self._contents[item]
            except KeyError:
                raise KeyError(f"{item} not found in {self}.") from None

    def __getattr__(self, item: str) -> Content:
        try:
            return self[item]
        except KeyError:
            raise AttributeError(f"{item} not found in {self}.") from None

    def __dir__(self):
        return super().__dir__() + list(self._contents)

    def copy(self, *, new=None) -> Container:
        if new is None:
            new = super().copy(new=new)

        # Copy _contents
        for content in self._contents.values():
            new._add(content.copy())
        return new
