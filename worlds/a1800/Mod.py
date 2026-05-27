from collections.abc import Callable
from itertools import groupby
from os import walk
from os.path import dirname, join, relpath
from typing import Any, TYPE_CHECKING, Optional
from zipfile import ZipFile, ZIP_DEFLATED

import jinja2

from Utils import __version__, get_text_after
from worlds.Files import APPlayerContainer

from .data import A1800_DATA, DLC, Region, Trigger, TriggerType
from .Items import A1800Item
from .Locations import A1800Location

if TYPE_CHECKING:
    from . import A1800World

_GUID_RANGE_START = 1701000000  # Start of Anno 1800 Archipelago Randomizer GUID range
_g_next_guid: int = _GUID_RANGE_START + 3  # -1 GUID offset, 4 GUIDS used for expedition unlocks


def _get_next_guid() -> int:
    global _g_next_guid
    _g_next_guid += 1
    return _g_next_guid


def _get_trigger_with_dlc(trigger: Trigger, trigger_dlc: DLC) -> Trigger:
    if trigger_dlc == DLC.VANILLA:
        return trigger

    new_trigger = Trigger(TriggerType.DLC, trigger_dlc)

    if trigger.trigger_type == TriggerType.ALL:
        return Trigger(TriggerType.ALL, *trigger.triggers, new_trigger)
    else:
        return Trigger(TriggerType.ALL, trigger, new_trigger)


class A1800ModFile(APPlayerContainer):
    game = "A1800"
    compression_method = ZIP_DEFLATED
    writing_tasks: list[Callable[[], tuple[str, str | bytes]]]
    patch_file_ending = ".zip"

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.writing_tasks = []

    def write_contents(self, opened_zipfile: ZipFile):
        if not self.path:
            raise FileNotFoundError(f"Cannot write A1800ModFile due to no path provided.")

        mod_dir = self.path[:-4]  # cut off .zip

        for root, _, files in walk(mod_dir):
            for file in files:
                filename = join(root, file)
                opened_zipfile.write(filename, relpath(filename, join(mod_dir, '..')))

        for task in self.writing_tasks:
            target, content = task()
            opened_zipfile.writestr(target, content)

        super(A1800ModFile, self).write_contents(opened_zipfile)


