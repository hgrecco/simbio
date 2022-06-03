# from simbio.components import InReactionSpecies, ReactionBalance, Species
# from pytest import raises


# @test("Species to InReactionSpecies")
# def _():
#     A = Species(0, name="A")

#     assert isinstance(A, Species)

#     for k in (1.0, 2.0):
#         Ak = k * A

#         assert isinstance(Ak, InReactionSpecies)
#         assert A in Ak
#         assert Ak[A] == k

#         assert (2.0 * Ak)[A] == 2.0 * k

#     assert (1.0 * A) is not (1.0 * A)
#     assert (1.0 * A) == (1.0 * A)


# @test("Species cannot form reactions")
# def _():
#     A = Species(0, name="A")

#     with raises(TypeError):
#         A + A

#     with raises(TypeError):
#         A >> A


# @test("Addition and multiplication of InReactionSpecies")
# def _():
#     A = Species(0, name="A")
#     B = Species(0, name="B")

#     X = 1 * A + 1 * B
#     assert isinstance(X, InReactionSpecies)
#     assert X == {A: 1, B: 1}

#     Y = X + 1 * A
#     assert isinstance(Y, InReactionSpecies)
#     assert Y == {A: 2, B: 1}

#     Z = 2 * X
#     assert isinstance(Z, InReactionSpecies)
#     assert Z == {A: 2, B: 2}


# @test("Null-term in reaction")
# def _():
#     A = Species(0, name="A")

#     reaction = None >> 1 * A
#     assert reaction.reactants == {}
#     assert reaction.products == {A: 1}

#     reaction = 1 * A >> None
#     assert reaction.reactants == {A: 1}
#     assert reaction.products == {}


# @test("Reactants and products")
# def _():
#     A = Species(0, name="A")
#     B = Species(0, name="B")
#     C = Species(0, name="C")
#     D = Species(0, name="D")

#     # Simple reaction
#     reaction = 1 * A >> 1 * B
#     assert isinstance(reaction, ReactionBalance)
#     assert reaction.reactants == {A: 1}
#     assert reaction.products == {B: 1}
#     assert reaction.change == {A: -1, B: +1}

#     # Multiple reaction
#     reaction = 1 * A + 1 * B >> 1 * C + 1 * D
#     assert reaction.reactants == {A: 1, B: 1}
#     assert reaction.products == {C: 1, D: 1}
#     assert reaction.change == {A: -1, B: -1, C: +1, D: +1}

#     # Non-unit stoichiometric coefficients
#     reaction = 2 * A >> 3 * B
#     assert reaction.reactants == {A: 2}
#     assert reaction.products == {B: 3}
#     assert reaction.change == {A: -2, B: +3}

#     reaction = 2 * A + 3 * B >> 4 * C + 5 * D
#     assert reaction.reactants == {A: 2, B: 3}
#     assert reaction.products == {C: 4, D: 5}
#     assert reaction.change == {A: -2, B: -3, C: +4, D: +5}

#     # Same species at both sides
#     reaction = 2 * A >> 3 * A
#     assert reaction.reactants == {A: 2}
#     assert reaction.products == {A: 3}
#     assert reaction.change == {A: +1}
