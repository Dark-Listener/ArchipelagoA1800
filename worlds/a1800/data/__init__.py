from collections.abc import Sequence
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options


from ._Dlc import DLC
from ._EventItem import A1800EventItem, find_event_items, get_event_items
from ._EventLocation import _a1800_event_locations  # pyright: ignore[reportPrivateUsage]
from ._EventLocation import A1800EventLocation, find_event_locations, get_event_locations
from ._Product import A1800Product, find_populations
from ._Region import ALL_REGIONS, A1800Region, get_start_region, NO_REGION, Region, get_regions
from ._Requirement import A1800Requirement, RequirementType
from ._Unlock import A1800Unlock, find_ap_item, find_starting_items, find_unlocks, get_starting_items, get_unlock_locations, get_unlocks, UnlockType


def _get_victory_condition_name_and_requirements(
    population_requirements: list[tuple[str, Region, int, bool, bool, bool]]
) -> tuple[str, set[A1800Requirement]]:
    victory_event_location_name = ""
    victory_required_items: set[A1800Requirement] = set()
    for population_requirement in population_requirements:
        population, region, amount, supplied, luxury, lifestyle = population_requirement

        victory_event_location_name += f"{' ' if victory_event_location_name else ''}"\
            f"{population} (Amount: {amount if amount else 1}, Supplied: {'Yes' if supplied else 'No'}, "\
            f"Luxury: {'Yes' if luxury else 'No'}, Lifestyle: {'Yes' if lifestyle else 'No'})"

        victory_required_items.add(A1800Requirement(population, region))

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

    return victory_event_location_name, victory_required_items


class _AnnoData:
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_location_requirements: list[tuple[str, frozenset[A1800Requirement]]] = []

    _item_name_to_ap_code: dict[str, int] = {
        unlock.ap_item_name: unlock.ap_code for unlock in get_unlocks() if unlock.ap_code}

    _location_name_to_ap_code: dict[str, int] = {
        unlock.ap_location_name: unlock.ap_code for unlock in get_unlock_locations() if unlock.ap_code}

    def _generate_requirements_and_rules(
        self,
        to_check: set[A1800Requirement],
        checked: set[A1800Requirement],
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
                            assert UnlockType.RESIDENCE in previous_unlock.type
                            new_requirements |= {A1800Requirement(name, previous_unlock.region)
                                                 for name in previous_unlock.consumption}

                    for event_location in find_event_locations(unlock.name, region=unlock.region):
                        location_requirements.append((event_location.ap_location_name, frozenset(new_requirements)))
                else:
                    raise ValueError(f"Requirement name {requirement.name} doesn't match any unlock.")

            else:
                raise ValueError(f"Requirement type {requirement.type} isn't PRODUCT or UNLOCK.")

            for new_requirement in new_requirements:
                if not new_requirement in checked and not new_requirement in to_check:
                    to_check.add(new_requirement)

        return checked, location_requirements

    def _is_progressive(self, obj: A1800Unlock | A1800EventItem | A1800EventLocation) -> bool:
        requirement_type = RequirementType.PRODUCT if isinstance(obj, A1800EventItem) else RequirementType.UNLOCK

        return bool(next((
            requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
            and requirement.name == obj.name and requirement.region in obj.region), None))

    def process_options(self, options: "A1800Options") -> None:
        global _a1800_event_locations

        # options -> get victory condition stuff
        population_requirements = [
            ("Artisans", Region.OW, 1, False, False, False),
        ]

        victory_event_location_name, initial_required_items = _get_victory_condition_name_and_requirements(
            population_requirements)

        victory_event_location = A1800EventLocation(
            victory_event_location_name, DLC.VANILLA, Region.OW, "Victory", is_progressive=True)
        _a1800_event_locations.append(victory_event_location)

        for event_item in get_event_items():
            if event_item.name == "Victory":
                event_item.locations = {victory_event_location.name}

        initial_checked_items: set[A1800Requirement] = {A1800Requirement("Victory", ALL_REGIONS)}

        initial_location_requirements = [(victory_event_location.ap_location_name, frozenset(initial_required_items))]

        self._a1800_required_items, self._a1800_location_requirements = self._generate_requirements_and_rules(
            initial_required_items, initial_checked_items, initial_location_requirements)

        for obj in list(get_unlocks()) + list(get_event_items()) + list(get_event_locations()):
            if self._is_progressive(obj):
                obj.is_progressive = True

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return find_ap_item(ap_name)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return find_event_items(name, region)

    def find_event_locations(self, name: str, output: str, region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return find_event_locations(name, output, region)

    def find_starting_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
        return find_starting_items(name, region)

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return find_populations(name, region)

    def get_event_items(self) -> Sequence[A1800EventItem]:
        return get_event_items()

    def get_event_locations(self) -> Sequence[A1800EventLocation]:
        return get_event_locations()

    def get_item_name_to_ap_code(self) -> dict[str, int]:
        return self._item_name_to_ap_code

    def get_location_name_to_ap_code(self) -> dict[str, int]:
        return self._location_name_to_ap_code

    def get_regions(self) -> Sequence[A1800Region]:
        return get_regions()

    def get_location_requirements(self) -> Sequence[tuple[str, frozenset[A1800Requirement]]]:
        return self._a1800_location_requirements

    def get_start_region(self) -> A1800Region:
        return get_start_region()

    def get_starting_items(self) -> Sequence[A1800Unlock]:
        return get_starting_items()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        return get_unlocks()

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        return get_unlock_locations()


ANNO_DATA = _AnnoData()

__all__ = [
    "A1800EventItem",
    "A1800Region",
    "A1800Requirement",
    "A1800Unlock",
    "ALL_REGIONS",
    "ANNO_DATA",
    "Region",
]
