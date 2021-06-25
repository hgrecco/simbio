from importlib.util import spec_from_file_location
from pathlib import Path

from ward import each, test

examples = Path("examples").rglob("*.py")


@test("Test {example}")
def _(example=each(*examples)):
    import matplotlib.pyplot as plt

    plt.show = lambda: None
    spec = spec_from_file_location(example.stem, example)
    spec.loader.load_module()
