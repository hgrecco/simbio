---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.14.0
kernelspec:
  display_name: Python 3.10.6 64-bit ('simbio')
  language: python
  name: python3
---

# Defining new reactions

SimBio includes a comprehensive set of predefined reactions
that relate reactants with products
and a well defined kinetics.
But,
new reactions can be easily defined,
to extend SimBio's capabilities.

There are two main types of reactions,

- `SingleReaction`, which models elementary chemical reactions,
- `ReactionGroup`, which consists of multiple `SingleReaction` and/or `ReactionGroup`.

+++

## Single reactions

A `SingleReaction`
converting species $A$ and $B$ to $C$,

$$ n_A A + n_B B \xrightarrow{k} n_C C $$

where $n_A$, $n_B$, and $n_C$ are the stoichiometric coefficients,
corresponds to the following differential equations:

$$
\begin{cases}
\frac{dA}{dt} = -n_A \; R(t, A^{n_A}, B^{n_B}, k) \\
\frac{dB}{dt} = -n_B \; R(t, A^{n_A}, B^{n_B}, k) \\
\frac{dC}{dt} = +n_C \; R(t, A^{n_A}, B^{n_B}, k)
\end{cases}
$$

where $R(t, A, B, k)$ is the reaction rate.

For a reaction following mass action kinetics,
the reaction rate is

$$ R(t, A, B, k) = k A B $$

For a Michaelis-Menten reaction,

$$ S + E ↔ ES → P + E $$

where an enzyme $E$ converts a substrate $S$ to a product $P$,
under certain assumptions can be modeled as a single-step reaction with rate:

$$ R(t, S, V_{max}, K_M) = V_{max} * S / (K_M + S) $$

To define a `SingleReaction`,
we need to declare the species and parameters it relates,
which corresponds to reactants and products,
and the reaction rate function:

```{code-cell} ipython3
from simbio.components import SingleReaction, Species, Parameter


class Synthesis(SingleReaction):
    """A + B → AB"""
    A: Species
    B: Species
    AB: Species
    rate: Parameter

    def reactants(self):
        return (self.A, self.B)

    def products(self):
        return (self.AB,)

    @staticmethod
    def reaction_rate(t, A, B, rate):
        return rate * A * B
```

## Compound reactions

Compound reactions are a convenience to englobe a series of reactions into one.
They can be composed of many single or compound reactions.
For instance,
the `MichaelisMenten` reaction,

$$ S + E ↔ ES → P + E $$

which is included in `simbio.reactions.enzymatic`,
is defined as follows:

```{code-cell} ipython3
from simbio.components import ReactionGroup, Species, Parameter
from simbio.reactions.compound import ReversibleSynthesis
from simbio.reactions.single import Dissociation


class MichaelisMenten(ReactionGroup):
    """S + E ↔ ES → P + E"""
    E: Species
    S: Species
    ES: Species
    P: Species
    forward_rate: Parameter
    reverse_rate: Parameter
    catalytic_rate: Parameter

    binding_reaction = ReversibleSynthesis(
        A=E,
        B=S,
        AB=ES,
        forward_rate=forward_rate,
        reverse_rate=reverse_rate,
    )
    dissociation_reaction = Dissociation(
        AB=ES,
        A=E,
        B=P,
        rate=catalytic_rate,
    )
```
