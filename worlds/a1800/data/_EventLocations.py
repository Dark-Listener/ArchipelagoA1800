from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator, TYPE_CHECKING

from ._Enums import DLC, NO_REGION, Region, UnlockType
from ._Unlocks import create_unlock_name

if TYPE_CHECKING:
    from . import A1800Data


@dataclass
class A1800EventLocation:
    name: str
    dlc: set[DLC]
    region: Region
    ap_region: Region
    output: str
    ap_location_name: str = ""
    is_progression: bool = False

    def __post_init__(self) -> None:
        self.ap_location_name: str = create_unlock_name(self.name, self.region, postfix=f" => {self.output}")


class EventLocations:
    def __init__(self, A1800_DATA: "A1800Data") -> None:
        self._A1800_DATA = A1800_DATA

        self._a1800_event_locations = [
            A1800EventLocation(
                unlock.name, unlock.dlc, output_region, unlock.ap_region, output_name
            )
            for unlock in self._A1800_DATA.get_unlocks() if UnlockType.FACTORY in unlock.type_
            for output_name, output_region in unlock.output
        ]

    def append_event_location(self, event_location: A1800EventLocation):
        self._a1800_event_locations.append(event_location)

    def get_event_locations(self) -> Sequence[A1800EventLocation]:
        return self._a1800_event_locations

    def find_event_locations(self, name: str, output: str = "", region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return (event_location for event_location in self._a1800_event_locations if event_location.name == name
                and (not output or event_location.output == output) and event_location.region in region)
