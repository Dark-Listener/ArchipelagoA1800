from typing import Optional, TYPE_CHECKING

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, START_REGION, TriggerConditionType, UnlockType
from ._EventItems import A1800EventItem
from ._EventLocations import A1800EventLocation
from ._Requirement import A1800Requirement
from ._TriggerCondition import TriggerCondition
from ._Unlocks import A1800Unlock

if TYPE_CHECKING:
    from . import A1800Data


class Logic:
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: dict[str, set[A1800Requirement]] = {}
    _victory_condition: TriggerCondition = TriggerCondition.TRUE()

    def __init__(self, A1800_DATA: "A1800Data") -> None:
        self._A1800_DATA = A1800_DATA

        self._required_population = {
            (population.name, population.region): (population, amount) for name, amount in self._A1800_DATA.get_parsed_options().required_population.items()
            for population in self._A1800_DATA.find_populations(name)
        }

        self._required_buildings = {
            (unlock.name, unlock.region): (unlock, amount) for name, amount in self._A1800_DATA.get_parsed_options().required_skyscrapers.items()
            for unlock in self._A1800_DATA.find_unlocks(name)
        } | {
            (unlock.name, unlock.region): (unlock, 1) for name, region in self._A1800_DATA.get_parsed_options().required_monuments
            for unlock in self._A1800_DATA.find_unlocks(name, region or NO_REGION)
        }

    def _get_victory_condition(self) -> tuple[set[A1800Requirement], TriggerCondition, DLC]:
        victory_required_items: set[A1800Requirement] = set()
        victory_conditions: list[TriggerCondition] = []
        victory_dlcs: DLC = DLC.VANILLA
        for required_population in self._required_population.values():
            population, amount = required_population
            supplied = False
            luxury = False
            lifestyle = False

            victory_required_items.add(self._A1800_DATA.make_requirement(population.name, population.region))
            victory_conditions.append(TriggerCondition.POPULATION(
                population.name, population.region, amount, guid=population.guid))
            assert len(population.dlc) == 1, \
                f"Victory condition requested population {population.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(population.dlc))

            if supplied or luxury or lifestyle:
                residence = self._A1800_DATA.get_primary_residence(population.name, population.region)

                if supplied:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(consumption, population.region)
                                                  for consumption in residence.consumption)
                if luxury:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(luxury, population.region)
                                                  for luxury in residence.luxury)
                if lifestyle:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(lifestyle, population.region)
                                                  for lifestyle in residence.lifestyle)

        for required_building in self._required_buildings.values():
            unlock, amount = required_building
            supplied = False
            luxury = False
            lifestyle = False

            victory_required_items |= self.get_requirements_for_construction(unlock)
            victory_conditions.append(TriggerCondition.COUNTER(
                unlock.name, unlock.region, amount, guid=unlock.guids[0]))
            assert len(unlock.dlc) == 1, \
                f"Victory condition requested building {unlock.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(unlock.dlc))

            if UnlockType.RESIDENCE in unlock.type_ and (supplied or luxury or lifestyle):
                if supplied:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(consumption, unlock.region)
                                                  for consumption in unlock.consumption)
                if luxury:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(luxury, unlock.region)
                                                  for luxury in unlock.luxury)
                if lifestyle:
                    victory_required_items |= set(self._A1800_DATA.make_requirement(lifestyle, unlock.region)
                                                  for lifestyle in unlock.lifestyle)

        assert len(victory_conditions), "No victory subconditions could be created, goal would be immediately reached!"
        if len(victory_conditions) == 1:
            victory_condition = victory_conditions[0]
        else:
            victory_condition = TriggerCondition.ALL(*victory_conditions)

        if victory_dlcs != DLC.VANILLA and DLC.VANILLA in victory_dlcs:
            victory_dlcs ^= DLC.VANILLA

        return victory_required_items, victory_condition, victory_dlcs

    def _generate_requirements_and_rules(
        self,
        to_check: set[A1800Requirement],
        checked: set[A1800Requirement],
        checked_regions: Region,
        location_requirements: dict[str, set[A1800Requirement]]
    ) -> tuple[set[A1800Requirement], dict[str, set[A1800Requirement]]]:
        while to_check:
            requirement = to_check.pop()
            checked.add(requirement)

            new_requirements: set[A1800Requirement] = set()
            if requirement.type == RequirementType.PRODUCT:
                event_item = next(self._A1800_DATA.find_event_items(requirement.name, requirement.region), None)
                if event_item:
                    for event_location_name in event_item.locations:
                        for event_location in self._A1800_DATA.find_event_locations(event_location_name, event_item.name, event_item.region):
                            new_requirements.add(self._A1800_DATA.make_requirement(
                                event_location.name, event_location.region, type=RequirementType.UNLOCK))
                else:
                    raise ValueError(f"Requirement name {requirement.name} doesn't match any product.")

            elif requirement.type == RequirementType.UNLOCK:
                unlock = next(self._A1800_DATA.find_unlocks(requirement.name, requirement.region), None)
                if unlock:
                    new_requirements |= self.get_requirements_for_construction(unlock)

                    if UnlockType.BUILDING in unlock.type_:
                        new_requirements |= {self._A1800_DATA.make_requirement(
                            name, unlock.region) for name in unlock.maintenance}

                    if UnlockType.FACTORY in unlock.type_:
                        new_requirements |= {self._A1800_DATA.make_requirement(
                            name, region) for name, region in unlock.input}

                    for event_location in self._A1800_DATA.find_event_locations(requirement.name, region=requirement.region):
                        if event_location.ap_location_name in location_requirements:
                            assert location_requirements[event_location.ap_location_name] == new_requirements, \
                                f"Tried to add identical locations {event_location.ap_location_name} with differing "\
                                f"requirements: was: {location_requirements[event_location.ap_location_name]} "\
                                f"new: {new_requirements}"
                        else:
                            location_requirements[event_location.ap_location_name] = new_requirements

                    # Traverse region requirements, but don't add them to location rule
                    check_region = unlock.ap_region or unlock.region
                    if check_region ^ checked_regions != NO_REGION:
                        for region in [region for region in Region.__members__.values()
                                       if region in check_region & (check_region ^ checked_regions)]:
                            anno_region = self._A1800_DATA.find_region(region)
                            if anno_region:
                                new_requirements |= anno_region.requirements
                            checked_regions |= region
                else:
                    raise ValueError(
                        f"Requirement name {requirement.name} region {requirement.region.name} doesn't match any unlock.")

            else:
                raise ValueError(
                    f"Requirement type {requirement.type} of ({requirement.name, requirement.region.name}) isn't PRODUCT or UNLOCK.")

            for new_requirement in new_requirements:
                if not new_requirement in checked:
                    to_check.add(new_requirement)

        return checked, location_requirements

    def _is_progression(self, obj: A1800Unlock | A1800EventItem | A1800EventLocation) -> bool:
        requirement_type = RequirementType.PRODUCT if isinstance(obj, A1800EventItem) else RequirementType.UNLOCK

        if isinstance(obj, A1800EventLocation):
            return bool(next((
                requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
                and requirement.name == obj.name and requirement.region in obj.region), None)) and \
                self._is_progression(next(self._A1800_DATA.find_event_items(obj.output, obj.region)))
        else:
            return bool(next((
                requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
                and requirement.name == obj.name and requirement.region in obj.region), None))

    def _get_requirements_from_condition(self, condition: TriggerCondition) -> Optional[set[A1800Requirement]]:
        match(condition.type_):
            case TriggerConditionType.TRUE:
                return set()
            case TriggerConditionType.FALSE:
                assert False, "TriggerConditionType FALSE should never be used for unlocks"
            case TriggerConditionType.ALL:
                return {requirement for subcondition in condition.conditions for requirement in self._get_requirements_from_condition(subcondition) or set()}
            case TriggerConditionType.LINEAR:
                return {requirement for subcondition in condition.conditions for requirement in self._get_requirements_from_condition(subcondition) or set()}
            case TriggerConditionType.ANY:
                return {requirement for subcondition in condition.conditions for requirement in self._get_requirements_from_condition(subcondition) or set()}
            case TriggerConditionType.SESSION_ENTER:
                return self._A1800_DATA.find_session(condition.session).requirements
            case TriggerConditionType.POPULATION:
                return {self._A1800_DATA.make_requirement(condition.population_name, condition.region)}
            case TriggerConditionType.POPULATION_HAPPINESS:
                populations = list(self._A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                assert len(populations) == 1, \
                    f"Condition {condition.type_.name} {condition.amount} {condition.product_name} has 0 or multiple "\
                    "population residences"
                population = populations[0]
                return {self._A1800_DATA.make_requirement(condition.population_name, condition.region)} | {self._A1800_DATA.make_requirement(name, population.region) for name in population.luxury}
            case TriggerConditionType.COUNTER:
                unlock = next(self._A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                region = self._A1800_DATA.find_region(condition.region)
                region_requirements: set[A1800Requirement] = region.requirements if region else set()
                return self.get_requirements_for_construction(unlock) | region_requirements | {self._A1800_DATA.make_requirement(name, region) for name, region in condition.requirements}
            case TriggerConditionType.COUNTER_GOOD_IN_REGION:
                a1800_region = self._A1800_DATA.find_region(condition.region)
                assert a1800_region, \
                    f"Condition {condition.type_.name} {condition.amount} {condition.product_name} in {condition.region.name} "\
                    f"has 0 or multiple regions"
                return {self._A1800_DATA.make_requirement(condition.product_name, condition.product_region)} | a1800_region.requirements
            case TriggerConditionType.COUNTER_GOOD_IN_STOCK:
                assert False, "TriggerConditionType COUNTER_GOOD_IN_STOCK should never be used for unlocks"
            case TriggerConditionType.COUNTER_EXPEDITION_SOLVED:
                return {self._A1800_DATA.make_requirement(name, region) for name, region in condition.requirements}
            case TriggerConditionType.UNLOCK:
                return {self._A1800_DATA.make_requirement(condition.unlock_name, condition.region, type=RequirementType.UNLOCK)}
            case TriggerConditionType.QUEST_COMPLETE:
                return {self._A1800_DATA.make_requirement(name, region) for name, region in condition.requirements}
            case TriggerConditionType.EVENT_ACTIVE:
                return {self._A1800_DATA.make_requirement(condition.product_name, condition.region)}
            case TriggerConditionType.OBJECT_POSITION:
                unlock = next(self._A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                target = next(self._A1800_DATA.find_unlocks(condition.target_name, condition.region))
                return self.get_requirements_for_construction(unlock) | self.get_requirements_for_construction(target)
            case TriggerConditionType.ITEM_SET_ACTIVE:
                unlock = next(self._A1800_DATA.find_unlocks(condition.unlock_name, condition.unlock_region))
                return {self._A1800_DATA.make_requirement(unlock.name, unlock.region)} | {self._A1800_DATA.make_requirement(name, unlock.region) for name in unlock.cost} | {self._A1800_DATA.make_requirement(name, region) for name, region in condition.requirements}
            case TriggerConditionType.FACTORY_PRODUCTIVITY:
                unlock = next(self._A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                return {self._A1800_DATA.make_requirement(unlock.name, unlock.region)} | {self._A1800_DATA.make_requirement(name, unlock.region) for name in unlock.cost | unlock.maintenance | {name for name, _ in unlock.input}}
            case TriggerConditionType.ACTIVE_DLC:
                assert False, "TriggerConditionType ACTIVE_DLC should never be used for unlocks"

    def get_requirements_for_construction(self, unlock: A1800Unlock) -> set[A1800Requirement]:
        new_requirements: set[A1800Requirement] = set()

        if not UnlockType.META in unlock.type_:
            new_requirements.add(self._A1800_DATA.make_requirement(
                unlock.name, unlock.region, type=RequirementType.UNLOCK))

        if UnlockType.BUILDING in unlock.type_:
            new_requirements |= {self._A1800_DATA.make_requirement(name, unlock.region) for name in unlock.cost}

        if UnlockType.FACTORY in unlock.type_:
            new_requirements |= {self._A1800_DATA.make_requirement(name, region) for name, region in unlock.input}

        is_upgrade = UnlockType.UPGRADE in unlock.type_
        current_unlock = unlock
        while is_upgrade:
            previous_unlock = next(self._A1800_DATA.find_unlocks(
                current_unlock.previous_building, current_unlock.region))
            new_requirements.add(self._A1800_DATA.make_requirement(previous_unlock.name,
                                 previous_unlock.region, type=RequirementType.UNLOCK))

            if UnlockType.RESIDENCE in unlock.type_:
                assert UnlockType.RESIDENCE in previous_unlock.type_, f"Residence {current_unlock.name} references"\
                    f" previous building {previous_unlock.name}, which is not also a residence"
                new_requirements |= {self._A1800_DATA.make_requirement(
                    name, previous_unlock.region) for name in previous_unlock.consumption}

            is_upgrade = UnlockType.UPGRADE in previous_unlock.type_
            current_unlock = previous_unlock

        return new_requirements

    def generate_logic(self) -> None:
        victory_required_items, self._victory_condition, self._victory_dlcs = self._get_victory_condition()

        if self._A1800_DATA.get_parsed_options().full_accessibility:
            initial_required_items = victory_required_items.copy() | {requirement for unlock in self._A1800_DATA.get_unlock_locations(
            ) for requirement in self._get_requirements_from_condition(unlock.condition) or set()}
        else:
            initial_required_items = victory_required_items.copy()

        victory_event_location = A1800EventLocation(
            self._victory_condition.ap_location_name, {DLC.VANILLA}, Region.OW, NO_REGION, "Victory", is_progression=True)
        self._A1800_DATA.append_event_location(victory_event_location)
        self._victory_condition.ap_location_name = "Victory Condition"

        for event_item in self._A1800_DATA.get_event_items():
            if event_item.name == "Victory":
                event_item.locations = {victory_event_location.name}

        initial_checked_items: set[A1800Requirement] = {self._A1800_DATA.make_requirement("Victory", ALL_REGIONS)}

        initial_location_requirements = {victory_event_location.ap_location_name: victory_required_items.copy()}

        self._a1800_required_items, self._a1800_location_requirements = self._generate_requirements_and_rules(
            initial_required_items, initial_checked_items, START_REGION, initial_location_requirements)

        for obj in list(self._A1800_DATA.get_unlocks()) + list(self._A1800_DATA.get_event_items()) + list(self._A1800_DATA.get_event_locations()):
            if self._is_progression(obj):
                obj.is_progression = True

    def get_location_requirements(self) -> dict[str, set[A1800Requirement]]:
        return self._a1800_location_requirements

    def get_victory_dlcs(self) -> DLC:
        return self._victory_dlcs

    def get_victory_condition(self) -> TriggerCondition:
        return self._victory_condition
