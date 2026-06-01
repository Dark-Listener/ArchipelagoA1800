from typing import Optional

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, START_REGION, TriggerType, UnlockType
from ._EventItems import A1800EventItem, EVENT_ITEMS
from ._EventLocations import A1800EventLocation, EVENT_LOCATIONS
from ._ParsedOptions import ParsedOptions
from ._Products import PRODUCTS
from ._Regions import REGIONS
from ._Requirement import A1800Requirement
from ._Sessions import SESSIONS
from ._Trigger import Trigger
from ._Unlocks import A1800Unlock, UNLOCKS


def get_requirements_for_construction(unlock: A1800Unlock) -> set[A1800Requirement]:
    new_requirements: set[A1800Requirement] = set()

    if not UnlockType.META in unlock.type:
        new_requirements.add(A1800Requirement(unlock.name, unlock.region, RequirementType.UNLOCK))

    if UnlockType.BUILDING in unlock.type:
        new_requirements |= {A1800Requirement(name, unlock.region) for name in unlock.cost}

    if UnlockType.FACTORY in unlock.type:
        new_requirements |= {A1800Requirement(name, region) for name, region in unlock.input}

    is_upgrade = UnlockType.UPGRADE in unlock.type
    current_unlock = unlock
    while is_upgrade:
        previous_unlock = next(UNLOCKS.find_unlocks(
            current_unlock.previous_building, current_unlock.region))
        new_requirements.add(A1800Requirement(previous_unlock.name,
                                              previous_unlock.region, RequirementType.UNLOCK))

        if UnlockType.RESIDENCE in unlock.type:
            assert UnlockType.RESIDENCE in previous_unlock.type, f"Residence {current_unlock.name} references"\
                f" previous building {previous_unlock.name}, which is not also a residence"
            new_requirements |= {A1800Requirement(name, previous_unlock.region)
                                 for name in previous_unlock.consumption}

        is_upgrade = UnlockType.UPGRADE in previous_unlock.type
        current_unlock = previous_unlock
    return new_requirements


def _get_requirements_from_trigger(trigger: Trigger) -> Optional[set[A1800Requirement]]:
    match(trigger.trigger_type):
        case TriggerType.TRUE:
            return set()
        case TriggerType.FALSE:
            assert False, "TriggerType FALSE should never be used for unlocks"
        case TriggerType.ALL:
            return {requirement for trigger in trigger.triggers for requirement in _get_requirements_from_trigger(trigger) or set()}
        case TriggerType.LINEAR:
            return {requirement for trigger in trigger.triggers for requirement in _get_requirements_from_trigger(trigger) or set()}
        case TriggerType.ANY:
            return {requirement for trigger in trigger.triggers for requirement in _get_requirements_from_trigger(trigger) or set()}
        case TriggerType.SESSION_ENTER:
            return SESSIONS.find_session(trigger.session).requirements
        case TriggerType.POPULATION:
            return {A1800Requirement(trigger.population_name, trigger.region)}
        case TriggerType.POPULATION_HAPPINESS:
            populations = list(UNLOCKS.find_unlocks(trigger.unlock_name, trigger.region))
            assert len(populations) == 1, \
                f"Trigger {trigger.trigger_type.name} {trigger.amount} {trigger.product_name} has 0 or multiple "\
                "population residences"
            population = populations[0]
            return {A1800Requirement(trigger.population_name, trigger.region)} | {A1800Requirement(name, population.region) for name in population.luxury}
        case TriggerType.COUNTER:
            unlock = next(UNLOCKS.find_unlocks(trigger.unlock_name, trigger.region))
            return get_requirements_for_construction(unlock)
        case TriggerType.COUNTER_GOOD_IN_REGION:
            a1800_region = REGIONS.find_region(trigger.region)
            assert a1800_region, \
                f"Trigger {trigger.trigger_type.name} {trigger.amount} {trigger.product_name} in {trigger.region.name} "\
                f"has 0 or multiple regions"
            return {A1800Requirement(trigger.product_name, trigger.product_region)} | a1800_region.requirements
        case TriggerType.COUNTER_EXPEDITION_SOLVED:
            return {A1800Requirement(name, region) for name, region in trigger.requirements}
        case TriggerType.UNLOCK:
            return {A1800Requirement(trigger.unlock_name, trigger.region, type=RequirementType.UNLOCK)}
        case TriggerType.QUEST_COMPLETE:
            return {A1800Requirement(name, region) for name, region in trigger.requirements}
        case TriggerType.EVENT_ACTIVE:
            return {A1800Requirement(trigger.product_name, trigger.region)}
        case TriggerType.OBJECT_POSITION:
            unlock = next(UNLOCKS.find_unlocks(trigger.unlock_name, trigger.region))
            target = next(UNLOCKS.find_unlocks(trigger.target_name, trigger.region))
            return get_requirements_for_construction(unlock) | get_requirements_for_construction(target)
        case TriggerType.ITEM_SET_ACTIVE:
            unlock = next(UNLOCKS.find_unlocks(trigger.unlock_name, trigger.unlock_region))
            return {A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost} | {A1800Requirement(name, region) for name, region in trigger.requirements}
        case TriggerType.FACTORY_PRODUCTIVITY:
            unlock = next(UNLOCKS.find_unlocks(trigger.unlock_name, trigger.region))
            return {A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost | unlock.maintenance | {name for name, _ in unlock.input}}
        case TriggerType.ACTIVE_DLC:
            assert False, "TriggerType ACTIVE_DLC should never be used for unlocks"


