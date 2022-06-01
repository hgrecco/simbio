from simbio.components import EmptyCompartment, Override, Parameter, Species


class Cell(EmptyCompartment):
    A: Species = 1
    k: Parameter = 1

    class Nucleus(EmptyCompartment):
        A: Species = 2
        k: Parameter = 2


class ExtendedCell(Cell):
    A: Species[Override] = 10

    class Nucleus(Cell.Nucleus):  # Extend compartment
        A: Species[Override] = 20
