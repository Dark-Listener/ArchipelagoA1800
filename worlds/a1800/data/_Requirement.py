from dataclasses import dataclass, field

from ._Enums import Region, RequirementType
from ._EventItems import EVENT_ITEMS
from ._Products import PRODUCTS
from ._Unlocks import UNLOCKS


@dataclass(frozen=True)
class A1800Requirement:
    name: str
    region: Region
    amount: int = 1
    type: RequirementType = RequirementType.NONE
    ap_item_names: frozenset[str] = field(default_factory=lambda: frozenset())
    progressive_ap_item_name: str = ""

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
            if unlocks and unlocks[0].progressive_group:
                assert len(unlocks) == 1
                object.__setattr__(self, "progressive_ap_item_name", unlocks[0].progressive_ap_item_name)
                object.__setattr__(self, "amount", unlocks[0].progressive_tier)

        object.__setattr__(self, "ap_item_names", frozenset(ap_item_names))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"({self.name}, {self.region}, {self.type.name}, {self.progressive_ap_item_name}, {self.amount})"
