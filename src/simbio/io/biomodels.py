import biomodels

from .sbml import loads


def load_model(model_id: str):
    omex = biomodels.get_omex(model_id)
    text = omex.master.read_text()
    model = loads(text)
    return model


if __name__ == "__main__":
    model = load_model("BIOMD12")
