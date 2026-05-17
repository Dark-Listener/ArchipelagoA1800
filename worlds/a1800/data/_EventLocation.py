from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator

from ._Dlc import DLC
from ._Region import NO_REGION, Region
from ._Unlock import create_unlock_name, get_unlocks, UnlockType


@dataclass
class A1800EventLocation:
    name: str
    dlc: DLC
    region: Region
    output: str
    ap_location_name: str = ""
    is_progressive: bool = False

    def __post_init__(self) -> None:
        self.ap_location_name: str = create_unlock_name(self.name, self.region, postfix=f" => {self.output}")


_a1800_event_locations = [
    A1800EventLocation(unlock.name, unlock.dlc, region, output)
    for unlock in get_unlocks() if UnlockType.FACTORY in unlock.type
    for output in unlock.output
    for region in Region.__members__.values() if region in unlock.region]


def get_event_locations() -> Sequence[A1800EventLocation]:
    global _a1800_event_locations
    return _a1800_event_locations


def find_event_locations(name: str, output: str = "", region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
    global a1800_event_locations
    return (event_location for event_location in _a1800_event_locations if event_location.name == name
            and (not output or event_location.output == output) and event_location.region in region)
