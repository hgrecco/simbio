from dataclasses import asdict
from functools import singledispatchmethod

import libsbml

from ..mathML import mathMLImporter
from . import types


class Converter:
    def __init__(self):
        self.mathML = mathMLImporter()

    @singledispatchmethod
    def convert(self, x):
        raise NotImplementedError(type(x))

    @convert.register
    def NoneType(self, x: None):
        return None

    @convert.register
    def ListOf(self, x: libsbml.ListOf) -> list:
        return list(map(self.convert, x))

    @convert.register
    def Math(self, x: libsbml.ASTNode):
        return self.mathML.convert(x)

    @convert.register
    def FunctionDefinition(
        self, x: libsbml.FunctionDefinition
    ) -> types.FunctionDefinition:
        # x.isSetMath()
        return types.FunctionDefinition(
            **asdict(self.Base(x)),
            math=self.mathML.compile_function(x.getId(), x.getMath()),
        )

    def Base(self, x: libsbml.SBase) -> types.Base:
        return types.Base(
            id=types.ID(x.getId()) if x.isSetId() else None,
            name=x.getName() if x.isSetName() else None,
            meta_id=x.getMetaId() if x.isSetMetaId() else None,
            sbo_term=x.getSBOTerm() if x.isSetSBOTerm() else None,
            notes=x.getNotesString() if x.isSetNotes() else None,
            annotation=x.getAnnotationString() if x.isSetAnnotation() else None,
        )

    @convert.register
    def Model(self, x: libsbml.Model) -> types.Model:
        return types.Model(
            **asdict(self.Base(x)),
            substance_units=x.getSubstanceUnits() if x.isSetSubstanceUnits() else None,
            time_units=x.getTimeUnits() if x.isSetTimeUnits() else None,
            volume_units=x.getVolumeUnits() if x.isSetVolumeUnits() else None,
            area_units=x.getAreaUnits() if x.isSetAreaUnits() else None,
            length_units=x.getLengthUnits() if x.isSetLengthUnits() else None,
            extent_units=x.getExtentUnits() if x.isSetExtentUnits() else None,
            conversion_factor=x.getConversionFactor()
            if x.isSetConversionFactor()
            else None,
            functions=self.convert(x.getListOfFunctionDefinitions()),
            units=self.convert(x.getListOfUnitDefinitions()),
            compartments=self.convert(x.getListOfCompartments()),
            species=self.convert(x.getListOfSpecies()),
            parameters=self.convert(x.getListOfParameters()),
            initial_assignments=self.convert(x.getListOfInitialAssignments()),
            rules=self.convert(x.getListOfRules()),
            constraints=self.convert(x.getListOfConstraints()),
            reactions=self.convert(x.getListOfReactions()),
            events=self.convert(x.getListOfEvents()),
        )

    @convert.register
    def Parameter(self, x: libsbml.Parameter) -> types.Parameter:
        # x.isSetConstant()
        return types.Parameter(
            **asdict(self.Base(x)),
            value=x.getValue() if x.isSetValue() else None,
            units=x.getUnits() if x.isSetUnits() else None,
            constant=x.getConstant(),
        )

    @convert.register
    def LocalParameter(self, x: libsbml.LocalParameter) -> types.LocalParameter:
        return types.LocalParameter(
            **asdict(self.Base(x)),
            value=x.getValue() if x.isSetValue() else None,
            units=x.getUnits() if x.isSetUnits() else None,
        )

    @convert.register
    def Species(self, x: libsbml.Species) -> types.Species:
        # x.isSetCompartment()
        # x.isSetHasOnlySubstanceUnits()
        # x.isSetBoundaryCondition()
        # x.isSetConstant()
        return types.Species(
            **asdict(self.Base(x)),
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
    def Compartment(self, x: libsbml.Compartment) -> types.Compartment:
        # x.isSetConstant()
        return types.Compartment(
            **asdict(self.Base(x)),
            spatial_dimensions=x.getSpatialDimensions()
            if x.isSetSpatialDimensions()
            else None,
            size=x.getSize() if x.isSetSize() else None,
            units=x.getUnits() if x.isSetUnits() else None,
            constant=x.getConstant(),
        )

    @convert.register
    def Event(self, x: libsbml.Event) -> types.Event:
        # x.isSetUseValuesFromTriggerTime()
        return types.Event(
            **asdict(self.Base(x)),
            use_values_from_trigger_time=x.getUseValuesFromTriggerTime(),
            trigger=self.convert(x.getTrigger()),
            prority=self.convert(x.getPriority()),
            delay=self.convert(x.getDelay()),
            assignments=self.convert(x.getListOfEventAssignments()),
        )

    @convert.register
    def Priority(self, x: libsbml.Priority) -> types.Priority:
        # x.isSetMath()
        return types.Priority(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def Delay(self, x: libsbml.Delay) -> types.Delay:
        # x.isSetMath()
        return types.Delay(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def EventAssignment(self, x: libsbml.EventAssignment) -> types.EventAssignment:
        # x.isSetMath()
        return types.EventAssignment(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def InitialAssignment(
        self, x: libsbml.InitialAssignment
    ) -> types.InitialAssignment:
        # x.isSetSymbol()
        # x.isSetMath()
        return types.InitialAssignment(
            **asdict(self.Base(x)),
            symbol=x.getSymbol(),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def Rule(self, x: libsbml.Rule) -> types.Rule:
        # x.isSetMath()
        return types.Rule(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def AlgebraicRule(self, x: libsbml.AlgebraicRule) -> types.AlgebraicRule:
        # x.isSetMath()
        return types.AlgebraicRule(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def AssignmentRule(self, x: libsbml.AssignmentRule) -> types.AssignmentRule:
        # x.isSetMath()
        # x.isSetVariable()
        return types.AssignmentRule(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
            variable=x.getVariable(),
        )

    @convert.register
    def RateRule(self, x: libsbml.RateRule) -> types.RateRule:
        # x.isSetMath()
        # x.isSetVariable()
        return types.RateRule(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
            variable=x.getVariable(),
        )

    @convert.register
    def Constraint(self, x: libsbml.Constraint) -> types.Constraint:
        # x.isSetMath()
        # x.isSetMessageString()
        return types.Constraint(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
            message=x.getMessageString(),
        )

    @convert.register
    def Reaction(self, x: libsbml.Reaction) -> types.Reaction:
        # x.isSetReversible()
        return types.Reaction(
            **asdict(self.Base(x)),
            reversible=x.getReversible(),
            compartment=x.getCompartment() if x.isSetCompartment() else None,
            reactants=self.convert(x.getListOfReactants()),
            products=self.convert(x.getListOfProducts()),
            modifiers=self.convert(x.getListOfModifiers()),
            kinetic_law=self.convert(x.getKineticLaw()),
        )

    @convert.register
    def SimpleSpeciesReference(
        self,
        x: libsbml.SimpleSpeciesReference,
    ) -> types.SimpleSpeciesReference:
        return types.SimpleSpeciesReference(
            **asdict(self.Base(x)),
            species=types.ID(x.getSpecies()),
        )

    @convert.register
    def ModifierSpeciesReference(
        self,
        x: libsbml.ModifierSpeciesReference,
    ) -> types.ModifierSpeciesReference:
        return types.ModifierSpeciesReference(
            **asdict(self.Base(x)),
            species=types.ID(x.getSpecies()),
        )

    @convert.register
    def SpeciesReference(self, x: libsbml.SpeciesReference) -> types.SpeciesReference:
        # x.isSetConstant()
        return types.SpeciesReference(
            **asdict(self.Base(x)),
            species=types.ID(x.getSpecies()),
            stoichiometry=x.getStoichiometry() if x.isSetStoichiometry() else None,
            constant=x.getConstant(),
        )

    @convert.register
    def KineticLaw(self, x: libsbml.KineticLaw) -> types.KineticLaw:
        # x.isSetMath()
        return types.KineticLaw(
            **asdict(self.Base(x)),
            math=self.convert(x.getMath()),
            parameters=self.convert(x.getListOfParameters()),
        )

    @convert.register
    def Trigger(self, x: libsbml.Trigger) -> types.Trigger:
        # x.isSetInitialValue()
        # x.isSetPersistent()
        # x.isSetMath()
        return types.Trigger(
            **asdict(self.Base(x)),
            initial_value=x.getInitialValue(),
            persistent=x.getPersistent(),
            math=self.convert(x.getMath()),
        )

    @convert.register
    def UnitDefinition(self, x: libsbml.UnitDefinition) -> types.UnitDefinition:
        return types.UnitDefinition(
            **asdict(self.Base(x)),
            units=self.convert(x.getListOfUnits()),
        )

    @convert.register
    def Unit(self, x: libsbml.Unit) -> types.Unit:
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
