import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import pooch
from pandas.testing import assert_frame_equal
from poincare.solvers import LSODA
from pydantic import BaseModel
from pytest import mark, xfail
from symbolite.core import Unsupported

from .... import Simulator
from .. import loads

PATH = pooch.retrieve(
    "https://github.com/sbmlteam/sbml-test-suite/releases/download/3.4.0/semantic_tests.v3.4.0.zip",
    known_hash="sha256:ec1abd53e28221b8828c88f237142067d0e6e63042519f486868195b581c4b2c",
)
FILE = zipfile.Path(PATH, "semantic/")
MODELS = sorted(p.name for p in FILE.iterdir() if p.is_dir())
ATOL_FACTOR: dict[str, float] = pd.read_csv(
    Path(__file__).parent / "atol_factor.csv",
    header=None,
    index_col=0,
    dtype={0: str, 1: float},
).squeeze()


class Settings(BaseModel):
    start: float | None
    duration: float | None
    steps: int | None
    variables: list[str]
    absolute: float
    relative: float
    amount: list[str]
    concentration: list[str]

    @classmethod
    def from_file(cls, file: Iterable[str], /):
        lists = ("variables", "amount", "concentration")

        kwargs = {}
        for line in file:
            k, _, v = line.partition(":")
            if k in lists:
                v = [v.strip() for v in v.split(",")]
            else:
                v = v.strip()
                if v == "":
                    v = None
            kwargs[k] = v
        return cls(**kwargs)


@dataclass
class Loader:
    file: zipfile.Path
    model: str

    def read_sbml(self, lv: tuple[int, int] | None = None) -> str:
        if lv is not None:
            level, version = lv
            relative_path = f"{self.model}/{self.model}-sbml-l{level}v{version}.xml"
            return (self.file / relative_path).read_text()

        for lv in [(3, 2), (3, 1), (2, 5), (2, 4), (2, 3), (2, 2), (2, 1)]:
            try:
                return self.read_sbml(lv)
            except FileNotFoundError as e:
                last_error = e
        else:
            raise last_error

    def read_settings(self) -> Settings:
        relative_path = f"{self.model}/{self.model}-settings.txt"
        with (self.file / relative_path).open() as f:
            return Settings.from_file(f)

    def read_results(self) -> pd.DataFrame:
        relative_path = f"{self.model}/{self.model}-results.csv"
        with (self.file / relative_path).open() as f:
            return pd.read_csv(f)


@mark.parametrize("model", MODELS)
def test_loading(model):
    sbml = Loader(FILE, model).read_sbml()
    try:
        model = loads(sbml, name=model)
    except Exception as e:
        xfail(str(e))


@mark.parametrize("model_id", MODELS)
def test_running(model_id):
    loader = Loader(FILE, model_id)

    sbml = loader.read_sbml()
    try:
        model = loads(sbml, name=model_id)
    except Exception:
        # There is a separate test for model loading errors
        xfail("Loading error")

    if len(model.variables) == 0:
        xfail("no variables in model")

    settings = loader.read_settings()
    if settings.start is None:
        xfail("start is None")
    elif settings.duration is None:
        xfail("duration is None")
    elif settings.steps is None:
        xfail("steps is None")
    else:
        save_at = np.linspace(
            settings.start,
            settings.start + settings.duration,
            settings.steps + 1,
        )

    try:
        df = (
            Simulator(
                model,
                transform=[getattr(model, name) for name in settings.variables],
            )
            .solve(
                save_at=save_at,
                solver=LSODA(
                    atol=settings.absolute,
                    rtol=settings.relative,
                ),
            )
            .reset_index()
        )
    except TypeError as e:
        if Unsupported.__name__ in e.args[0]:
            xfail("unsupported symbolite operation")
        raise e
    except KeyError:
        xfail("dependency solving error")

    df_expected = loader.read_results()
    assert_frame_equal(
        df[settings.variables],
        df_expected[settings.variables],
        atol=settings.absolute * ATOL_FACTOR.get(model_id, 1),
        rtol=settings.relative,
        check_dtype=False,
    )
