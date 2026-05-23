from dataclasses import dataclass, field

from ._Enums import Region, RequirementType
from ._EventItem import EVENT_ITEMS
from ._Product import PRODUCTS
from ._Unlock import UNLOCKS


@dataclass(frozen=True)
class A1800Requirement:
    name: str
    region: Region
    type: RequirementType = RequirementType.NONE
    ap_item_names: frozenset[str] = field(default_factory=lambda: frozenset())

    def __post_init__(self) -> None:
        if self.type == RequirementType.NONE:
            if next(PRODUCTS.find_products(self.name), None):
                object.__setattr__(self, "type", RequirementType.PRODUCT)
            elif next(UNLOCKS.find_unlocks(self.name), None):
                object.__setattr__(self, "type", RequirementType.UNLOCK)

        ap_item_names: list[str] = []
        if self.type == RequirementType.PRODUCT:
            event_items = list(EVENT_ITEMS.find_event_items(self.name, self.region))
            ap_item_names += [event_item.ap_item_name for event_item in event_items]
        elif self.type == RequirementType.UNLOCK:
            unlocks = list(UNLOCKS.find_unlocks(self.name, self.region))
            ap_item_names += [unlock.ap_item_name for unlock in unlocks]
        object.__setattr__(self, "ap_item_names", frozenset(ap_item_names))
