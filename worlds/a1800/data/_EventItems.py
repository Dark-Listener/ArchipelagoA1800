from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterator

from ._Enums import DLC, NO_REGION, ProductType, Region
from ._EventLocations import EVENT_LOCATIONS
from ._Products import PRODUCTS
from ._Unlocks import create_unlock_name


@dataclass
class A1800EventItem:
    name: str
    dlc: set[DLC]
    region: Region
    type: ProductType
    ap_item_name: str = ""
    is_progressive: bool = False
    locations: set[str] = field(default_factory=lambda: set())

    def __post_init__(self) -> None:
        self.ap_item_name: str = create_unlock_name(self.name, self.region, f"{self.type.full_name}: ")

        self.locations: set[str] = {event_location.name for event_location in EVENT_LOCATIONS.get_event_locations() if event_location.output ==
                                    self.name and event_location.region in self.region}


class _EventItems:
    _initialized: bool = False

    def init(self) -> None:
        self._a1800_event_items = [A1800EventItem(product.name, product.dlc, product.region, product.type)
                                   for product in PRODUCTS.get_products()]

        self._initialized = True

    def get_event_items(self) -> Sequence[A1800EventItem]:
        assert self._initialized, "The Anno 1800 event items module was used before it was initialized."
        return self._a1800_event_items

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        assert self._initialized, "The Anno 1800 event items module was used before it was initialized."
        return (event_item for event_item in self._a1800_event_items if event_item.name == name and region in event_item.region)


EVENT_ITEMS = _EventItems()
