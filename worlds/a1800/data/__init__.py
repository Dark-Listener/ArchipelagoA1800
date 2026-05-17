from collections.abc import Sequence
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options


from ._Dlc import DLC
from ._EventItem import _a1800_event_items  # pyright: ignore[reportPrivateUsage]
from ._EventItem import A1800EventItem, find_event_items, get_event_items
from ._EventLocation import _a1800_event_locations  # pyright: ignore[reportPrivateUsage]
from ._EventLocation import A1800EventLocation, find_event_locations, get_event_locations
from ._Region import ALL_REGIONS, A1800Region, get_start_region, NO_REGION, Region, get_regions
from ._Requirement import A1800Requirement, RequirementType
from ._Unlock import A1800Unlock, find_ap_item, find_starting_items, find_unlocks, get_starting_items, get_unlock_locations, get_unlocks, UnlockType


class AnnoData:
    _a1800_required_items: set[A1800Requirement] = set()
    _a1800_rules: list[tuple[str, list[str]]] = []

    _item_name_to_ap_code: dict[str, int] = {
        unlock.ap_item_name: unlock.ap_code for unlock in get_unlocks() if unlock.ap_code}

    _location_name_to_ap_code: dict[str, int] = {
        unlock.ap_location_name: unlock.ap_code for unlock in get_unlock_locations() if unlock.ap_code}

    def _is_progressive(self, obj: A1800Unlock | A1800EventItem | A1800EventLocation) -> bool:
        requirement_type = RequirementType.PRODUCT if isinstance(obj, A1800EventItem) else RequirementType.UNLOCK

        return bool(next((
            requirement for requirement in self._a1800_required_items if requirement.type == requirement_type
            and requirement.name == obj.name and requirement.region in obj.region), None))

    def _generate_requirements_and_rules(
        self,
        to_check: set[A1800Requirement],
        checked: set[A1800Requirement],
        rules: list[tuple[str, list[str]]]
    ) -> tuple[set[A1800Requirement], list[tuple[str, list[str]]]]:
        if not to_check:
            return checked, rules

        requirement = to_check.pop()
        checked.add(requirement)

        new_requirements: set[A1800Requirement] = set()
        event_item = next(find_event_items(requirement.name, requirement.region), None)
        unlock = next(find_unlocks(requirement.name, requirement.region), None)
        if requirement.type == RequirementType.PRODUCT and event_item:
            for event_location_name in event_item.locations:
                for event_location in find_event_locations(event_location_name, event_item.name, event_item.region):
                    new_requirements.add(A1800Requirement(event_location.name,
                                         event_location.region, RequirementType.UNLOCK))

        elif requirement.type == RequirementType.UNLOCK and unlock:
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
                rules.append((event_location.ap_location_name, [ap_item_name for requirement in new_requirements
                                                                for ap_item_name in requirement.ap_item_names]))

        else:
            raise ValueError(f"Requirement name {requirement.name} doesn't match any product or unlock.")

        for new_requirement in new_requirements:
            if not new_requirement in checked and not new_requirement in to_check:
                to_check.add(new_requirement)

        return self._generate_requirements_and_rules(to_check, checked, rules)

    def process_options(self, options: "A1800Options") -> None:
        global _a1800_event_locations

        population_requirements = [
            ("Artisans", Region.OW, 1, False, False, False)
        ]

        victory_event_location_name = ""
        victory_required_items: set[A1800Requirement] = set()
        for population_requirement in population_requirements:
            population, region, amount, supplied, luxury, lifestyle = population_requirement

            victory_event_location_name += f"{population}(Amount: {amount if amount else 1}, "\
                f"Supplied: {'Yes' if supplied else 'No'}, Luxury: {'Yes' if luxury else 'No'}, "\
                f"Lifestyle: {'Yes' if lifestyle else 'No'})"

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

        victory_event_location = A1800EventLocation(victory_event_location_name, DLC.VANILLA, Region.OW, "Victory")
        victory_event_location.is_progressive = True

        victory_checked_items: set[A1800Requirement] = {A1800Requirement("Victory", ALL_REGIONS)}

        _a1800_event_locations.append(victory_event_location)
        victory_event_item_idx = next(i for i, event_item in enumerate(
            get_event_items()) if event_item.name == "Victory")
        _a1800_event_items[victory_event_item_idx].locations = {victory_event_location.name}

        victory_rules = [(victory_event_location.ap_location_name, [ap_item_name for requirement in victory_required_items
                                                                    for ap_item_name in requirement.ap_item_names])]

        self._a1800_required_items, self._a1800_rules = self._generate_requirements_and_rules(
            victory_required_items, victory_checked_items, victory_rules)

        for unlock in get_unlocks():
            if self._is_progressive(unlock):
                unlock.is_progressive = True
        for event_item in get_event_items():
            if self._is_progressive(event_item):
                event_item.is_progressive = True
        for event_location in get_event_locations():
            if self._is_progressive(event_location):
                event_location.is_progressive = True

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return find_ap_item(ap_name)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return find_event_items(name, region)

    def find_event_locations(self, name: str, output: str, region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return find_event_locations(name, output, region)

    def find_starting_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
        return find_starting_items(name, region)

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

    def get_rules(self) -> Sequence[tuple[str, list[str]]]:
        return self._a1800_rules

    def get_start_region(self) -> A1800Region:
        return get_start_region()

    def get_starting_items(self) -> Sequence[A1800Unlock]:
        return get_starting_items()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        return get_unlocks()

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        return get_unlock_locations()


ANNO_DATA = AnnoData()

__all__ = [
    "A1800EventItem",
    "A1800Region",
    "A1800Requirement",
    "A1800Unlock",
    "ALL_REGIONS",
    "ANNO_DATA",
    "Region",
]
