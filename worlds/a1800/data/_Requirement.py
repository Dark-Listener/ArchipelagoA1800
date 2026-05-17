from dataclasses import dataclass
from enum import auto, Enum
from typing import Callable

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

    def __post_init__(self) -> None:
        if self.type == RequirementType.NONE:
            if next(find_products(self.name), None):
                object.__setattr__(self, "type", RequirementType.PRODUCT)
            elif next(find_unlocks(self.name), None):
                object.__setattr__(self, "type", RequirementType.UNLOCK)


A1800Rule = Callable[[object, int], bool]
