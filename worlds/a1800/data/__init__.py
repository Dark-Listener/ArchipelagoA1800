from collections.abc import Sequence
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options

from ._Enums import ALL_REGIONS, NO_REGION, Region, Session, START_REGION, TriggerType
from ._EventItem import A1800EventItem, find_event_items, get_event_items
from ._EventLocation import A1800EventLocation, find_event_locations, get_event_locations
from ._Logic import LOGIC
from ._Product import A1800Product, find_populations
from ._Region import A1800Region, find_region, get_regions
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
        # options -> get victory condition stuff
        population_requirements = [
            ("Artisans", Region.OW, 1, False, False, False),
        ]

        LOGIC.generate_logic(population_requirements)

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return find_ap_item(ap_name)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return find_event_items(name, region)

    def find_event_locations(self, name: str, output: str, region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return find_event_locations(name, output, region)

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return find_populations(name, region)

    def find_region(self, region: Region) -> A1800Region:
        return find_region(region)

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
