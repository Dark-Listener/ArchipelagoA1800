from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Iterator

from ._Enums import DLC, NO_REGION, Region
from ._EventLocation import get_event_locations
from ._Product import get_products
from ._Unlock import create_unlock_name


@dataclass
class A1800EventItem:
    name: str
    dlc: DLC
    region: Region
    ap_item_name: str = ""
    is_progressive: bool = False
    locations: set[str] = field(default_factory=lambda: set())

    def __post_init__(self) -> None:
        self.ap_item_name: str = create_unlock_name(self.name, self.region, "Produces ")

        self.locations: set[str] = {event_location.name for event_location in get_event_locations() if event_location.output ==
                                    self.name and event_location.region in self.region}


_a1800_event_items = [A1800EventItem(product.name, product.dlc, product.region) for product in get_products()]


def get_event_items() -> Sequence[A1800EventItem]:
    global _a1800_event_items
    return _a1800_event_items


def find_event_items(name: str, region: Region = NO_REGION) -> Iterator[A1800EventItem]:
    global _a1800_event_items
    return (event_item for event_item in _a1800_event_items if event_item.name == name and region in event_item.region)
