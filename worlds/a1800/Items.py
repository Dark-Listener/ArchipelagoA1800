from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from BaseClasses import Item, ItemClassification as IC

from .data import ANNO_DATA, A1800EventItem, A1800Unlock, START_REGION, TriggerType

if TYPE_CHECKING:
    from . import A1800World


@dataclass
class A1800ItemData:
    name: str
    ICification: IC
    unlock_guids: list[int] = field(default_factory=lambda: [])
    lock_guids: list[int] = field(default_factory=lambda: [])
    ap_code: Optional[int] = None
    is_early: bool = False
    is_starting_item: bool = False
    is_event: bool = False
    event_locations: list[str] = field(default_factory=lambda: [])


class A1800Item(Item):
    game: str = "Anno 1800"
    data: A1800ItemData

    def __init__(self, player: int, data: A1800ItemData):
        super().__init__(data.name, data.ICification, None if data.is_event else data.ap_code, player)
        self.data = data


def _to_item_data(obj: A1800EventItem | A1800Unlock) -> Optional[A1800ItemData]:
    if isinstance(obj, A1800Unlock):
        is_starting_item: bool = not obj.is_early \
            and obj.trigger.trigger_type == TriggerType.SESSION_ENTER \
            and obj.trigger.session.region == START_REGION \
            and not ANNO_DATA.find_session(obj.trigger.session).requirements
        return A1800ItemData(
            obj.ap_item_name,
            IC.progression if obj.is_progressive else IC.filler,
            list(obj.unlock_guids),
            list(obj.lock_guids),
            obj.ap_code,
            obj.is_early,
            is_starting_item,
            False)
    elif obj.is_progressive:
        # Player starts with some timber and enough unlocks to let them produce more
        # This avoids circular logic blocking the randomizer
        is_starting_item: bool = obj.name == "Timber"
        return A1800ItemData(
            obj.ap_item_name,
            IC.progression,
            is_starting_item=is_starting_item,
            is_event=True,
            event_locations=[event_location.ap_location_name for event_location_name in obj.locations for event_location
                             in ANNO_DATA.find_event_locations(event_location_name, obj.name, obj.region)]
        )
    else:
        return None


def create_item(world: "A1800World", item: str | A1800ItemData) -> Item:
    if isinstance(item, A1800ItemData):
        data = item
    else:
        ap_item = ANNO_DATA.find_ap_item(item)
        assert ap_item, f"Couldn't find item for string {item}"
        data = _to_item_data(ap_item)
        assert data, f"Couldn't create item data for item {ap_item}"
    return A1800Item(world.player, data)


class _Items:
    _start_item_data_list: list[A1800ItemData] = []
    _unlock_item_data_list: list[A1800ItemData] = []
    _event_item_data_list: list[A1800ItemData] = []
    _item_data_list: list[A1800ItemData] = []

    def process_items(self) -> None:
        all_unlock_item_data = [item_data for item in ANNO_DATA.get_unlocks()
                                for item_data in [_to_item_data(item)] if item_data]
        self._unlock_item_data_list = [
            item_data for item_data in all_unlock_item_data if not item_data.is_starting_item]
        self._start_item_data_list += [item_data for item_data in all_unlock_item_data if item_data.is_starting_item]

        self._event_item_data_list = [item_data for item in ANNO_DATA.get_event_items()
                                      for item_data in [_to_item_data(item)] if item_data]
        self._start_item_data_list += [item_data for item_data in self._event_item_data_list if item_data.is_starting_item]

        self._item_data_list = [
            *self._unlock_item_data_list,
            *self._event_item_data_list,
        ]

    def create_and_push_start_items(self, world: "A1800World") -> None:
        for item in self._start_item_data_list:
            world.multiworld.push_precollected(create_item(world, item))

    def create_itempool(self, world: "A1800World") -> list[Item]:
        itempool: list[Item] = []

        for data in self._item_data_list:
            item = create_item(world, data)

            if data.is_event:
                for location_name in data.event_locations:
                    world.multiworld.get_location(location_name, world.player).place_locked_item(item)
            else:
                itempool.append(item)

            if data.is_early:
                world.multiworld.local_early_items[world.player][data.name] = 1

        return itempool


ITEMS = _Items()
