from collections.abc import Callable, Iterable
from copy import deepcopy
from dataclasses import dataclass
from itertools import groupby
from os import walk
from os.path import dirname, join, relpath
from typing import Any, TYPE_CHECKING, Optional
from zipfile import ZipFile, ZIP_DEFLATED

import jinja2

from Utils import __version__, get_text_after
from worlds.Files import APPlayerContainer

from .data import A1800_DATA, DLC, Region, Session, Trigger, TriggerAction, TriggerActionType, TriggerCondition, TriggerConditionType
from .Items import A1800Item
from .Locations import A1800Location

if TYPE_CHECKING:
    from . import A1800World


@dataclass
class _Quest:
    guid: int
    name: str
    description_guid: int
    quest_giver: int
    max_solve: int
    delay: int
    visible: bool
    condition: TriggerCondition
    pre_condition: Optional[TriggerCondition]


@dataclass
class _QuestPool:
    guid: int
    name: str
    quests: list[tuple[int, int]]
    max_quests: int
    pre_condition: Optional[TriggerCondition]


def _get_condition_with_dlc(condition: TriggerCondition, condition_dlc: set[DLC]) -> TriggerCondition:
    new_conditions: list[TriggerCondition] = []

    for dlc in condition_dlc:
        if dlc == DLC.VANILLA:
            continue
        elif DLC.VANILLA in dlc:
            dlc ^= DLC.VANILLA

        new_conditions.append(TriggerCondition.ACTIVE_DLC(dlc))

    if not new_conditions:
        return condition

    if len(new_conditions) == 1:
        if condition.type_ == TriggerConditionType.ALL:
            return TriggerCondition.ALL(*condition.conditions, *new_conditions)
        else:
            return TriggerCondition.ALL(condition, *new_conditions)
    else:
        if condition.type_ == TriggerConditionType.ALL:
            return TriggerCondition.ALL(*condition.conditions, TriggerCondition.ANY(*new_conditions))
        else:
            return TriggerCondition.ALL(condition, TriggerCondition.ANY(*new_conditions))


def _get_allowed_goods_and_ships_by_session(world: "A1800World", player: int) -> dict[Session, dict[str, bool]]:
    multiworld = world.multiworld

    sessions = {session.session for session in A1800_DATA.get_sessions()}
    session_requirements = {session.session: {requirement.name for requirement in session.requirements}
                            for session in A1800_DATA.get_sessions() if session.session != Session.OW}

    gathered: set[str] = set()
    allowed_goods_and_ships_by_session: dict[Session, dict[str, Any]] = dict()
    for sphere in multiworld.get_spheres():
        for location in sphere:
            if isinstance(location.item, A1800Item) and location.item.player == player:
                if "Expedition" in location.item.name:
                    gathered.add(location.item.name.split(": ")[-2] + ": " + location.item.name.split(": ")[-1])
                else:
                    gathered.add(location.item.name.split(": ")[-1])

        for session in sessions:
            if session == Session.OW:
                continue
            if not session in allowed_goods_and_ships_by_session and session_requirements[session].issubset(gathered):
                allowed_goods_and_ships_by_session[session] = {
                    "Bricks": "Bricks" in gathered,
                    "Steel Beams": "Steel Beams" in gathered,
                    "Coal": "Coal" in gathered,
                    "Gunboat": "Gunboat" in gathered,
                    "Schooner": "Schooner" in gathered,
                    "Frigate": "Frigate" in gathered,
                    "Clipper": "Clipper" in gathered,
                }

        if set(allowed_goods_and_ships_by_session.keys()) | {Session.OW} == sessions:
            break

    for session in set(Session.__members__.values()) - sessions:
        allowed_goods_and_ships_by_session[session] = {
            "Bricks": False,
            "Steel Beams": False,
            "Coal": False,
            "Gunboat": False,
            "Schooner": False,
            "Frigate": False,
            "Clipper": False,
        }

    return allowed_goods_and_ships_by_session


