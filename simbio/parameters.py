from __future__ import annotations

from .core import Content


class BaseParameter(Content):
    value: float = 0


class Parameter(BaseParameter):
    pass
