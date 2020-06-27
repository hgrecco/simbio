from dataclasses import dataclass


@dataclass
class Parameter:
    name: str
    value: float = 0
