from dataclasses import dataclass
from typing import Optional

from BaseClasses import Location, Region as APRegion

from .data import ANNO_DATA, Region


@dataclass
class A1800LocationData:
    name: str
    region: Region
    population: Optional[str] = None
    amount: Optional[int] = None
    population_guid: Optional[int] = None
    ap_code: Optional[int] = None
    is_event: bool = False


class A1800Location(Location):
    game: str = "Anno 1800"
    data: A1800LocationData

    def __init__(self, player: int, data: A1800LocationData, parent: APRegion):
        super().__init__(player, data.name, None if data.is_event else data.ap_code, parent)
        self.show_in_spoiler = not data.is_event
        self.data = data


class _Locations:
    _unlock_location_data_list: list[A1800LocationData] = []
    _event_location_data_list: list[A1800LocationData] = []
    _location_data_list: list[A1800LocationData] = []

    def process_locations(self):
        self._unlock_location_data_list = [
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

        self._event_location_data_list = [
            A1800LocationData(
                location.ap_location_name,
                location.region,
                is_event=True
            ) for location in ANNO_DATA.get_event_locations() if location.is_progressive
        ]

        self._location_data_list = [
            *self._unlock_location_data_list,
            *self._event_location_data_list,
        ]

    def get_unlock_location_data_list(self) -> list[A1800LocationData]:
        return self._unlock_location_data_list

    def get_event_location_data_list(self) -> list[A1800LocationData]:
        return self._event_location_data_list

    def get_location_data_list(self) -> list[A1800LocationData]:
        return self._location_data_list


LOCATIONS = _Locations()
