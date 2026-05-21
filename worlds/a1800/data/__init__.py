from collections.abc import Sequence
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options

from ._Enums import ALL_REGIONS, NO_REGION, Region, Session, START_REGION, TriggerType
from ._EventItem import A1800EventItem, find_event_items, get_event_items
from ._EventLocation import A1800EventLocation, find_event_locations, get_event_locations
from ._Logic import LOGIC
from ._Product import A1800Product, find_populations, get_populations
from ._Region import A1800Region, get_regions
from ._Requirement import A1800Requirement
from ._Session import A1800Session, find_session
from ._Trigger import Trigger
from ._Unlock import A1800Unlock, find_ap_item, get_unlock_locations, get_unlocks


class _AnnoData:
    _item_name_to_ap_code: dict[str, int] = {
        unlock.ap_item_name: unlock.ap_code for unlock in get_unlocks() if unlock.ap_code}

    _location_name_to_ap_code: dict[str, int] = {
        unlock.ap_location_name: unlock.ap_code for unlock in get_unlock_locations() if unlock.ap_code}

    def process_options(self, options: "A1800Options") -> None:
        population_requirements: list[tuple[str, Region, int, bool, bool, bool]] = []
        for identifier, amount_str in options.required_population_amount.value.items():
            id_split = identifier.split("-")
            if len(id_split) != 4:
                continue

            region = getattr(Region, id_split[1].upper(), None)
            name = id_split[3].capitalize()
            if not region or not name:
                continue

            population = next(find_populations(name, region), None)
            if not population:
                continue

            try:
                amount = int(amount_str)
            except ValueError:
                amount = 0

            if not amount:
                continue

            population_requirements.append((population.name, population.region, amount, False, False, False))

        LOGIC.generate_logic(population_requirements)

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return find_ap_item(ap_name)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return find_event_items(name, region)

    def find_event_locations(self, name: str, output: str, region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return find_event_locations(name, output, region)

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return find_populations(name, region)

    def find_session(self, session: Session) -> A1800Session:
        return find_session(session)

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
        return LOGIC.get_location_requirements()

    def get_populations(self) -> Sequence[A1800Product]:
        return get_populations()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        return get_unlocks()

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        return get_unlock_locations()

    def get_victory_trigger(self) -> Trigger:
        return LOGIC.get_victory_trigger()


ANNO_DATA = _AnnoData()

__all__ = [
    "A1800EventItem",
    "A1800Region",
    "A1800Requirement",
    "A1800Unlock",
    "ALL_REGIONS",
    "ANNO_DATA",
    "Region",
    "START_REGION",
    "Trigger",
    "TriggerType",
]