def generate_mod(world: "A1800World", output_directory: str):
    player = world.player
    multiworld = world.multiworld

    def load_template(name: str):
        import pkgutil
        data = pkgutil.get_data(__name__, "data/mod_template/" + name)
        if data:
            return data.decode(), name, lambda: False
        else:
            return None

    template_env: Optional[jinja2.Environment] = \
        jinja2.Environment(loader=jinja2.FunctionLoader(load_template))
    template_env.trim_blocks = True
    template_env.lstrip_blocks = True

    modinfo_template = template_env.get_template("modinfo.json")
    readme_en_template = template_env.get_template("readme_en.md")
    readme_de_template = template_env.get_template("readme_de.md")
    data_py_template = template_env.get_template("data/archipelago/scripts/data.py")
    data_lua_template = template_env.get_template("data/archipelago/scripts/data.lua")
    on_game_loaded_template = template_env.get_template("data/archipelago/scripts/on_game_loaded.py")
    triggers_template = template_env.get_template("data/config/export/main/asset/triggers.include.xml")
    set_is_unlocked_template = template_env.get_template("data/archipelago/scripts/set_is_unlocked/set_is_unlocked.py")
    ap_receive_item_template = template_env.get_template(
        "data/archipelago/scripts/ap_receive_item/ap_receive_item.lua")

    # get data for templates
    mod_name = f"AP-{multiworld.seed_name}-P{player}-{multiworld.get_file_safe_player_name(player)}"
    versioned_mod_name = mod_name + "-" + __version__

    start_trigger_guid = _get_next_guid()

    trigger_key: Callable[[A1800Location], tuple[Any, ...]] = \
        lambda location: location.data.trigger.get_sort_key() if location.data.trigger else tuple()

    checkable_locations = [location for location in multiworld.get_filled_locations(
        player) if isinstance(location, A1800Location) and not location.is_event]

    for location in checkable_locations:
        if location.item and isinstance(location.item, A1800Item) and location.data.trigger:
            location.data.trigger = _get_trigger_with_dlc(location.data.trigger, location.item.data.dlc)

    palace_ministry_unhide_guid = _get_next_guid()
    trigger_guid_to_locations = {_get_next_guid(): list(locations) for _, locations in groupby(
        sorted(checkable_locations, key=trigger_key), key=trigger_key)}
    victory_trigger_guid = _get_next_guid()

    def location_to_data(location: A1800Location) -> tuple[int, A1800Location, list[int], list[int]]:
        return (
            _get_next_guid(),
            location,
            location.item.data.unlock_guids if location.item and isinstance(location.item, A1800Item) else [],
            []
        )

    trigger_to_location_data = {guid: (locations[0].data.trigger, list(map(location_to_data, locations)))
                                for guid, locations in trigger_guid_to_locations.items()}

    location_guid_data = {location_guid: (location.address, False)
                          for _, (_, locations) in trigger_to_location_data.items()
                          for location_guid, location, _, _ in locations}

    item_id_to_guids = {unlock.ap_code: (list(unlock.unlock_guids), 0) for unlock in A1800_DATA.get_unlocks()} | {
        location.item.code: (unlock_guids, location_guid) for _, (_, locations) in trigger_to_location_data.items()
        for location_guid, location, unlock_guids, _ in locations
        if location.item and isinstance(location.item, A1800Item) and location.item.code
    }

    victory_guid = _get_next_guid()

    start_trigger = Trigger(TriggerType.TRUE)
    start_trigger.ap_location_name = "Game Start"
    starting_guids = list(set([guid for item in multiworld.precollected_items[player] if isinstance(item, A1800Item)
                               for guid in item.data.unlock_guids]))

    expedition_unlocks = [
        ("Expedition: New World", 1701000000),
        ("Expedition: Cape Trelawney", 1701000001),
        ("Expedition: The Arctic", 1701000002),
        ("Expedition: Enbesa", 1701000003),
    ]

    palace_ministry_unhide_trigger = Trigger(TriggerType.ALL, Trigger(
        TriggerType.UNLOCK, 249947, "Palace", Region.OW), Trigger(TriggerType.DLC, DLC.SEAT_OF_POWER))

    template_data: dict[str, Any] = {
        "lock_guid_list": sorted(set([guid for unlock in A1800_DATA.get_unlocks() for guid in unlock.lock_guids])),
        "trigger_to_location_data": trigger_to_location_data,
        "Region": Region,
        "Trigger": Trigger,
        "TriggerType": TriggerType,
        "DLC": DLC,
        "enabled_dlcs": A1800_DATA.get_enabled_dlcs(),
        "location_guid_data": location_guid_data,
        "item_id_to_guids": item_id_to_guids,
        "start_trigger_guid": start_trigger_guid,
        "start_trigger": start_trigger,
        "start_trigger_data": [(
            starting_guids[0] if starting_guids else 0, None, starting_guids[1:] if len(starting_guids) > 1 else [], []
        )],
        "expedition_unlocks": expedition_unlocks,
        "victory_trigger_guid": victory_trigger_guid,
        "victory_trigger": _get_trigger_with_dlc(A1800_DATA.get_victory_trigger(), A1800_DATA.get_victory_dlcs()),
        "victory_trigger_data": [(victory_guid, None, [], [])],
        "palace_ministry_unhide_guid": palace_ministry_unhide_guid,
        "palace_ministry_unhide_trigger": palace_ministry_unhide_trigger,
        "palace_ministry_unhide_trigger_data": [(0, None, [], [269602])],
        "mod_name": versioned_mod_name,
        "ap_version": __version__,
        "slot_name": world.player_name,
        "seed_name": multiworld.seed_name,
    }

    zipfile_path = join(output_directory, versioned_mod_name + ".zip")
    mod = A1800ModFile(zipfile_path, player=player, player_name=world.player_name)

    if world.zip_path:
        with ZipFile(world.zip_path) as zipfile:
            for file in zipfile.infolist():
                if not file.is_dir() and "/data/mod/" in file.filename:
                    file_path = get_text_after(file.filename, "/data/mod/")
                    mod.writing_tasks.append(lambda arcpath=file_path, content=zipfile.read(file): (arcpath, content))
    else:
        basepath = join(dirname(__file__), "data", "mod")
        for dirpath, _, filenames in walk(basepath):
            base_arc_path = (relpath(dirpath, basepath)).rstrip("/.\\")
            for filename in filenames:
                mod.writing_tasks.append(lambda arcpath=(base_arc_path + "/" + filename),
                                         file_path=join(dirpath, filename): (arcpath, open(file_path, "rb").read()))

    mod.writing_tasks.append(lambda: ("modinfo.json", modinfo_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("readme_en.md", readme_en_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("readme_de.md", readme_de_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("data/archipelago/scripts/data.py", data_py_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("data/archipelago/scripts/data.lua", data_lua_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("data/archipelago/scripts/on_game_loaded.py",
                             on_game_loaded_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("data/config/export/main/asset/triggers.include.xml",
                             triggers_template.render(**template_data)))

    for location_guid in location_guid_data.keys():
        set_is_unlocked_data: dict[str, Any] = {
            "unlocked_guid": location_guid,
            "victory": False,
        }
        mod.writing_tasks.append(lambda location_guid=location_guid, set_is_unlocked_data=set_is_unlocked_data: (
            f"data/archipelago/scripts/set_is_unlocked/set_is_unlocked_{location_guid}.py", set_is_unlocked_template.render(**set_is_unlocked_data)))

    set_is_unlocked_data: dict[str, Any] = {
        "unlocked_guid": victory_guid,
        "victory": True,
    }
    mod.writing_tasks.append(lambda victory_guid=victory_guid, set_is_unlocked_data=set_is_unlocked_data: (
        f"data/archipelago/scripts/set_is_unlocked/set_is_unlocked_{victory_guid}.py", set_is_unlocked_template.render(**set_is_unlocked_data)))

    for item_id, (unlock_guids, location_guid) in item_id_to_guids.items():
        ap_receive_item_data: dict[str, Any] = {
            "unlock_guids": unlock_guids,
            "location_guid": location_guid,
        }
        mod.writing_tasks.append(lambda item_id=item_id, ap_receive_item_data=ap_receive_item_data: (
            f"data/archipelago/scripts/ap_receive_item/ap_receive_item_{item_id}.lua", ap_receive_item_template.render(**ap_receive_item_data)))

    # write the mod file
    mod.write()
