from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ._Enums import Region, RequirementType

if TYPE_CHECKING:
    from . import A1800Data


@dataclass(frozen=True)
class A1800Requirement:
    name: str
    region: Region
    amount: int = 1
    type: RequirementType = RequirementType.NONE
    ap_item_names: frozenset[str] = field(default_factory=lambda: frozenset())
    progressive_ap_item_name: str = ""

    def post_init(self, A1800_DATA: "A1800Data") -> None:
        if self.type == RequirementType.NONE:
            if next(A1800_DATA.find_products(self.name), None):
                object.__setattr__(self, "type", RequirementType.PRODUCT)
            elif next(A1800_DATA.find_unlocks(self.name), None):
                object.__setattr__(self, "type", RequirementType.UNLOCK)

        ap_item_names: list[str] = []
        if self.type == RequirementType.PRODUCT:
            event_items = list(A1800_DATA.find_event_items(self.name, self.region))
            ap_item_names += [event_item.ap_item_name for event_item in event_items]
        elif self.type == RequirementType.UNLOCK:
            unlocks = list(A1800_DATA.find_unlocks(self.name, self.region))
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


def make_requirement(
        A1800_DATA: "A1800Data",
        name: str, region: Region,
        amount: int = 1,
        type: RequirementType = RequirementType.NONE,
) -> A1800Requirement:
    a1800_requirement = A1800Requirement(name, region, amount=amount, type=type)
    a1800_requirement.post_init(A1800_DATA)
    return a1800_requirement
