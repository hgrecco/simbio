from dataclasses import dataclass

from .core import Content


@dataclass
class Parameter(Content):
    value: float = 0
