import importlib
from pathlib import Path

import pytest

path = Path(__file__).parent / "examples"
examples = path.glob("*.py")
# To be properly named in pytest, they must be a string:
examples = [p.stem for p in examples]


@pytest.mark.parametrize("example", examples)
def test_example(example):
    spec = importlib.util.spec_from_file_location(example, path / f"{example}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
