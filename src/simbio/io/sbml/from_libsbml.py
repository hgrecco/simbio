from dataclasses import asdict
from functools import singledispatch

import libsbml

from ..mathML import from_mathML
from . import types


@singledispatch
def convert(x):
    raise NotImplementedError(type(x))


@convert.register
def NoneType(x: None):
    return None


@convert.register
def ListOf(x: libsbml.ListOf) -> list:
    return list(map(convert, x))


@convert.register
def Math(x: libsbml.ASTNode):
    return from_mathML(x)


def Base(x: libsbml.SBase) -> types.Base:
    return types.Base(
        id=types.ID(x.getId()) if x.isSetId() else None,
        name=x.getName() if x.isSetName() else None,
        meta_id=x.getMetaId() if x.isSetMetaId() else None,
        sbo_term=x.getSBOTerm() if x.isSetSBOTerm() else None,
        notes=x.getNotesString() if x.isSetNotes() else None,
        annotation=x.getAnnotationString() if x.isSetAnnotation() else None,
    )


@convert.register
def Model(x: libsbml.Model) -> types.Model:
    return types.Model(
        **asdict(Base(x)),
        substance_units=x.getSubstanceUnits() if x.isSetSubstanceUnits() else None,
        time_units=x.getTimeUnits() if x.isSetTimeUnits() else None,
        volume_units=x.getVolumeUnits() if x.isSetVolumeUnits() else None,
        area_units=x.getAreaUnits() if x.isSetAreaUnits() else None,
        length_units=x.getLengthUnits() if x.isSetLengthUnits() else None,
        extent_units=x.getExtentUnits() if x.isSetExtentUnits() else None,
        conversion_factor=x.getConversionFactor()
        if x.isSetConversionFactor()
        else None,
        functions=convert(x.getListOfFunctionDefinitions()),
        units=convert(x.getListOfUnitDefinitions()),
        compartments=convert(x.getListOfCompartments()),
        species=convert(x.getListOfSpecies()),
        parameters=convert(x.getListOfParameters()),
        initial_assignments=convert(x.getListOfInitialAssignments()),
        rules=convert(x.getListOfRules()),
        constraints=convert(x.getListOfConstraints()),
        reactions=convert(x.getListOfReactions()),
        events=convert(x.getListOfEvents()),
    )


@convert.register
def Parameter(x: libsbml.Parameter) -> types.Parameter:
    # x.isSetConstant()
    return types.Parameter(
        **asdict(Base(x)),
        value=x.getValue() if x.isSetValue() else None,
        units=x.getUnits() if x.isSetUnits() else None,
        constant=x.getConstant(),
    )


@convert.register
def LocalParameter(x: libsbml.LocalParameter) -> types.LocalParameter:
    return types.LocalParameter(
        **asdict(Base(x)),
        value=x.getValue() if x.isSetValue() else None,
        units=x.getUnits() if x.isSetUnits() else None,
    )


@convert.register
def Species(x: libsbml.Species) -> types.Species:
    # x.isSetCompartment()
    # x.isSetHasOnlySubstanceUnits()
    # x.isSetBoundaryCondition()
    # x.isSetConstant()
    return types.Species(
        **asdict(Base(x)),
        compartment=x.getCompartment(),
        initial_amount=x.getInitialAmount() if x.isSetInitialAmount() else None,
        initial_concentration=x.getInitialConcentration()
        if x.isSetInitialConcentration()
        else None,
        substance_units=x.getSubstanceUnits() if x.isSetSubstanceUnits() else None,
        has_only_substance_units=x.getHasOnlySubstanceUnits(),
        boundary_condition=x.getBoundaryCondition(),
        constant=x.getConstant(),
        conversion_factor=x.getConversionFactor()
        if x.isSetConversionFactor()
        else None,
    )


@convert.register
def Compartment(x: libsbml.Compartment) -> types.Compartment:
    # x.isSetConstant()
    return types.Compartment(
        **asdict(Base(x)),
        spatial_dimensions=x.getSpatialDimensions()
        if x.isSetSpatialDimensions()
        else None,
        size=x.getSize() if x.isSetSize() else None,
        units=x.getUnits() if x.isSetUnits() else None,
        constant=x.getConstant(),
    )


@convert.register
def Event(x: libsbml.Event) -> types.Event:
    # x.isSetUseValuesFromTriggerTime()
    return types.Event(
        **asdict(Base(x)),
        use_values_from_trigger_time=x.getUseValuesFromTriggerTime(),
        trigger=convert(x.getTrigger()),
        prority=convert(x.getPriority()),
        delay=convert(x.getDelay()),
        assignments=convert(x.getListOfEventAssignments()),
    )


