from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterator, TYPE_CHECKING

from ._Enums import DLC, NO_REGION, ProductType, Region
from ._Unlocks import create_unlock_name

if TYPE_CHECKING:
    from . import A1800Data


@dataclass
class A1800EventItem:
    name: str
    dlc: set[DLC]
    region: Region
    type: ProductType
    ap_item_name: str = ""
    is_progression: bool = False
    locations: set[str] = field(default_factory=lambda: set())

    def post_init(self, A1800_DATA: "A1800Data") -> None:
        self.ap_item_name: str = create_unlock_name(self.name, self.region, f"{self.type.full_name}: ")

        self.locations: set[str] = {event_location.name for event_location in A1800_DATA.get_event_locations() if event_location.output ==
                                    self.name and event_location.region in self.region}


class EventItems:
    def __init__(self, A1800_DATA: "A1800Data") -> None:
        self._A1800_DATA = A1800_DATA

        self._a1800_event_items = [A1800EventItem(product.name, product.dlc, product.region, product.type)
                                   for product in self._A1800_DATA.get_products()]
        for a1800_event_item in self._a1800_event_items:
            a1800_event_item.post_init(self._A1800_DATA)

    def get_event_items(self) -> Sequence[A1800EventItem]:
        return self._a1800_event_items

    def find_event_items(self, name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
        return (event_item for event_item in self._a1800_event_items if event_item.name == name and region in event_item.region)
