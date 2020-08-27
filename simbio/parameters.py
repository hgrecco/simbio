from __future__ import annotations

from dataclasses import dataclass

from .core import Content


@dataclass(frozen=True, eq=False)
class BaseParameter(Content):
    value: float = 0


@dataclass(frozen=True, eq=False)
class Parameter(BaseParameter):
    pass
