# Domain-Specific Language (DSL)

To define a model, we implemented a Domain-Specify Language (DSL) with metaclasses. The syntax is as follows:

```python
class ModelA(Compartment):
    A = Species(0)
    k = Parameter(1)
    create_A = reactions.Creation(A, k)
```

## Extend model

To extend a model, we can subclass from it:

```python
class ExtendedModelA(ModelA):
    B = Species(0)
```

where we added a new `Species`. It is equivalent to writing:

```python
class ExtendedModelA(Compartment):
    A = Species(0)
    k = Parameter(1)
    create_A = reactions.Creation(A, k)
    B = Species(0)
```

## Extending models using previous components

When extending a previous model, we don't have access to previously defined components in the new class namespace. For instance, if we tried to do this:

```python
class ExtendedModelA(ModelA):
    B = Species(0)
    create_B = reactions.Creation(A, k)  # k in this line
```

the IDE will flag that `k` isn't yet defined. While we can inject it with the metaclass, it would be preferrable to make it more explicit.

There are three possible solutions:

### Solution 1: reference directly from inherited model

```python
class ExtendedModelA(ModelA):
    B = Species(0)
    create_B = reactions.Creation(A, ModelA.k)
```

### Solution 2: define a class annotation

To avoid mistaking it with a global variable, all upstream components to be used must be defined as a class annotation. If `k` isn't defined in one of the bases, it will raise a `NameError`.

```python
class ExtendedModelA(ModelA):
    k: Parameter

    B = Species(0)
    create_B = reactions.Creation(A, k)
```

Disadvantage of this approach:

- "go to definition" stp\[s at the type annotation `k: Parameter` instead of continuing into `ModelA.k`.
- Renaming `ModelA.k` with refactoring tools won't rename `k` in `ExtendedModelA`.

### Solution 3: Self type (Python 3.11)

Other solution is to define a helper `Self` type as:

```python
T = typing.TypeVarTuple("T")


def Self(*cls: *T) -> typing.Union[*T]:
    pass
```

and do this:

```python
class ExtendedModel(ModelA):
    self = Self(ModelA)

    B = Species(0)
    create_B = reactions.Creation(A, self.k)
```

Advantages of this approach:

- "Go to definition" goes to `ModelA`.

Disadvanges of this approach:

- Refactoring tools' "Rename" is tricky when inheriting from multiple models.

## Combining models

We can define another model and combine them using the subclass syntax:

```python
class ModelB(Compartment):
    B = Species(0)
    k = Parameter(1)
    create_B = reactions.Creation(B, k)


class Combined(ModelA, ModelB):
    pass
```

which is equivalent to writing:

```python
class Combined(Compartment):
    A = Species(0)
    k = Parameter(1)
    create_A = reactions.Creation(A, k)
    B = Species(0)
    # k = Parameter(1)
    create_B = reactions.Creation(B, k)
```

We could also have used the union set operator:

```python
assert Combined == (ModelA | ModelB)
```

but, using the subclass syntax allows to obtain type-completitions for `Combined`.

## Collision between models

If the models have collisions between their components, it raises an exception, such as in this case:

```python
class ModelA(Compartment):
    A = Species(0)


class ModelB(Compartment):
    A = Species(1)


class Combined(ModelA, ModelB):
    pass
```

we need to override it.

### Solution 1: reference directly from upstream model

```python
class Combined(ModelA, ModelB):
    A = ModelA.A.replace(1)

    # it would also work from ModelB:
    # A = ModelB.A.replace(1)
```

### Solution 2: add a type annotation

```python
class Combined(ModelA, ModelB):
    A: Species = Species(1)
```

or

```python
class Combined(ModelA, ModelB):
    A: Species
    A = A.replace(1)
```

Solution 1 is more explicit, while Solution 2 is similar to the previous Solution 2 for reusing previously defined components.

## Renaming components

```python
class RenamedModel(ModelA):
    A: Species
    B = A.rename()
```

## Deleting components

### Option 1

```python
class RenamedModel(ModelA):
    A = ModelA.remove()
```

### Option 2

```python
class RenamedModel(ModelA):
    A: Species
    A = A.remove()
```

### Option 3

```python
class RenamedModel(ModelA):
    A: Species
    del A
```

### Option 4

```python
class RenamedModel(ModelA):
    del A
```

Option 4, is the only one in which static type hints (in VSCode) show no `A` for RenamedModel. But also show a undefined name warning.

## MRO: Method Resolution Order

We override the standard `type.mro` of Python classes.
