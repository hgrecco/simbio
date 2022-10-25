import importlib.util
import pkgutil

import typer

app = typer.Typer()


class Module:
    def __init__(self, name: str):
        self.name = name

    def yield_submodule_names(self):
        spec = importlib.util.find_spec(self.name)
        for finder, name, ispkg in pkgutil.iter_modules(
            spec.submodule_search_locations
        ):
            yield name

    @property
    def path(self):
        return importlib.util.find_spec(self.name).origin

    def run(self):
        spec = importlib.util.find_spec(self.name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


@app.command()
def list():
    for name in Module("simbio.models").yield_submodule_names():
        print(name)


@app.command(no_args_is_help=True)
def test(
    model: str,
    *,
    name: str | None = None,
    all: bool = typer.Option(False, "--all"),
    list: bool = typer.Option(False, "--list"),
):
    if list:
        for name in Module(f"simbio.models.{model}.tests").yield_submodule_names():
            print(name)
    elif all:
        import pytest

        module = Module(f"simbio.models.{model}")
        pytest.main([module.path])
    else:
        if name is None:
            raise ValueError
        import pytest

        module = Module(f"simbio.models.{model}.tests.{name}")
        pytest.main([module.path])


@app.command(no_args_is_help=True)
def figure(
    model: str,
    *,
    name: str | None = None,
    list: bool = typer.Option(False, "--list"),
):
    if list:
        for name in Module(f"simbio.models.{model}.figures").yield_submodule_names():
            print(name)
    else:
        if name is None:
            raise ValueError

        Module(f"simbio.models.{model}.figures.{name}").run()


if __name__ == "__main__":
    app()
