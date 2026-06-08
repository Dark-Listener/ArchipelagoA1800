from typing import Optional

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, START_REGION, TriggerConditionType, UnlockType
from ._EventItems import A1800EventItem, EVENT_ITEMS
from ._EventLocations import A1800EventLocation, EVENT_LOCATIONS
from ._ParsedOptions import ParsedOptions
from ._Products import PRODUCTS
from ._Regions import REGIONS
from ._Requirement import A1800Requirement
from ._Sessions import SESSIONS
from ._TriggerCondition import TriggerCondition
from ._Unlocks import A1800Unlock, UNLOCKS


def get_requirements_for_construction(unlock: A1800Unlock) -> set[A1800Requirement]:
    new_requirements: set[A1800Requirement] = set()

    if not UnlockType.META in unlock.type_:
        new_requirements.add(A1800Requirement(unlock.name, unlock.region, RequirementType.UNLOCK))

    if UnlockType.BUILDING in unlock.type_:
        new_requirements |= {A1800Requirement(name, unlock.region) for name in unlock.cost}

    if UnlockType.FACTORY in unlock.type_:
        new_requirements |= {A1800Requirement(name, region) for name, region in unlock.input}

    is_upgrade = UnlockType.UPGRADE in unlock.type_
    current_unlock = unlock
    while is_upgrade:
        previous_unlock = next(UNLOCKS.find_unlocks(
            current_unlock.previous_building, current_unlock.region))
        new_requirements.add(A1800Requirement(previous_unlock.name,
                                              previous_unlock.region, RequirementType.UNLOCK))

        if UnlockType.RESIDENCE in unlock.type_:
            assert UnlockType.RESIDENCE in previous_unlock.type_, f"Residence {current_unlock.name} references"\
                f" previous building {previous_unlock.name}, which is not also a residence"
            new_requirements |= {A1800Requirement(name, previous_unlock.region)
                                 for name in previous_unlock.consumption}

        is_upgrade = UnlockType.UPGRADE in previous_unlock.type_
        current_unlock = previous_unlock
    return new_requirements


def _get_requirements_from_condition(condition: TriggerCondition) -> Optional[set[A1800Requirement]]:
    match(condition.type_):
        case TriggerConditionType.TRUE:
            return set()
        case TriggerConditionType.FALSE:
            assert False, "TriggerConditionType FALSE should never be used for unlocks"
        case TriggerConditionType.ALL:
            return {requirement for subcondition in condition.conditions for requirement in _get_requirements_from_condition(subcondition) or set()}
        case TriggerConditionType.LINEAR:
            return {requirement for subcondition in condition.conditions for requirement in _get_requirements_from_condition(subcondition) or set()}
        case TriggerConditionType.ANY:
            return {requirement for subcondition in condition.conditions for requirement in _get_requirements_from_condition(subcondition) or set()}
        case TriggerConditionType.SESSION_ENTER:
            return SESSIONS.find_session(condition.session).requirements
        case TriggerConditionType.POPULATION:
            return {A1800Requirement(condition.population_name, condition.region)}
        case TriggerConditionType.POPULATION_HAPPINESS:
            populations = list(UNLOCKS.find_unlocks(condition.unlock_name, condition.region))
            assert len(populations) == 1, \
                f"Condition {condition.type_.name} {condition.amount} {condition.product_name} has 0 or multiple "\
                "population residences"
            population = populations[0]
            return {A1800Requirement(condition.population_name, condition.region)} | {A1800Requirement(name, population.region) for name in population.luxury}
        case TriggerConditionType.COUNTER:
            unlock = next(UNLOCKS.find_unlocks(condition.unlock_name, condition.region))
            return get_requirements_for_construction(unlock) | {A1800Requirement(name, region) for name, region in condition.requirements}
        case TriggerConditionType.COUNTER_GOOD_IN_REGION:
            a1800_region = REGIONS.find_region(condition.region)
            assert a1800_region, \
                f"Condition {condition.type_.name} {condition.amount} {condition.product_name} in {condition.region.name} "\
                f"has 0 or multiple regions"
            return {A1800Requirement(condition.product_name, condition.product_region)} | a1800_region.requirements
        case TriggerConditionType.COUNTER_EXPEDITION_SOLVED:
            return {A1800Requirement(name, region) for name, region in condition.requirements}
        case TriggerConditionType.UNLOCK:
            return {A1800Requirement(condition.unlock_name, condition.region, type=RequirementType.UNLOCK)}
        case TriggerConditionType.QUEST_COMPLETE:
            return {A1800Requirement(name, region) for name, region in condition.requirements}
        case TriggerConditionType.EVENT_ACTIVE:
            return {A1800Requirement(condition.product_name, condition.region)}
        case TriggerConditionType.OBJECT_POSITION:
            unlock = next(UNLOCKS.find_unlocks(condition.unlock_name, condition.region))
            target = next(UNLOCKS.find_unlocks(condition.target_name, condition.region))
            return get_requirements_for_construction(unlock) | get_requirements_for_construction(target)
        case TriggerConditionType.ITEM_SET_ACTIVE:
            unlock = next(UNLOCKS.find_unlocks(condition.unlock_name, condition.unlock_region))
            return {A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost} | {A1800Requirement(name, region) for name, region in condition.requirements}
        case TriggerConditionType.FACTORY_PRODUCTIVITY:
            unlock = next(UNLOCKS.find_unlocks(condition.unlock_name, condition.region))
            return {A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost | unlock.maintenance | {name for name, _ in unlock.input}}
        case TriggerConditionType.ACTIVE_DLC:
            assert False, "TriggerConditionType ACTIVE_DLC should never be used for unlocks"


