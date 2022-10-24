from importlib.util import spec_from_file_location
from pathlib import Path

import pytest

path = Path(__file__).parent / "examples"
examples = path.glob("*.py")
# To be properly named in pytest, they must be a string:
examples = [p.stem for p in examples]


@pytest.mark.parametrize("example", examples)
def test_example(example):
    spec = spec_from_file_location(example, path / f"{example}.py")
    spec.loader.load_module()