class _Logic:
    _initialized: bool = False
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: dict[str, set[A1800Requirement]] = {}
    _victory_trigger: Trigger = Trigger.TRUE()

    def init(self, parsed_options: ParsedOptions) -> None:
        self._parsed_options = parsed_options

        self._required_population = {
            name: (population, amount) for name, amount in parsed_options.required_population.items()
            for population in PRODUCTS.find_populations(name)
        }

        self._required_buildings = {
            name: (unlock, amount) for name, amount in parsed_options.required_skyscrapers.items()
            for unlock in UNLOCKS.find_unlocks(name)
        } | {
            name: (unlock, 1) for name, region in parsed_options.required_monuments
            for unlock in UNLOCKS.find_unlocks(name, region)
        }

        self._initialized = True

    def _get_victory_condition(self) -> tuple[set[A1800Requirement], Trigger, DLC]:
        victory_required_items: set[A1800Requirement] = set()
        victory_triggers: list[Trigger] = []
        victory_dlcs: DLC = DLC.VANILLA
        for required_population in self._required_population.values():
            population, amount = required_population
            supplied = False
            luxury = False
            lifestyle = False

            victory_required_items.add(A1800Requirement(population.name, population.region))
            victory_triggers.append(Trigger.POPULATION(
                population.name, population.region, amount, guid=population.guid))
            assert len(population.dlc) == 1, \
                f"Victory condition requested population {population.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(population.dlc))

            if supplied or luxury or lifestyle:
                # Pick residence, but avoid skyscrapers and the Skyline Tower
                residence = next(
                    unlock for unlock in UNLOCKS.get_unlocks()
                    if UnlockType.RESIDENCE in unlock.type and not "Level" in unlock.name and not "Tower" in unlock.name
                    and population.region in unlock.region and population.name in next(zip(*unlock.output)))

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
            victory_triggers.append(Trigger.COUNTER(
                unlock.name, unlock.region, amount, guid=unlock.guids[0]))
            assert len(unlock.dlc) == 1, \
                f"Victory condition requested building {unlock.name} which was introduced in more than one DLC"
            victory_dlcs |= next(iter(unlock.dlc))

            if UnlockType.RESIDENCE in unlock.type and (supplied or luxury or lifestyle):
                if supplied:
                    victory_required_items |= set(A1800Requirement(consumption, unlock.region)
                                                  for consumption in unlock.consumption)
                if luxury:
                    victory_required_items |= set(A1800Requirement(luxury, unlock.region)
                                                  for luxury in unlock.luxury)
                if lifestyle:
                    victory_required_items |= set(A1800Requirement(lifestyle, unlock.region)
                                                  for lifestyle in unlock.lifestyle)

        assert len(victory_triggers), "No victory subtriggers could be created, goal would be immediately reached!"
        if len(victory_triggers) == 1:
            victory_trigger = victory_triggers[0]
        else:
            victory_trigger = Trigger.ALL(*victory_triggers)

        if victory_dlcs != DLC.VANILLA and DLC.VANILLA in victory_dlcs:
            victory_dlcs ^= DLC.VANILLA

        return victory_required_items, victory_trigger, victory_dlcs

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

                    if UnlockType.BUILDING in unlock.type:
                        new_requirements |= {A1800Requirement(name, unlock.region) for name in unlock.maintenance}

                    if UnlockType.FACTORY in unlock.type:
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
                    if (unlock.ap_region or unlock.region) ^ checked_regions != NO_REGION:
                        for region in [region for region in Region.__members__.values()
                                       if region in unlock.region & (unlock.region ^ checked_regions)]:
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
        victory_required_items, self._victory_trigger, self._victory_dlcs = self._get_victory_condition()

        if self._parsed_options.full_accessibility:
            initial_required_items = victory_required_items.copy() | {requirement for unlock in UNLOCKS.get_unlock_locations(
            ) for requirement in _get_requirements_from_trigger(unlock.trigger) or set()}
        else:
            initial_required_items = victory_required_items.copy()

        victory_event_location = A1800EventLocation(
            self._victory_trigger.ap_location_name, {DLC.VANILLA}, Region.OW, NO_REGION, "Victory", is_progressive=True)
        EVENT_LOCATIONS._a1800_event_locations.append(victory_event_location)  # pyright: ignore[reportPrivateUsage]
        self._victory_trigger.ap_location_name = "Victory Condition"

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

    def get_victory_trigger(self) -> Trigger:
        return self._victory_trigger


LOGIC = _Logic()
