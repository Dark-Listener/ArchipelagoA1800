from dataclasses import dataclass
from typing import Optional

from BaseClasses import Location, Region

from .data import ANNO_DATA, Region as AnnoRegion


@dataclass
class A1800LocationData:
    name: str
    """The name of this location according to Archipelago.

    This needs to be unique within this world."""

    region: AnnoRegion
    """The region of this location."""

    population: Optional[str] = None

    amount: Optional[int] = None

    population_guid: Optional[int] = None

    ap_code: Optional[int] = None
    """Archipelago's internal ID for this location (also known as its "address")."""

    is_event: bool = False
    """Whether this location is an event location with no ID."""


class A1800Location(Location):
    game: str = "Anno 1800"
    data: A1800LocationData

    def __init__(self, player: int, data: A1800LocationData, parent: Region):
        super().__init__(player, data.name, None if data.is_event else data.ap_code, parent)
        self.show_in_spoiler = not data.is_event
        self.data = data


_unlock_location_data_list: list[A1800LocationData]
_event_location_data_list: list[A1800LocationData]
_location_data_list: list[A1800LocationData]


def process_locations():
    global _unlock_location_data_list, _event_location_data_list, _location_data_list

    _unlock_location_data_list = [
        A1800LocationData(
            location.ap_location_name,
            location.unlocking_region,
            location.unlocking_population,
            location.unlocking_amount,
            location.unlocking_guid,
            location.ap_code,
            False
        ) for location in ANNO_DATA.get_unlock_locations()
    ]

    _event_location_data_list = [
        A1800LocationData(
            location.ap_location_name,
            location.region,
            is_event=True
        ) for location in ANNO_DATA.get_event_locations() if location.is_progressive
    ]

    _location_data_list = [
        *_unlock_location_data_list,
        *_event_location_data_list,
    ]


def get_unlock_location_data_list() -> list[A1800LocationData]:
    global _unlock_location_data_list
    return _unlock_location_data_list


def get_event_location_data_list() -> list[A1800LocationData]:
    global _event_location_data_list
    return _event_location_data_list


def get_location_data_list() -> list[A1800LocationData]:
    global _location_data_list
    return _location_data_list
