from typing import Sequence

import biomodels

from .sbml import loads


def load(
    model_id: str,
    *,
    name: str | None = None,
    ignore_namespaces: Sequence[str] = [],
):
    omex = biomodels.get_omex(model_id)
    text = omex.master.read_text()
    model = loads(
        text,
        name=name,
        ignore_namespaces=ignore_namespaces,
    )
    return model
