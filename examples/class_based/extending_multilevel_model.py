from simbio import Compartment, Parameter, Species


class Cell(Compartment):
    A = Species(1)
    k = Parameter(1)

    class Nucleus(Compartment):
        A = Species(2)
        k = Parameter(2)


class ExtendedCell(Cell):
    A = Species(10, override=True)

    class Nucleus(Cell.Nucleus):  # Extend compartment
        A = Species(20, override=True)
