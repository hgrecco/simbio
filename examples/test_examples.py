from pathlib import Path

from ward import each, test

examples = Path("examples").glob("usage*.py")


@test("Test {example}")
def _(example=each(*examples)):
    with open(example) as f:
        script = f.read()
        exec(script)
