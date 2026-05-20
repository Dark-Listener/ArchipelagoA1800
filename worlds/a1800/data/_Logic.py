from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, START_REGION, UnlockType
from ._EventItem import A1800EventItem, find_event_items, get_event_items
from ._EventLocation import _a1800_event_locations  # pyright: ignore[reportPrivateUsage]
from ._EventLocation import A1800EventLocation, find_event_locations, get_event_locations
from ._Region import find_region
from ._Requirement import A1800Requirement
from ._Trigger import ALL, POPULATION, Trigger, TRUE
from ._Unlock import A1800Unlock, find_unlocks, get_unlocks


def _get_victory_condition_name_and_requirements(
    population_requirements: list[tuple[str, Region, int, bool, bool, bool]]
) -> tuple[str, set[A1800Requirement], Trigger]:
    victory_event_location_name = ""
    victory_required_items: set[A1800Requirement] = set()
    victory_triggers: list[Trigger] = []
    for population_requirement in population_requirements:
        population, region, amount, supplied, luxury, lifestyle = population_requirement

        victory_event_location_name += f"{', ' if victory_event_location_name else ''}"\
            f"{population} (Amount: {amount if amount else 1}, Supplied: {'Yes' if supplied else 'No'}, "\
            f"Luxury: {'Yes' if luxury else 'No'}, Lifestyle: {'Yes' if lifestyle else 'No'})"

        victory_required_items.add(A1800Requirement(population, region))
        victory_triggers.append(POPULATION(region, population, amount))

        residence = next(
            unlock for unlock in get_unlocks()
            if UnlockType.RESIDENCE in unlock.type and region in unlock.region and population in unlock.output)

        if supplied:
            victory_required_items |= set(A1800Requirement(consumption, region)
                                          for consumption in residence.consumption)
        if luxury:
            victory_required_items |= set(A1800Requirement(luxury, region)
                                          for luxury in residence.luxury)
        if lifestyle:
            victory_required_items |= set(A1800Requirement(lifestyle, region)
                                          for lifestyle in residence.lifestyle)

    if len(victory_triggers) == 1:
        victory_trigger = victory_triggers[0]
    else:
        victory_trigger = ALL(*victory_triggers)

    return victory_event_location_name, victory_required_items, victory_trigger


class _Logic:
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: list[tuple[str, frozenset[A1800Requirement]]] = []
    _victory_trigger: Trigger = TRUE

    def _generate_requirements_and_rules(
        self,
        to_check: set[A1800Requirement],
        checked: set[A1800Requirement],
        checked_regions: Region,
        location_requirements: list[tuple[str, frozenset[A1800Requirement]]]
    ) -> tuple[set[A1800Requirement], list[tuple[str, frozenset[A1800Requirement]]]]:
        while to_check:
            requirement = to_check.pop()
            checked.add(requirement)

            new_requirements: set[A1800Requirement] = set()
            if requirement.type == RequirementType.PRODUCT:
                event_item = next(find_event_items(requirement.name, requirement.region), None)
                if event_item:
                    for event_location_name in event_item.locations:
                        for event_location in find_event_locations(event_location_name, event_item.name, event_item.region):
                            new_requirements.add(A1800Requirement(event_location.name,
                                                                  event_location.region, RequirementType.UNLOCK))
                else:
                    raise ValueError(f"Requirement name {requirement.name} doesn't match any product.")

            elif requirement.type == RequirementType.UNLOCK:
                unlock = next(find_unlocks(requirement.name, requirement.region), None)
                if unlock:
                    new_requirements.add(A1800Requirement(unlock.name, unlock.region, RequirementType.UNLOCK))

                    if UnlockType.BUILDING in unlock.type:
                        new_requirements |= {A1800Requirement(name, unlock.region)
                                             for name in unlock.cost | unlock.maintenance}

                    if UnlockType.FACTORY in unlock.type:
                        new_requirements |= {A1800Requirement(name, unlock.region) for name in unlock.input}

                    if UnlockType.UPGRADE in unlock.type:
                        previous_unlock = next(find_unlocks(unlock.previous_building, unlock.region))
                        new_requirements.add(A1800Requirement(previous_unlock.name,
                                                              previous_unlock.region, RequirementType.UNLOCK))

                        if UnlockType.RESIDENCE in unlock.type:
                            assert UnlockType.RESIDENCE in previous_unlock.type, f"Residence {unlock.name} references"\
                                f" previous building {previous_unlock.name}, which is not also a residence"
                            new_requirements |= {A1800Requirement(name, previous_unlock.region)
                                                 for name in previous_unlock.consumption}

                    for event_location in find_event_locations(unlock.name, region=unlock.region):
                        location_requirements.append((event_location.ap_location_name, frozenset(new_requirements)))

                    # Traverse region requirements, but don't add them to location rule
                    if unlock.region ^ checked_regions != NO_REGION:
                        for region in [region for region in Region.__members__.values()
                                       if region in unlock.region & (unlock.region ^ checked_regions)]:
                            new_requirements |= find_region(region).requirements
                            checked_regions |= region
                else:
                    raise ValueError(f"Requirement name {requirement.name} doesn't match any unlock.")

            else:
                raise ValueError(f"Requirement type {requirement.type} isn't PRODUCT or UNLOCK.")

            for new_requirement in new_requirements:
                if not new_requirement in checked:
                    to_check.add(new_requirement)

        return checked, location_requirements

    def _is_progressive(self, obj: A1800Unlock | A1800EventItem | A1800EventLocation) -> bool:
        requirement_type = RequirementType.PRODUCT if isinstance(obj, A1800EventItem) else RequirementType.UNLOCK

        return bool(next((
            requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
            and requirement.name == obj.name and requirement.region in obj.region), None))

    def generate_logic(self, population_requirements: list[tuple[str, Region, int, bool, bool, bool]]) -> None:
        global _a1800_event_locations

        victory_event_location_name, initial_required_items, self._victory_trigger = _get_victory_condition_name_and_requirements(
            population_requirements)
        self._victory_trigger.ap_location_name = "Victory Condition"

        victory_event_location = A1800EventLocation(
            victory_event_location_name, DLC.VANILLA, Region.OW, "Victory", is_progressive=True)
        _a1800_event_locations.append(victory_event_location)

        for event_item in get_event_items():
            if event_item.name == "Victory":
                event_item.locations = {victory_event_location.name}

        initial_checked_items: set[A1800Requirement] = {A1800Requirement("Victory", ALL_REGIONS)}

        initial_location_requirements = [(victory_event_location.ap_location_name, frozenset(initial_required_items))]

        self._a1800_required_items, self._a1800_location_requirements = self._generate_requirements_and_rules(
            initial_required_items, initial_checked_items, START_REGION, initial_location_requirements)

        for obj in list(get_unlocks()) + list(get_event_items()) + list(get_event_locations()):
            if self._is_progressive(obj):
                obj.is_progressive = True

    def get_location_requirements(self) -> list[tuple[str, frozenset[A1800Requirement]]]:
        return self._a1800_location_requirements

    def get_victory_trigger(self) -> Trigger:
        return self._victory_trigger


LOGIC = _Logic()
