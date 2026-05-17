from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from BaseClasses import Item, ItemClassification as IC

from .data import ANNO_DATA, A1800EventItem, A1800Unlock

if TYPE_CHECKING:
    from . import A1800World


@dataclass
class A1800ItemData:
    name: str
    ICification: IC
    unlock_guids: list[int] = field(default_factory=lambda: [])
    lock_guids: list[int] = field(default_factory=lambda: [])
    ap_code: Optional[int] = None
    is_event: Optional[bool] = False
    event_locations: list[str] = field(default_factory=lambda: [])


class A1800Item(Item):
    game: str = "Anno 1800"
    data: A1800ItemData

    def __init__(self, player: int, data: A1800ItemData):
        super().__init__(data.name, data.ICification, None if data.is_event else data.ap_code, player)
        self.data = data


_starting_item_data_list: list[A1800ItemData]

_anno_1800_unlock_item_data: list[A1800ItemData]

_anno_1800_event_item_data: list[A1800ItemData]

_unlock_item_data_list: list[A1800ItemData]

_event_item_data_list: list[A1800ItemData]

_item_data_list: list[A1800ItemData]


def _to_item_data(obj: A1800EventItem | A1800Unlock) -> Optional[A1800ItemData]:
    if isinstance(obj, A1800Unlock):
        return A1800ItemData(
            obj.ap_item_name,
            IC.progression if obj.is_progressive else IC.filler,
            list(obj.unlock_guids),
            list(obj.lock_guids),
            obj.ap_code,
            False)
    elif obj.is_progressive:
        return A1800ItemData(
            obj.ap_item_name,
            IC.progression,
            is_event=True,
            event_locations=[event_location.ap_location_name for event_location_name in obj.locations for event_location
                             in ANNO_DATA.find_event_locations(event_location_name, obj.name, obj.region)]
        )
    else:
        return None


def process_items() -> None:
    global _starting_item_data_list
    global _anno_1800_unlock_item_data
    global _anno_1800_event_item_data
    global _unlock_item_data_list
    global _event_item_data_list
    global _item_data_list

    _starting_item_data_list = [
        item_data for item in ANNO_DATA.get_starting_items() for item_data in [_to_item_data(item)] if item_data
    ]

    # Player starts with some timber and enough unlocks to let them produce more
    timber_data = _to_item_data(next(ANNO_DATA.find_event_items("Timber")))
    assert timber_data
    _starting_item_data_list.append(timber_data)

    _anno_1800_unlock_item_data = [item_data for item in ANNO_DATA.get_unlocks()
                                   if not next(ANNO_DATA.find_starting_items(item.name, item.region), None)
                                   for item_data in [_to_item_data(item)] if item_data]

    _anno_1800_event_item_data = [
        item_data for item in ANNO_DATA.get_event_items() for item_data in [_to_item_data(item)] if item_data
    ]

    _unlock_item_data_list = [
        *_anno_1800_unlock_item_data
    ]

    _event_item_data_list = [
        *_anno_1800_event_item_data
    ]

    _item_data_list = [
        *_unlock_item_data_list,
        *_event_item_data_list,
    ]


def create_item(world: "A1800World", item: str | A1800ItemData) -> Item:
    if isinstance(item, A1800ItemData):
        data = item
    else:
        ap_item = ANNO_DATA.find_ap_item(item)
        assert ap_item
        data = _to_item_data(ap_item)
        assert data
    return A1800Item(world.player, data)


def create_and_push_starting_items(world: "A1800World") -> None:
    for item in _starting_item_data_list:
        world.multiworld.push_precollected(create_item(world, item))


def create_itempool(world: "A1800World") -> list[Item]:
    itempool: list[Item] = []

    for data in _item_data_list:
        item = create_item(world, data)

        if data.is_event:
            for location_name in data.event_locations:
                location = world.multiworld.get_location(location_name, world.player)
                location.place_locked_item(item)
        else:
            itempool.append(item)

    world.multiworld.local_early_items[world.player]["OW: Fishery"] = 1
    world.multiworld.local_early_items[world.player]["OW: Sheep Farm"] = 1
    world.multiworld.local_early_items[world.player]["OW: Framework Knitters"] = 1
    world.multiworld.local_early_items[world.player]["OW: Worker Residence"] = 1

    return itempool
