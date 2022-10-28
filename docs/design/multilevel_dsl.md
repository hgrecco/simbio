## DSL for Nested Compartments

When using nested Compartments, the standard syntax is simply to create a class inside a class:

```python
class Cell(Compartment):
    A = Species(0)
    k = Species(1)
    create_A = reactions.Creation(A, k)

    class Nucleus(Compartment):
        A = Species(0)
        k = Species(1)
        create_A = reactions.Creation(A, k)
```

For this example, there are other alternatives:

```python
class Nucleus(Compartment):
    A = Species(0)
    k = Species(1)
    create_A = reactions.Creation(A, k)


class Cell(Compartment):
    A = Species(0)
    k = Species(1)
    create_A = reactions.Creation(A, k)
    Nucleus = Nucleus
```
