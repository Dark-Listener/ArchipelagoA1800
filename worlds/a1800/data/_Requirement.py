from dataclasses import dataclass, field
from enum import auto, Enum

from ._EventItem import find_event_items
from ._Product import find_products
from ._Region import Region
from ._Unlock import find_unlocks


class RequirementType(Enum):
    NONE = 0
    PRODUCT = auto()
    UNLOCK = auto()


@dataclass(frozen=True)
class A1800Requirement:
    name: str
    region: Region
    type: RequirementType = RequirementType.NONE
    ap_item_names: frozenset[str] = field(default_factory=lambda: frozenset())

    def __post_init__(self) -> None:
        if self.type == RequirementType.NONE:
            if next(find_products(self.name), None):
                object.__setattr__(self, "type", RequirementType.PRODUCT)
            elif next(find_unlocks(self.name), None):
                object.__setattr__(self, "type", RequirementType.UNLOCK)

        ap_item_names: list[str] = []
        if self.type == RequirementType.PRODUCT:
            event_items = list(find_event_items(self.name, self.region))
            ap_item_names += [event_item.ap_item_name for event_item in event_items]
        elif self.type == RequirementType.UNLOCK:
            unlocks = list(find_unlocks(self.name, self.region))
            ap_item_names += [unlock.ap_item_name for unlock in unlocks]
        object.__setattr__(self, "ap_item_names", frozenset(ap_item_names))
