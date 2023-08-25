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
            kind=unit_kind_map[x.getKind()],
            exponent=x.getExponent(),
            scale=x.getScale(),
            multiplier=x.getMultiplier(),
        )


class _UnitKindMap(dict):
    def __getitem__(self, item) -> types.UnitKind:
        value = super().__getitem__(item)
        if isinstance(value, str):
            raise NotImplementedError(value)
        else:
            return value


unit_kind_map: dict[int, types.UnitKind] = _UnitKindMap(
    {
        libsbml.UNIT_KIND_AMPERE: types.UnitKind.ampere,
        libsbml.UNIT_KIND_COULOMB: types.UnitKind.coulomb,
        libsbml.UNIT_KIND_GRAY: types.UnitKind.gray,
        libsbml.UNIT_KIND_JOULE: types.UnitKind.joule,
        libsbml.UNIT_KIND_LITRE: types.UnitKind.litre,
        libsbml.UNIT_KIND_MOLE: types.UnitKind.mole,
        libsbml.UNIT_KIND_RADIAN: types.UnitKind.radian,
        libsbml.UNIT_KIND_STERADIAN: types.UnitKind.steradian,
        libsbml.UNIT_KIND_WEBER: types.UnitKind.weber,
        libsbml.UNIT_KIND_AVOGADRO: types.UnitKind.avogadro,
        libsbml.UNIT_KIND_DIMENSIONLESS: types.UnitKind.dimensionless,
        libsbml.UNIT_KIND_HENRY: types.UnitKind.henry,
        libsbml.UNIT_KIND_KATAL: types.UnitKind.katal,
        libsbml.UNIT_KIND_LUMEN: types.UnitKind.lumen,
        libsbml.UNIT_KIND_NEWTON: types.UnitKind.newton,
        libsbml.UNIT_KIND_SECOND: types.UnitKind.second,
        libsbml.UNIT_KIND_TESLA: types.UnitKind.tesla,
        libsbml.UNIT_KIND_BECQUEREL: types.UnitKind.becquerel,
        libsbml.UNIT_KIND_FARAD: types.UnitKind.farad,
        libsbml.UNIT_KIND_HERTZ: types.UnitKind.hertz,
        libsbml.UNIT_KIND_KELVIN: types.UnitKind.kelvin,
        libsbml.UNIT_KIND_LUX: types.UnitKind.lux,
        libsbml.UNIT_KIND_OHM: types.UnitKind.ohm,
        libsbml.UNIT_KIND_SIEMENS: types.UnitKind.siemens,
        libsbml.UNIT_KIND_VOLT: types.UnitKind.volt,
        libsbml.UNIT_KIND_CANDELA: types.UnitKind.candela,
        libsbml.UNIT_KIND_GRAM: types.UnitKind.gram,
        libsbml.UNIT_KIND_ITEM: types.UnitKind.item,
        libsbml.UNIT_KIND_KILOGRAM: types.UnitKind.kilogram,
        libsbml.UNIT_KIND_METRE: types.UnitKind.metre,
        libsbml.UNIT_KIND_PASCAL: types.UnitKind.pascal,
        libsbml.UNIT_KIND_SIEVERT: types.UnitKind.sievert,
        libsbml.UNIT_KIND_WATT: types.UnitKind.watt,
        libsbml.UNIT_KIND_LITER: types.UnitKind.litre,
        libsbml.UNIT_KIND_METER: types.UnitKind.metre,
        libsbml.UNIT_KIND_CELSIUS: "UNIT_KIND_CELSIUS",
        libsbml.UNIT_KIND_INVALID: "UNIT_KIND_INVALID",
    }
)
