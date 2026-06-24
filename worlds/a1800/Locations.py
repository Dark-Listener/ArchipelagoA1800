from dataclasses import dataclass
from typing import Optional

from BaseClasses import Location, LocationProgressType, Region as APRegion

from .data import A1800_DATA, Region, START_REGION, TriggerCondition, TriggerConditionType, UnlockType


@dataclass
class A1800LocationData:
    name: str
    region: Region
    guid: Optional[int] = None
    condition: Optional[TriggerCondition] = None
    ap_code: Optional[int] = None
    is_excluded: bool = False
    is_event: bool = False


class A1800Location(Location):
    game: str = "Anno 1800"
    data: A1800LocationData

    def __init__(self, player: int, data: A1800LocationData, parent: APRegion):
        super().__init__(player, data.name, None if data.is_event else data.ap_code, parent)
        self.show_in_spoiler = not data.is_event
        self.progress_type = LocationProgressType.EXCLUDED if data.is_excluded else LocationProgressType.DEFAULT
        self.data = data


class _Locations:
    _unlock_location_data_list: list[A1800LocationData] = []
    _event_location_data_list: list[A1800LocationData] = []
    _location_data_list: list[A1800LocationData] = []

    def init(self):
        self._unlock_location_data_list = [
            A1800LocationData(
                location.ap_location_name,
                location.ap_region or location.condition.region,
                A1800_DATA.get_next_anno_guid(),
                location.condition,
                location.ap_code,
                location.is_excluded,
                False
            ) for location in A1800_DATA.get_unlock_locations()
            if not UnlockType.META in location.type_
            and (location.condition.type_ != TriggerConditionType.SESSION_ENTER
                 or location.condition.session.region != START_REGION
                 or A1800_DATA.find_session(location.condition.session).requirements)
        ]

        self._event_location_data_list = [
            A1800LocationData(
                location.ap_location_name,
                location.ap_region or location.region,
                is_event=True
            ) for location in A1800_DATA.get_event_locations() if location.is_progression
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
