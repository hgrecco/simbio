from importlib.util import spec_from_file_location
from pathlib import Path

import pytest

examples = Path("examples").rglob("*.py")


@pytest.mark.parametrize("example", examples)
def test_example(example):
    import matplotlib.pyplot as plt

    plt.show = lambda: None
    spec = spec_from_file_location(example.stem, example)
    spec.loader.load_module()
