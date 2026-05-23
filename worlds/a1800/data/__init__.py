from collections.abc import Sequence
from functools import reduce
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options

from ._Chains import CHAINS
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, REGION_NAMES, Session, START_REGION, TriggerType
from ._EventItems import A1800EventItem, EVENT_ITEMS
from ._EventLocations import A1800EventLocation, EVENT_LOCATIONS
from ._Logic import LOGIC
from ._Products import A1800Product, PRODUCTS
from ._Regions import A1800Region, REGIONS
from ._Requirement import A1800Requirement
from ._Sessions import A1800Session, SESSIONS
from ._Trigger import Trigger
from ._Unlocks import _a1800_unlocks  # pyright: ignore[reportPrivateUsage]
from ._Unlocks import A1800Unlock, UNLOCKS


class _A1800Data:
    _item_name_to_ap_code: dict[str, int] = {
        unlock.ap_item_name: unlock.ap_code for unlock in _a1800_unlocks if unlock.ap_code}

    _location_name_to_ap_code: dict[str, int] = {
        unlock.ap_location_name: unlock.ap_code for unlock in sorted(
            _a1800_unlocks, key=lambda location: location.trigger.get_sort_key()) if unlock.ap_code}

    def init(self, options: "A1800Options") -> None:
        self._enabled_dlcs = DLC.VANILLA | reduce(DLC.__or__, (
            dlc for dlc in DLC.__members__.values() if dlc.name in options.enabled_dlcs))

        CHAINS.init(self._enabled_dlcs)
        PRODUCTS.init(self._enabled_dlcs)
        UNLOCKS.init(self._enabled_dlcs)  # Chains, products must init before unlocks
        EVENT_LOCATIONS.init()  # Unlocks must init before event locations
        EVENT_ITEMS.init()  # Products, event locations must init before event items
        REGIONS.init(self._enabled_dlcs)  # Event items, products, unlocks must init before regions
        SESSIONS.init(self._enabled_dlcs)  # Event items, products, unlocks, regions must init before sessions

        self._parse_remaining_options(options)

        LOGIC.init(self._population_requirements)  # Logic comes last
        LOGIC.generate_logic()

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return UNLOCKS.find_ap_item(ap_name)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return EVENT_ITEMS.find_event_items(name, region)

    def find_event_locations(self, name: str, output: str, region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return EVENT_LOCATIONS.find_event_locations(name, output, region)

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return PRODUCTS.find_populations(name, region)

    def find_session(self, session: Session) -> A1800Session:
        return SESSIONS.find_session(session)

    def get_event_items(self) -> Sequence[A1800EventItem]:
        return EVENT_ITEMS.get_event_items()

    def get_event_locations(self) -> Sequence[A1800EventLocation]:
        return EVENT_LOCATIONS.get_event_locations()

    def get_item_name_to_ap_code(self) -> dict[str, int]:
        return self._item_name_to_ap_code

    def get_location_name_to_ap_code(self) -> dict[str, int]:
        return self._location_name_to_ap_code

    def get_regions(self) -> Sequence[A1800Region]:
        return REGIONS.get_regions()

    def get_location_requirements(self) -> Sequence[tuple[str, frozenset[A1800Requirement]]]:
        return LOGIC.get_location_requirements()

    def get_populations(self) -> Sequence[A1800Product]:
        return PRODUCTS.get_populations()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        return UNLOCKS.get_unlocks()

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        return UNLOCKS.get_unlock_locations()

    def get_victory_dlcs(self) -> DLC:
        return LOGIC.get_victory_dlcs()

    def get_victory_trigger(self) -> Trigger:
        return LOGIC.get_victory_trigger()

    def _parse_remaining_options(self, options: "A1800Options") -> None:
        self._population_requirements: list[tuple[A1800Product, int, bool, bool, bool]] = []
        for identifier, amount_str in options.required_population_amount.value.items():
            id_split = identifier.split("-")
            if len(id_split) != 4:
                continue

            region = {full_name: region for region, full_name in REGION_NAMES.items()}[
                id_split[1].replace("_", " ").title()]
            name = id_split[3].replace("_", " ").title()
            if not region or not name:
                continue

            population = next(PRODUCTS.find_populations(name, region), None)
            if not population:
                continue

            try:
                amount = int(amount_str)
            except ValueError:
                amount = 0

            if not amount:
                continue

            self._population_requirements.append((population, amount, False, False, False))


A1800_DATA = _A1800Data()

__all__ = [
    "A1800EventItem",
    "A1800Region",
    "A1800Requirement",
    "A1800Unlock",
    "ALL_REGIONS",
    "A1800_DATA",
    "DLC",
    "Region",
    "START_REGION",
    "Trigger",
    "TriggerType",
]
