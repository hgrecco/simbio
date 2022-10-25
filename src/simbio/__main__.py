import typer

from .cli import models

app = typer.Typer(no_args_is_help=True)
app.add_typer(models.app, name="model", no_args_is_help=True)

if __name__ == "__main__":
    app()
