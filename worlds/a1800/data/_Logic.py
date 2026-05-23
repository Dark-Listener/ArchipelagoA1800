from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, START_REGION, UnlockType
from ._EventItems import A1800EventItem, EVENT_ITEMS
from ._EventLocations import A1800EventLocation, EVENT_LOCATIONS
from ._Products import A1800Product
from ._Regions import REGIONS
from ._Requirement import A1800Requirement
from ._Trigger import ALL, POPULATION, Trigger, TRUE
from ._Unlocks import A1800Unlock, UNLOCKS


def _get_victory_condition_info(
    population_requirements: list[tuple[A1800Product, int, bool, bool, bool]]
) -> tuple[str, set[A1800Requirement], Trigger, DLC]:
    victory_event_location_name = ""
    victory_required_items: set[A1800Requirement] = set()
    victory_triggers: list[Trigger] = []
    victory_dlcs: DLC = DLC.VANILLA
    for population_requirement in population_requirements:
        population, amount, supplied, luxury, lifestyle = population_requirement

        victory_event_location_name += f"{', ' if victory_event_location_name else ''}"\
            f"{amount} {population.name if amount > 1 else population.name[:-1]}"  # ("\
        # f"Supplied: {'Yes' if supplied else 'No'}, "\
        # f"Luxury: {'Yes' if luxury else 'No'}, "\
        # f"Lifestyle: {'Yes' if lifestyle else 'No'})"

        victory_required_items.add(A1800Requirement(population.name, population.region))
        victory_triggers.append(POPULATION(population.region, population.name, amount))
        victory_dlcs |= population.dlc

        residence = next(
            unlock for unlock in UNLOCKS.get_unlocks()
            if UnlockType.RESIDENCE in unlock.type and population.region in unlock.region and population.name in unlock.output)

        if supplied:
            victory_required_items |= set(A1800Requirement(consumption, population.region)
                                          for consumption in residence.consumption)
        if luxury:
            victory_required_items |= set(A1800Requirement(luxury, population.region)
                                          for luxury in residence.luxury)
        if lifestyle:
            victory_required_items |= set(A1800Requirement(lifestyle, population.region)
                                          for lifestyle in residence.lifestyle)

    if len(victory_triggers) == 1:
        victory_trigger = victory_triggers[0]
    else:
        victory_trigger = ALL(*victory_triggers)

    return victory_event_location_name, victory_required_items, victory_trigger, victory_dlcs


class _Logic:
    _initialized: bool = False
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: list[tuple[str, frozenset[A1800Requirement]]] = []
    _victory_trigger: Trigger = TRUE

    def init(self, population_requirements: list[tuple[A1800Product, int, bool, bool, bool]]) -> None:
        self._population_requirements = population_requirements

        self._initialized = True

    def _generate_requirements_and_rules(
        self,
        to_check: set[A1800Requirement],
        checked: set[A1800Requirement],
        checked_regions: Region,
        location_requirements: list[tuple[str, frozenset[A1800Requirement]]]
    ) -> tuple[set[A1800Requirement], list[tuple[str, frozenset[A1800Requirement]]]]:
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
                    new_requirements.add(A1800Requirement(unlock.name, unlock.region, RequirementType.UNLOCK))

                    if UnlockType.BUILDING in unlock.type:
                        new_requirements |= {A1800Requirement(name, unlock.region)
                                             for name in unlock.cost | unlock.maintenance}

                    if UnlockType.FACTORY in unlock.type:
                        new_requirements |= {A1800Requirement(name, unlock.region) if isinstance(
                            name, str) else A1800Requirement(name[0], name[1]) for name in unlock.input}

                    if UnlockType.UPGRADE in unlock.type:
                        previous_unlock = next(UNLOCKS.find_unlocks(unlock.previous_building, unlock.region))
                        new_requirements.add(A1800Requirement(previous_unlock.name,
                                                              previous_unlock.region, RequirementType.UNLOCK))

                        if UnlockType.RESIDENCE in unlock.type:
                            assert UnlockType.RESIDENCE in previous_unlock.type, f"Residence {unlock.name} references"\
                                f" previous building {previous_unlock.name}, which is not also a residence"
                            new_requirements |= {A1800Requirement(name, previous_unlock.region)
                                                 for name in previous_unlock.consumption}

                    for event_location in EVENT_LOCATIONS.find_event_locations(unlock.name, region=unlock.region):
                        location_requirements.append((event_location.ap_location_name, frozenset(new_requirements)))

                    # Traverse region requirements, but don't add them to location rule
                    if unlock.region ^ checked_regions != NO_REGION:
                        for region in [region for region in Region.__members__.values()
                                       if region in unlock.region & (unlock.region ^ checked_regions)]:
                            anno_region = REGIONS.find_region(region)
                            if anno_region:
                                new_requirements |= anno_region.requirements
                            checked_regions |= region
                else:
                    raise ValueError(
                        f"Requirement name {requirement.name} region {requirement.region} doesn't match any unlock.")

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

    def generate_logic(self) -> None:
        assert self._initialized, "The Anno 1800 logic module was used before it was initialized."
        victory_event_location_name, initial_required_items, self._victory_trigger, self._victory_dlcs = _get_victory_condition_info(
            self._population_requirements)
        self._victory_trigger.ap_location_name = "Victory Condition"

        victory_event_location = A1800EventLocation(
            victory_event_location_name, DLC.VANILLA, Region.OW, "Victory", is_progressive=True)
        EVENT_LOCATIONS._a1800_event_locations.append(victory_event_location)  # pyright: ignore[reportPrivateUsage]

        for event_item in EVENT_ITEMS.get_event_items():
            if event_item.name == "Victory":
                event_item.locations = {victory_event_location.name}

        initial_checked_items: set[A1800Requirement] = {A1800Requirement("Victory", ALL_REGIONS)}

        initial_location_requirements = [(victory_event_location.ap_location_name, frozenset(initial_required_items))]

        self._a1800_required_items, self._a1800_location_requirements = self._generate_requirements_and_rules(
            initial_required_items, initial_checked_items, START_REGION, initial_location_requirements)

        for obj in list(UNLOCKS.get_unlocks()) + list(EVENT_ITEMS.get_event_items()) + list(EVENT_LOCATIONS.get_event_locations()):
            if self._is_progressive(obj):
                obj.is_progressive = True

    def get_location_requirements(self) -> list[tuple[str, frozenset[A1800Requirement]]]:
        return self._a1800_location_requirements

    def get_victory_dlcs(self) -> DLC:
        return self._victory_dlcs

    def get_victory_trigger(self) -> Trigger:
        return self._victory_trigger


LOGIC = _Logic()
