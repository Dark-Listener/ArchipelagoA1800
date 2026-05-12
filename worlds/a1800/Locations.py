from dataclasses import dataclass
from typing import Optional

from BaseClasses import Location, Region

from .AnnoData import a1800_location_dict, a1800_population_dict, A1800Unlock, get_requirement_name


@dataclass
class A1800LocationData:
    name: str
    """The name of this location according to Archipelago.

    This needs to be unique within this world."""

    region: str
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


_anno_1800_unlock_location_data: list[A1800LocationData] = [
    A1800LocationData(
        full_name,
        next(iter(a1800_population_dict[location.unlock_population].region)),
        location.unlock_population,
        location.unlock_amount,
        a1800_population_dict[location.unlock_population].guid,
        location.ap_code,
        False
    ) for full_name, location in a1800_location_dict.items() if isinstance(location, A1800Unlock)
]

_anno_1800_event_location_data: list[A1800LocationData]

unlock_location_data_list: list[A1800LocationData] = [
    *_anno_1800_unlock_location_data,
]

event_location_data_list: list[A1800LocationData] = []

location_data_list: list[A1800LocationData] = []


def process_locations():
    from .AnnoData import a1800_event_locations, a1800_required_items

    global _anno_1800_event_location_data
    global event_location_data_list
    global location_data_list

    _anno_1800_event_location_data = [
        A1800LocationData(location.name, next(iter(location.region)), is_event=True)
        for location in a1800_event_locations if not isinstance(location, A1800Unlock)
        if next((
            requirement for requirement in a1800_required_items
            if get_requirement_name(requirement) == location.name.split(" => ")[0]), None) or location.name.split(" => ")[1] == "Victory"
    ]

    event_location_data_list = [
        *_anno_1800_event_location_data,
    ]

    location_data_list = [
        *unlock_location_data_list,
        *event_location_data_list,
    ]
