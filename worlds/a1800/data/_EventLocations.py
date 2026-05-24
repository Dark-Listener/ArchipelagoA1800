from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator

from ._Enums import DLC, NO_REGION, Region, UnlockType
from ._Unlocks import create_unlock_name, UNLOCKS


@dataclass
class A1800EventLocation:
    name: str
    dlc: DLC
    region: Region
    ap_region: Region
    output: str
    ap_location_name: str = ""
    is_progressive: bool = False

    def __post_init__(self) -> None:
        self.ap_location_name: str = create_unlock_name(self.name, self.region, postfix=f" => {self.output}")


class _EventLocations:
    _initialized: bool = False

    def init(self) -> None:
        self._a1800_event_locations = [
            A1800EventLocation(
                unlock.name, unlock.dlc, region, unlock.ap_region, (output if isinstance(output, str) else output[0])
            )
            for unlock in UNLOCKS.get_unlocks() if UnlockType.FACTORY in unlock.type
            for output in unlock.output
            for region in Region.__members__.values() if region in (unlock.region if isinstance(output, str) else output[1])
        ]

        self._initialized = True

    def get_event_locations(self) -> Sequence[A1800EventLocation]:
        return self._a1800_event_locations

    def find_event_locations(self, name: str, output: str = "", region: Region = NO_REGION) -> Iterator[A1800EventLocation]:
        return (event_location for event_location in self._a1800_event_locations if event_location.name == name
                and (not output or event_location.output == output) and event_location.region in region)


EVENT_LOCATIONS = _EventLocations()
