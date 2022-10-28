from __future__ import annotations

import dataclasses
import inspect
import sys
from contextlib import suppress
from typing import TYPE_CHECKING

try:
    from typing import get_args
    from typing import get_origin as _get_origin
except ImportError:
    from typing_extensions import get_args, get_origin as _get_origin

from ._container import Container, Content, Override, RelativeReference

if TYPE_CHECKING:
    from ._builder import Builder


def get_origin(t):
    o = _get_origin(t)
    return o if o is not None else t


class AnnotationsDict(dict):
    """Evaluates annotations on insertion.

    If the annotation is a Content subclass,
    it removes the value from the locals namespace,
    wraps it in the Content subclass,
    and moves it to the contents dict.
    """

    def __init__(self, locals: dict, contents: dict):
        self.locals = locals
        self.contents = contents

    @property
    def module(self):
        module = self.locals["__module__"]
        return sys.modules[module].__dict__

    def __setitem__(self, key, annotation) -> None:
        if isinstance(annotation, str):
            annotation = self.evaluate_annotation(annotation)

        if issubclass(get_origin(annotation), Content):
            self.move_to_contents(key, annotation)

        return super().__setitem__(key, annotation)

    def evaluate_annotation(self, annotation: str):
        return eval(annotation, self.module, self.locals)

    def move_to_contents(self, key: str, type: type):
        with suppress(KeyError):
            value = self.locals.pop(key)
            self.contents[key] = type(value)


class DSLDict(dict):
    """Namespace for DSL metaclass.

    Saves Content and Container in a separate contents dict,
    for which it cooperates with AnnotationsDict.

    Returns RelativeReferences for annotated Content.
    """

    def __init__(self, contents: dict[str, Content | Container] = None):
        if contents is None:
            contents = {}

        self.contents = contents
        self.annotations = self["__annotations__"] = AnnotationsDict(
            locals=self, contents=self.contents
        )

    def __getitem__(self, key):
        with suppress(KeyError):
            # If it is Content subclass,
            # its type will be given by its annotation.
            annotation = self.annotations[key]
            annotation = get_origin(annotation)
            if issubclass(annotation, Content):
                return RelativeReference(name=key, type=annotation, parent=0)

        with suppress(KeyError):
            return self.contents[key]

        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(value, Container):
            self.contents[key] = value
        elif isinstance(value, Content):
            raise TypeError
        else:
            super().__setitem__(key, value)


class DSL(Container, type):
    """DSL is a metaclass that builds a Container from class annotations.

    >>> class A(metaclass=DSL):
    ...     A: Content
    ...     B: Content = 1
    ...     C: Content = A
    ...
    >>> A._contents
    {
        "B": Content(value=1),
        "C": Content(value=RelativeReference(name="A", type=Content, parent="."))
    }
    """

    _builder: type[Builder]

    def __copy__(self, new=None, *, name: str = None, parent: Container = None):
        if new is not None:
            raise TypeError

        new = self.__class__(self.__name__, (self,), DSLDict())
        new.name = name
        new.parent = parent
        return new

    def to_builder(self) -> Builder:
        self = self.__copy__()
        return self._builder(self)

    @classmethod
    def __prepare__(cls, name, bases):
        return DSLDict()

    def __init__(self, name, bases, namespace: DSLDict):
        overrides = set()
        for name, v in namespace.contents.items():
            if isinstance(v, DSL):
                replace = is_container_overriding(name, v, bases)
            elif isinstance(v, Container):
                annotation = namespace.annotations.get(name)
                replace = is_content_overriding(annotation)
            elif isinstance(v, Content):
                annotation = namespace.annotations.get(name)
                replace = is_content_overriding(annotation)
            else:
                raise TypeError

            if replace:
                overrides.add(name)

        self._contents = {}
        self._builder(
            self,
            inheriting=tuple(b for b in bases if isinstance(b, self.__class__)),
            namespace=namespace.contents,
            overrides=overrides,
        ).build()

        self.__signature__ = create_signature(self)

    def __call__(self, *args, **kwds):
        bound = self.__signature__.bind(
            *args, **kwds
        )  # TODO: create __init__ in DSL instance. It's faster.
        parameters = self.__signature__.parameters

        namespace = DSLDict()
        for name, value in bound.arguments.items():
            if isinstance(value, RelativeReference):
                value = dataclasses.replace(value, parent=value.parent + 1)
            namespace[name] = value
            namespace.annotations[name] = parameters[name].annotation

        instance = super().__call__()
        instance._contents = {}
        return self._builder(
            instance,
            inheriting=(self,),
            namespace=namespace.contents,
            overrides=kwds.keys(),
        ).build()


def is_content_overriding(annotation: type) -> bool:
    return Override in get_args(annotation)


def is_container_overriding(name: str, container: DSL, inheriting: tuple[DSL]) -> bool:
    inherited = {getattr(b, name, None) for b in inheriting}
    inherited.discard(None)

    if len(inherited) == 0:
        return False
    elif inherited.issubset(container.__bases__):
        return True
    else:
        raise ValueError


def create_signature(cls: Container):
    try:
        parameters = dict(cls.__signature__.parameters)
    except AttributeError:
        parameters = {}

    for (
        name,
        annotation,
    ) in cls.__annotations__.items():
        annotation = get_origin(annotation)
        if not issubclass(annotation, Content):
            continue

        try:
            default = cls._contents[name].value
        except KeyError:
            default = inspect.Parameter.empty

        parameters[name] = inspect.Parameter(
            name=name,
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=default,
            annotation=annotation,
        )

    return inspect.Signature(parameters.values())