class _Logic:
    _initialized: bool = False
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: dict[str, set[A1800Requirement]] = {}
    _victory_condition: TriggerCondition = TriggerCondition.TRUE()

    def init(self, parsed_options: ParsedOptions) -> None:
        self._parsed_options = parsed_options

        self._required_population = {
            (population.name, population.region): (population, amount) for name, amount in parsed_options.required_population.items()
            for population in PRODUCTS.find_populations(name)
        }

        self._required_buildings = {
            (unlock.name, unlock.region): (unlock, amount) for name, amount in parsed_options.required_skyscrapers.items()
            for unlock in UNLOCKS.find_unlocks(name)
        } | {
            (unlock.name, unlock.region): (unlock, 1) for name, region in parsed_options.required_monuments
            for unlock in UNLOCKS.find_unlocks(name, region or NO_REGION)
        }

        self._initialized = True

    def _get_victory_condition(self) -> tuple[set[A1800Requirement], TriggerCondition, DLC]:
        victory_required_items: set[A1800Requirement] = set()
        victory_conditions: list[TriggerCondition] = []
        victory_dlcs: DLC = DLC.VANILLA
        for required_population in self._required_population.values():
            population, amount = required_population
            supplied = False
            luxury = False
            lifestyle = False

            victory_required_items.add(A1800Requirement(population.name, population.region))
            victory_conditions.append(TriggerCondition.POPULATION(
                population.name, population.region, amount, guid=population.guid))
            assert len(population.dlc) == 1, \
                f"Victory condition requested population {population.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(population.dlc))

            if supplied or luxury or lifestyle:
                residence = UNLOCKS.get_primary_residence(population.name, population.region)

                if supplied:
                    victory_required_items |= set(A1800Requirement(consumption, population.region)
                                                  for consumption in residence.consumption)
                if luxury:
                    victory_required_items |= set(A1800Requirement(luxury, population.region)
                                                  for luxury in residence.luxury)
                if lifestyle:
                    victory_required_items |= set(A1800Requirement(lifestyle, population.region)
                                                  for lifestyle in residence.lifestyle)

        for required_building in self._required_buildings.values():
            unlock, amount = required_building
            supplied = False
            luxury = False
            lifestyle = False

            victory_required_items |= get_requirements_for_construction(unlock)
            victory_conditions.append(TriggerCondition.COUNTER(
                unlock.name, unlock.region, amount, guid=unlock.guids[0]))
            assert len(unlock.dlc) == 1, \
                f"Victory condition requested building {unlock.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(unlock.dlc))

            if UnlockType.RESIDENCE in unlock.type_ and (supplied or luxury or lifestyle):
                if supplied:
                    victory_required_items |= set(A1800Requirement(consumption, unlock.region)
                                                  for consumption in unlock.consumption)
                if luxury:
                    victory_required_items |= set(A1800Requirement(luxury, unlock.region)
                                                  for luxury in unlock.luxury)
                if lifestyle:
                    victory_required_items |= set(A1800Requirement(lifestyle, unlock.region)
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
        assert self._initialized, "The Anno 1800 logic module was used before it was initialized."
        while to_check:
            requirement = to_check.pop()
            checked.add(requirement)

            new_requirements: set[A1800Requirement] = set()
            if requirement.type == RequirementType.PRODUCT:
                event_item = next(EVENT_ITEMS.find_event_items(requirement.name, requirement.region), None)
                if event_item:
                    for event_location_name in event_item.locations:
                        for event_location in EVENT_LOCATIONS.find_event_locations(event_location_name, event_item.name, event_item.region):
                            new_requirements.add(A1800Requirement(event_location.name,
                                                                  event_location.region, RequirementType.UNLOCK))
                else:
                    raise ValueError(f"Requirement name {requirement.name} doesn't match any product.")

            elif requirement.type == RequirementType.UNLOCK:
                unlock = next(UNLOCKS.find_unlocks(requirement.name, requirement.region), None)
                if unlock:
                    new_requirements |= get_requirements_for_construction(unlock)

                    if UnlockType.BUILDING in unlock.type_:
                        new_requirements |= {A1800Requirement(name, unlock.region) for name in unlock.maintenance}

                    if UnlockType.FACTORY in unlock.type_:
                        new_requirements |= {A1800Requirement(name, region) for name, region in unlock.input}

                    for event_location in EVENT_LOCATIONS.find_event_locations(requirement.name, region=requirement.region):
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
                            anno_region = REGIONS.find_region(region)
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

    def _is_progressive(self, obj: A1800Unlock | A1800EventItem | A1800EventLocation) -> bool:
        requirement_type = RequirementType.PRODUCT if isinstance(obj, A1800EventItem) else RequirementType.UNLOCK

        if isinstance(obj, A1800EventLocation):
            return bool(next((
                requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
                and requirement.name == obj.name and requirement.region in obj.region), None)) and \
                self._is_progressive(next(EVENT_ITEMS.find_event_items(obj.output, obj.region)))
        else:
            return bool(next((
                requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
                and requirement.name == obj.name and requirement.region in obj.region), None))

    def generate_logic(self) -> None:
        assert self._initialized, "The Anno 1800 logic module was used before it was initialized."
        victory_required_items, self._victory_condition, self._victory_dlcs = self._get_victory_condition()

        if self._parsed_options.full_accessibility:
            initial_required_items = victory_required_items.copy() | {requirement for unlock in UNLOCKS.get_unlock_locations(
            ) for requirement in _get_requirements_from_condition(unlock.condition) or set()}
        else:
            initial_required_items = victory_required_items.copy()

        victory_event_location = A1800EventLocation(
            self._victory_condition.ap_location_name, {DLC.VANILLA}, Region.OW, NO_REGION, "Victory", is_progressive=True)
        EVENT_LOCATIONS._a1800_event_locations.append(victory_event_location)  # pyright: ignore[reportPrivateUsage]
        self._victory_condition.ap_location_name = "Victory Condition"

        for event_item in EVENT_ITEMS.get_event_items():
            if event_item.name == "Victory":
                event_item.locations = {victory_event_location.name}

        initial_checked_items: set[A1800Requirement] = {A1800Requirement("Victory", ALL_REGIONS)}

        initial_location_requirements = {victory_event_location.ap_location_name: victory_required_items.copy()}

        self._a1800_required_items, self._a1800_location_requirements = self._generate_requirements_and_rules(
            initial_required_items, initial_checked_items, START_REGION, initial_location_requirements)

        for obj in list(UNLOCKS.get_unlocks()) + list(EVENT_ITEMS.get_event_items()) + list(EVENT_LOCATIONS.get_event_locations()):
            if self._is_progressive(obj):
                obj.is_progressive = True

    def get_location_requirements(self) -> dict[str, set[A1800Requirement]]:
        return self._a1800_location_requirements

    def get_victory_dlcs(self) -> DLC:
        return self._victory_dlcs

    def get_victory_condition(self) -> TriggerCondition:
        return self._victory_condition


LOGIC = _Logic()