@convert.register
def Priority(x: libsbml.Priority) -> types.Priority:
    # x.isSetMath()
    return types.Priority(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def Delay(x: libsbml.Delay) -> types.Delay:
    # x.isSetMath()
    return types.Delay(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def EventAssignment(x: libsbml.EventAssignment) -> types.EventAssignment:
    # x.isSetMath()
    return types.EventAssignment(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def FunctionDefinition(x: libsbml.FunctionDefinition) -> types.FunctionDefinition:
    # x.isSetMath()
    return types.FunctionDefinition(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def InitialAssignment(x: libsbml.InitialAssignment) -> types.InitialAssignment:
    # x.isSetSymbol()
    # x.isSetMath()
    return types.InitialAssignment(
        **asdict(Base(x)),
        symbol=x.getSymbol(),
        math=convert(x.getMath()),
    )


@convert.register
def Rule(x: libsbml.Rule) -> types.Rule:
    # x.isSetMath()
    return types.Rule(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def AlgebraicRule(x: libsbml.AlgebraicRule) -> types.AlgebraicRule:
    # x.isSetMath()
    return types.AlgebraicRule(
        **asdict(Base(x)),
        math=convert(x.getMath()),
    )


@convert.register
def AssignmentRule(x: libsbml.AssignmentRule) -> types.AssignmentRule:
    # x.isSetMath()
    # x.isSetVariable()
    return types.AssignmentRule(
        **asdict(Base(x)),
        math=convert(x.getMath()),
        variable=x.getVariable(),
    )


@convert.register
def RateRule(x: libsbml.RateRule) -> types.RateRule:
    # x.isSetMath()
    # x.isSetVariable()
    return types.RateRule(
        **asdict(Base(x)),
        math=convert(x.getMath()),
        variable=x.getVariable(),
    )


@convert.register
def Constraint(x: libsbml.Constraint) -> types.Constraint:
    # x.isSetMath()
    # x.isSetMessageString()
    return types.Constraint(
        **asdict(Base(x)),
        math=convert(x.getMath()),
        message=x.getMessageString(),
    )


@convert.register
def Reaction(x: libsbml.Reaction) -> types.Reaction:
    # x.isSetReversible()
    return types.Reaction(
        **asdict(Base(x)),
        reversible=x.getReversible(),
        compartment=x.getCompartment() if x.isSetCompartment() else None,
        reactants=convert(x.getListOfReactants()),
        products=convert(x.getListOfProducts()),
        modifiers=convert(x.getListOfModifiers()),
        kinetic_law=convert(x.getKineticLaw()),
    )


@convert.register
def SimpleSpeciesReference(
    x: libsbml.SimpleSpeciesReference,
) -> types.SimpleSpeciesReference:
    return types.SimpleSpeciesReference(
        **asdict(Base(x)),
        species=types.ID(x.getSpecies()),
    )


@convert.register
def ModifierSpeciesReference(
    x: libsbml.ModifierSpeciesReference,
) -> types.ModifierSpeciesReference:
    return types.ModifierSpeciesReference(
        **asdict(Base(x)),
        species=types.ID(x.getSpecies()),
    )


@convert.register
def SpeciesReference(x: libsbml.SpeciesReference) -> types.SpeciesReference:
    # x.isSetConstant()
    return types.SpeciesReference(
        **asdict(Base(x)),
        species=types.ID(x.getSpecies()),
        stoichiometry=x.getStoichiometry() if x.isSetStoichiometry() else None,
        constant=x.getConstant(),
    )


@convert.register
def KineticLaw(x: libsbml.KineticLaw) -> types.KineticLaw:
    # x.isSetMath()
    return types.KineticLaw(
        **asdict(Base(x)),
        math=convert(x.getMath()),
        parameters=convert(x.getListOfParameters()),
    )


@convert.register
def Trigger(x: libsbml.Trigger) -> types.Trigger:
    # x.isSetInitialValue()
    # x.isSetPersistent()
    # x.isSetMath()
    return types.Trigger(
        **asdict(Base(x)),
        initial_value=x.getInitialValue(),
        persistent=x.getPersistent(),
        math=convert(x.getMath()),
    )


@convert.register
def UnitDefinition(x: libsbml.UnitDefinition) -> types.UnitDefinition:
    return types.UnitDefinition(
        **asdict(Base(x)),
        units=convert(x.getListOfUnits()),
    )


@convert.register
def Unit(x: libsbml.Unit) -> types.Unit:
    # x.isSetKind()
    # x.isSetExponent()
    # x.isSetScale()
    # x.isSetMultiplier()
    return types.Unit(
        kind=types.UnitKind(x.getKind()),
        exponent=x.getExponent(),
        scale=x.getScale(),
        multiplier=x.getMultiplier(),
    )
