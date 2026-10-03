from collections.abc import Mapping, Sequence
from typing import Iterator, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..Options import A1800Options

from ._Chains import A1800Chain, Chains
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, RequirementType, Session, START_REGION, TriggerActionType, TriggerConditionType, UnlockType
from ._EventItems import A1800EventItem, EventItems
from ._EventLocations import A1800EventLocation, EventLocations
from ._Guid import get_next_anno_guid, HACIENDA_QUARTER_GUIDS, RECIPE_GUIDS, reset_anno_guids
from ._Logic import Logic
from ._ParsedOptions import ParsedOptions
from ._Products import A1800Product, Products
from ._Regions import A1800Region, Regions
from ._Requirement import A1800Requirement, make_requirement
from ._Sessions import A1800Session, Sessions
from ._Trigger import Trigger
from ._TriggerAction import TriggerAction
from ._TriggerCondition import TriggerCondition
from ._Unlocks import A1800_ITEM_NAME_GROUPS, A1800_LOCATION_NAME_GROUPS, A1800_PROGRESSIVE_GROUPS, A1800_UNLOCKS
from ._Unlocks import A1800Unlock, Unlocks

ITEM_NAME_GROUPS = A1800_ITEM_NAME_GROUPS

LOCATION_NAME_GROUPS = A1800_LOCATION_NAME_GROUPS

ITEM_NAME_TO_AP_CODE: dict[str, int] = {
    unlock.ap_item_name: unlock.ap_code for unlock in A1800_UNLOCKS if unlock.ap_code
} | {
    ap_item_name: ap_code for ap_item_name, (ap_code, _) in A1800_PROGRESSIVE_GROUPS.items()
}

LOCATION_NAME_TO_AP_CODE: dict[str, int] = {
    unlock.ap_location_name: unlock.ap_code for unlock in sorted(
        A1800_UNLOCKS, key=lambda location: location.condition.get_sort_key()) if unlock.ap_code}


class A1800Data:
    def __init__(self, options: "A1800Options") -> None:
        reset_anno_guids()

        self._parsed_options = ParsedOptions(options)

        self._chains = Chains(self)
        self._products = Products(self)
        # Unlocks need chains, products
        self._unlocks = Unlocks(self)
        # Event locations need unlocks
        self._event_locations = EventLocations(self)
        # Event items need products, event locations
        self._event_items = EventItems(self)
        # Regions need products, unlocks, event items
        self._regions = Regions(self)
        # Sessions need products, unlocks, event items, regions
        self._sessions = Sessions(self)

        # Logic needs everything
        self._logic = Logic(self)
        self._logic.generate_logic()

    def append_event_location(self, event_location: A1800EventLocation) -> None:
        self._event_locations.append_event_location(event_location)

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        return self._unlocks.find_ap_item(ap_name)

    def find_chains(self, name: str, unlock_name: str, unlock_region: Region, region: Optional[Region] = None) -> Iterator[A1800Chain]:
        return self._chains.find_chains(name, unlock_name, unlock_region, region)

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return self._event_items.find_event_items(name, region)

    def find_event_locations(self, name: str, output: str = "", region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return self._event_locations.find_event_locations(name, output, region)

    def find_products(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return self._products.find_products(name, region)

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        return self._products.find_populations(name, region)

    def find_region(self, region: Region) -> Optional[A1800Region]:
        return self._regions.find_region(region)

    def find_session(self, session: Session) -> A1800Session:
        return self._sessions.find_session(session)

    def find_unlocks(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
        return self._unlocks.find_unlocks(name, region)

    def get_chains(self) -> Sequence[A1800Chain]:
        return self._chains.get_chains()

    def get_event_items(self) -> Sequence[A1800EventItem]:
        return self._event_items.get_event_items()

    def get_event_locations(self) -> Sequence[A1800EventLocation]:
        return self._event_locations.get_event_locations()

    def get_hacienda_quarter_unlocks(self) -> dict[str, tuple[int, int, str, int]]:
        return HACIENDA_QUARTER_GUIDS

    def get_location_requirements(self) -> Mapping[str, set[A1800Requirement]]:
        return self._logic.get_location_requirements()

    def get_next_anno_guid(self) -> int:
        return get_next_anno_guid()

    def get_parsed_options(self) -> ParsedOptions:
        return self._parsed_options

    def get_products(self) -> Sequence[A1800Product]:
        return self._products.get_products()

    def get_populations(self) -> Sequence[A1800Product]:
        return self._products.get_populations()

    def get_progressive_groups(self) -> dict[str, tuple[int, list[A1800Unlock]]]:
        return self._unlocks.get_progressive_groups()

    def get_recipe_unlocks(self) -> dict[str, tuple[int, int, int, int, bool]]:
        return RECIPE_GUIDS

    def get_regions(self) -> Sequence[A1800Region]:
        return self._regions.get_regions()

    def get_requirements_for_construction(self, unlock: A1800Unlock):
        return self._logic.get_requirements_for_construction(unlock)

    def get_sessions(self) -> Sequence[A1800Session]:
        return self._sessions.get_sessions()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        return self._unlocks.get_unlocks()

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        return self._unlocks.get_unlock_locations()

    def get_victory_dlcs(self) -> DLC:
        return self._logic.get_victory_dlcs()

    def get_victory_condition(self) -> TriggerCondition:
        return self._logic.get_victory_condition()

    def make_requirement(
        self,
        name: str,
        region: Region,
        amount: int = 1,
        type: RequirementType = RequirementType.NONE
    ) -> A1800Requirement:
        return make_requirement(self, name, region, amount=amount, type=type)


__all__ = [
    "A1800Data",
    "A1800EventItem",
    "A1800Region",
    "A1800Requirement",
    "A1800Unlock",
    "ALL_REGIONS",
    "DLC",
    "ITEM_NAME_GROUPS",
    "ITEM_NAME_TO_AP_CODE",
    "LOCATION_NAME_GROUPS",
    "LOCATION_NAME_TO_AP_CODE",
    "ParsedOptions",
    "Region",
    "RequirementType",
    "START_REGION",
    "Trigger",
    "TriggerAction",
    "TriggerActionType",
    "TriggerCondition",
    "TriggerConditionType",
    "UnlockType",
]