def _adapt_hacienda_unlocks(locations: list[A1800Location]) -> None:
    for location in locations:
        if location.item and isinstance(location.item, A1800Item) and location.data.condition:
            if "Hacienda" in location.item.data.name and "Quarters" in location.item.data.name:
                if "Jornalero" in location.item.data.name:
                    unlock_name = "Jornalero Residence"
                    guid = 101254
                elif "Obrera" in location.item.data.name:
                    unlock_name = "Obrero Residence"
                    guid = 101255
                elif "Artista" in location.item.data.name:
                    unlock_name = "Artista Residence"
                    guid = 5405
                else:
                    assert False, f"Somehow found Hacienda Quarter with wrong population in name: {location.item.data.name}"
                new_condition = TriggerCondition.COUNTER(unlock_name, Region.NW, 1, guid=guid)
                if location.data.condition.type_ == TriggerConditionType.ALL:
                    location.data.condition.conditions.append(new_condition)
                else:
                    location.data.condition = TriggerCondition.ALL(location.data.condition, new_condition)
                location.data.condition.post_init()


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
    free_goods_and_ships_template = template_env.get_template(
        "data/config/export/main/asset/free_goods_and_ships.include.xml")
    incidents_template = template_env.get_template("data/config/export/main/asset/incidents.include.xml")
    meta_products_template = template_env.get_template("data/config/export/main/asset/meta_products.include.xml")
    notifications_template = template_env.get_template("data/config/export/main/asset/notifications.include.xml")
    quests_template = template_env.get_template("data/config/export/main/asset/quests.include.xml")
    triggers_template = template_env.get_template("data/config/export/main/asset/triggers.include.xml")
    texts_chinese_template = template_env.get_template("data/config/gui/texts_chinese.xml")
    texts_english_template = template_env.get_template("data/config/gui/texts_english.xml")
    texts_french_template = template_env.get_template("data/config/gui/texts_french.xml")
    texts_german_template = template_env.get_template("data/config/gui/texts_german.xml")
    texts_italian_template = template_env.get_template("data/config/gui/texts_italian.xml")
    texts_japanese_template = template_env.get_template("data/config/gui/texts_japanese.xml")
    texts_korean_template = template_env.get_template("data/config/gui/texts_korean.xml")
    texts_polish_template = template_env.get_template("data/config/gui/texts_polish.xml")
    texts_russian_template = template_env.get_template("data/config/gui/texts_russian.xml")
    texts_spanish_template = template_env.get_template("data/config/gui/texts_spanish.xml")
    texts_taiwanese_template = template_env.get_template("data/config/gui/texts_taiwanese.xml")
    set_is_unlocked_template = template_env.get_template("data/archipelago/scripts/set_is_unlocked/set_is_unlocked.py")

    # get data for templates
    mod_name = f"AP-{multiworld.seed_name}-P{player}-{multiworld.get_file_safe_player_name(player)}"
    versioned_mod_name = mod_name + "-" + __version__

    locations = [location for location in multiworld.get_filled_locations(
        player) if isinstance(location, A1800Location) and not location.is_event]

    if not A1800_DATA.get_parsed_options().allow_hacienda_residences_upon_unlock:
        _adapt_hacienda_unlocks(locations)

    def _get_trigger_key(location: A1800Location) -> tuple[Any, ...]:
        return (location.data.condition or TriggerCondition.FALSE()).get_sort_key()

    items_found_guid = A1800_DATA.get_next_anno_guid()
    received_guid = A1800_DATA.get_next_anno_guid()

    meta_products_by_name = {
        "int_receive_index": A1800_DATA.get_next_anno_guid()
    }

    def _get_notification_trigger(groups: tuple[tuple[Any, ...], Iterable[A1800Location]]) -> Trigger:
        locations = list(groups[1])
        condition = locations[0].data.condition or TriggerCondition.FALSE()
        text = f"[AssetData({items_found_guid}) Text] <b>{condition.ap_location_name}</b>:<br/>"
        for location in locations:
            if location.item:
                if location.item.player == player:
                    text += f"- <b>{location.item.name}</b><br/>"
                else:
                    text += f"- {multiworld.get_player_name(location.item.player)}'s <b>{location.item.name}</b><br/>"
        text = text[:-5]
        return Trigger(
            condition,
            TriggerAction.SIDE_NOTIFICATION(A1800_DATA.get_next_anno_guid(), text),
            guid=A1800_DATA.get_next_anno_guid()
        )

    def _get_unlock_triggers(groups: tuple[tuple[Any, ...], Iterable[A1800Location]]) -> list[Trigger]:
        return [Trigger(
            deepcopy(location.data.condition) or TriggerCondition.FALSE(),
            TriggerAction.UNLOCK([location.data.guid or 0] + (location.item.data.unlock_guids if location.item and isinstance(
                location.item, A1800Item) and location.item.player == player else []))
        ) for location in groups[1]]

    notification_triggers = list(map(_get_notification_trigger, groupby(
        sorted(locations, key=_get_trigger_key), key=_get_trigger_key)))

    for location in locations:
        if location.item and isinstance(location.item, A1800Item) and location.data.condition:
            location.data.condition = _get_condition_with_dlc(location.data.condition, location.item.data.dlc)

    triggers_grouped_by_condition_and_dlc = list(map(_get_unlock_triggers, groupby(
        sorted(locations, key=_get_trigger_key), key=_get_trigger_key)))

    location_triggers = [Trigger.from_list([trigger for trigger in triggers], guid=A1800_DATA.get_next_anno_guid())
                         for triggers in triggers_grouped_by_condition_and_dlc]

    incident_feature_guids = {
        "FireIncidents_SA": A1800_DATA.get_next_anno_guid(),
        "RiotIncidents_SA": A1800_DATA.get_next_anno_guid(),
        "IllnessIncidents_SA": A1800_DATA.get_next_anno_guid(),
        "ExplosionIncidents_SA": A1800_DATA.get_next_anno_guid(),
    }

    expedition_unlocks = {
        "Expedition: New World": Session.NW.expedition_unlock_guid,
        "Expedition: Cape Trelawney": Session.CT.expedition_unlock_guid,
        "Expedition: The Arctic": Session.AR.expedition_unlock_guid,
        "Expedition: Enbesa": Session.EN.expedition_unlock_guid,
    }

    victory_quest = _Quest(
        A1800_DATA.get_next_anno_guid(),
        "Victory Quest",
        A1800_DATA.get_next_anno_guid(),
        75,
        1,
        5000,
        True,
        A1800_DATA.get_victory_condition(),
        None
    )

    victory_quest_pool = _QuestPool(
        A1800_DATA.get_next_anno_guid(),
        "Victory QuestPool",
        [(victory_quest.guid, 10)],
        1,
        TriggerCondition.ACTIVE_DLC(A1800_DATA.get_victory_dlcs())
    )

    victory_guid = A1800_DATA.get_next_anno_guid()
    victory_trigger = Trigger(
        TriggerCondition.QUEST_COMPLETE(
            A1800_DATA.get_victory_condition().ap_location_name, victory_quest.guid, set()),
        [TriggerAction.UNLOCK([victory_guid])],
        guid=A1800_DATA.get_next_anno_guid()
    )

    start_trigger = Trigger(
        TriggerCondition.TRUE(ap_location_name="Game Start"),
        [TriggerAction.UNLOCK(list(set([guid for item in multiworld.precollected_items[player] if isinstance(item, A1800Item)
                                        for guid in item.data.unlock_guids])))],
        guid=A1800_DATA.get_next_anno_guid()
    )

    palace_ministry_unhide_trigger = Trigger(
        TriggerCondition.ALL(TriggerCondition.UNLOCK(
            "Palace", Region.OW, guid=249947),
            TriggerCondition.ACTIVE_DLC(DLC.SEAT_OF_POWER)
        ),
        TriggerAction.UNLOCK([], [269602]),
        guid=A1800_DATA.get_next_anno_guid()
    )

    location_data_by_guid = {location.data.guid: (location.address, False)
                             for location in locations if location.data.guid}

    guids_by_ap_code = {
        unlock.ap_code: (list(unlock.unlock_guids), 0) for unlock in A1800_DATA.get_unlocks() if unlock.ap_code
    } | {
        location.item.code: (location.item.data.unlock_guids, location.data.guid) for location in locations
        if location.data.guid and location.item and isinstance(location.item, A1800Item) and location.item.code
    }

    notifications_by_ap_code = {
        ap_code: (
            unlock_guids[0] if unlock_guids else 0,
            A1800_DATA.get_next_anno_guid(),
            A1800_DATA.get_next_anno_guid(),
            f"[AssetData({received_guid}) Text] <b>{next(unlock for unlock in A1800_DATA.get_unlocks() if unlock.ap_code == ap_code).ap_item_name}</b>"
        ) for ap_code, (unlock_guids, _) in guids_by_ap_code.items()
    }

    lock_guids_by_trigger: dict[int, tuple[list[int], list[int]]] = {}
    for unlock in A1800_DATA.get_unlocks():
        for lock_guid, unhide_trigger_guids, unlock_trigger_guids in unlock.lock_guids:
            for unhide_trigger_guid in unhide_trigger_guids:
                if not unhide_trigger_guid in lock_guids_by_trigger:
                    lock_guids_by_trigger[unhide_trigger_guid] = ([], [])

                lock_guids_by_trigger[unhide_trigger_guid][0].append(lock_guid)

            for unlock_trigger_guid in unlock_trigger_guids:
                if not unlock_trigger_guid in lock_guids_by_trigger:
                    lock_guids_by_trigger[unlock_trigger_guid] = ([], [])

                lock_guids_by_trigger[unlock_trigger_guid][1].append(lock_guid)

    for trigger_guid, (unhide_guids, unlock_guids) in lock_guids_by_trigger.items():
        lock_guids_by_trigger[trigger_guid] = (sorted(list(set(unhide_guids))), sorted(list(set(unlock_guids))))

    template_data: dict[str, Any] = {
        "Region": Region,
        "Session": Session,
        "TriggerActionType": TriggerActionType,
        "TriggerCondition": TriggerCondition,
        "TriggerConditionType": TriggerConditionType,
        "parsed_options": A1800_DATA.get_parsed_options(),
        "lock_guids_by_trigger": {k: v for k, v in sorted(lock_guids_by_trigger.items(), key=lambda item: item[0])},
        "locations": locations,
        "location_triggers": location_triggers,
        "notification_triggers": notification_triggers,
        "notifications_by_ap_code": notifications_by_ap_code,
        "meta_products_by_name": meta_products_by_name,
        "start_trigger": start_trigger,
        "palace_ministry_unhide_trigger": palace_ministry_unhide_trigger,
        "victory_quest": victory_quest,
        "victory_quest_pool": victory_quest_pool,
        "victory_trigger": victory_trigger,
        "incident_feature_guids": incident_feature_guids,
        "expedition_unlocks": expedition_unlocks,
        "recipe_unlocks": A1800_DATA.get_recipe_unlocks(),
        "allowed_goods_and_ships_by_session": _get_allowed_goods_and_ships_by_session(world, player),
        "cape_trelawney_free_clipper_guid": A1800_DATA.get_next_anno_guid(),
        "enbesa_second_clipper_guid": A1800_DATA.get_next_anno_guid(),
    }

    anno_mod_data: dict[str, Any] = {
        "mod_name": versioned_mod_name,
        "slot_name": world.player_name,
        "seed_name": multiworld.seed_name,
        "ap_version": __version__,
    }

    text_data: dict[str, Any] = {
        "TriggerActionType": TriggerActionType,
        "notification_triggers": notification_triggers,
        "notifications_by_ap_code": notifications_by_ap_code,
        "victory_quest": victory_quest,
        "items_found_guid": items_found_guid,
        "received_guid": received_guid,
    }

    raw_data: dict[str, Any] = {
        "victory_guid": victory_guid,
        "location_data_by_guid": location_data_by_guid,
        "guids_by_ap_code": guids_by_ap_code,
        "notifications_by_ap_code": notifications_by_ap_code,
        "meta_products_by_name": meta_products_by_name,
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

    def _get_writing_task(template: jinja2.Template, data: dict[str, Any]) -> Callable[[], tuple[str, str | bytes]]:
        return lambda: (template.name or "", template.render(**data))

    mod.writing_tasks += [
        _get_writing_task(modinfo_template, anno_mod_data),
        _get_writing_task(readme_en_template, anno_mod_data),
        _get_writing_task(readme_de_template, anno_mod_data),
        _get_writing_task(on_game_loaded_template, anno_mod_data),
        _get_writing_task(data_py_template, raw_data),
        _get_writing_task(data_lua_template, raw_data),
        _get_writing_task(free_goods_and_ships_template, template_data),
        _get_writing_task(incidents_template, template_data),
        _get_writing_task(meta_products_template, template_data),
        _get_writing_task(notifications_template, template_data),
        _get_writing_task(quests_template, template_data),
        _get_writing_task(triggers_template, template_data),
        _get_writing_task(texts_chinese_template, text_data),
        _get_writing_task(texts_english_template, text_data),
        _get_writing_task(texts_french_template, text_data),
        _get_writing_task(texts_german_template, text_data),
        _get_writing_task(texts_italian_template, text_data),
        _get_writing_task(texts_japanese_template, text_data),
        _get_writing_task(texts_korean_template, text_data),
        _get_writing_task(texts_polish_template, text_data),
        _get_writing_task(texts_russian_template, text_data),
        _get_writing_task(texts_spanish_template, text_data),
        _get_writing_task(texts_taiwanese_template, text_data),
    ]

    for location_guid in location_data_by_guid.keys():
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

    # write the mod file
    mod.write()
