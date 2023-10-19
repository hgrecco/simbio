import biomodels

from .sbml import loads


def load_model(model_id: str, *, name: str | None = None):
    omex = biomodels.get_omex(model_id)
    text = omex.master.read_text()
    model = loads(text, name=name)
    return model


if __name__ == "__main__":
    model = load_model("BIOMD12")
