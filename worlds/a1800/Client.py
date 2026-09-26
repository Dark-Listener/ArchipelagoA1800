# pyright: reportOptionalMemberAccess=false
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from pathlib import Path
from typing import Callable, Optional

from CommonClient import ClientCommandProcessor, CommonContext, logger, server_loop, gui_enabled, get_base_parser
from NetUtils import ClientStatus, NetworkItem
from settings import get_settings
from Utils import Version, __version__, tuplize_version

from . import A1800World
from .Settings import A1800Settings
from .rcon.rcon_mmap_client import RCONMMapClient, RCONTimeout

VERSION_COMPATIBILITY = (Version(1, 4, 0), A1800World.world_version)


class A1800Context(CommonContext):
    command_processor = ClientCommandProcessor
    game = "Anno 1800"
    items_handling = 0b111  # full remote
    mod_version: Version = Version(0, 0, 0)

    def __init__(self, server_address: Optional[str], password: Optional[str], a1800_mods_folder_path: Path):
        super(A1800Context, self).__init__(server_address, password)
        self.send_index: int = 0
        self.rcon_mmap_client: RCONMMapClient = RCONMMapClient()
        self.a1800_mods_folder_path = a1800_mods_folder_path

    async def game_auth(self) -> bool:
        if not self.rcon_mmap_client.connected:
            try:
                self.rcon_mmap_client.connect()
            except FileNotFoundError:
                logger.warning(f"Could not find communication file: {self.rcon_mmap_client.file_path}")
                logger.warning("Please create/load into an Anno 1800 savegame to create it and unpause to connect.")
                self.auth = None
                return False
        if not self.rcon_mmap_client.connected:
            self.auth = None
            logger.warning(
                "Couldn't connect to Anno 1800. Please create/load into an Anno 1800 savegame and unpause to connect.")
            return False

        if self.auth:
            return True

        try:
            info = json.loads(self.rcon_mmap_client.send_command("/ap-rcon-info") or "{}")
        except RCONTimeout:
            logger.warning(
                "Couldn't retrieve session info. Please create/load into an Anno 1800 savegame and unpause to connect.")
            self.rcon_mmap_client.close()
            self.auth = None
            return False

        if not self.rcon_mmap_client.connected or not info:
            logger.warning(
                "Couldn't retrieve session info. Please create/load into an Anno 1800 savegame and unpause to connect.")
            self.rcon_mmap_client.close()
            self.auth = None
            return False

        self.auth = info.get("slot_name", None)
        self.seed_name = info.get("seed_name", None)
        self.mod_version = tuplize_version(info.get("mod_version", "0.0.0"))

        if not self.auth:
            logger.warning(
                "Couldn't retrieve session info. Please create/load into an Anno 1800 savegame and unpause to connect.")
            self.rcon_mmap_client.close()
            self.auth = None
            return False

        if not (VERSION_COMPATIBILITY[0] <= self.mod_version <= VERSION_COMPATIBILITY[1]):
            logger.warning(
                f"Connected Mod Version {self.mod_version.as_simple_string()} is not compatible with the current client version {A1800World.world_version.as_simple_string()}.")
            logger.warning(
                f"Current client is compatible with mod versions {VERSION_COMPATIBILITY[0].as_simple_string()} - {VERSION_COMPATIBILITY[1].as_simple_string()}")
            self.rcon_mmap_client.close()
            self.auth = None
            return False

        return True

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(A1800Context, self).server_auth(password_requested)

        if not self.auth:
            raise Exception("Please connect to Anno 1800 before connecting to the Archipelago server.")

        await self.send_connect()

    def run_gui(self):
        from kvui import GameManager

        class A1800Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago"),
            ]
            base_title = "Archipelago Anno 1800 Client"

        self.ui = A1800Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")


async def a1800_game_watcher(ctx: A1800Context):
    next_sync = time.perf_counter() + 1
    next_connect = time.perf_counter()
    try:
        while not ctx.exit_event.is_set():
            await asyncio.sleep(0.1)

            if not ctx.auth and time.perf_counter() > next_connect:
                await ctx.game_auth()
                if not ctx.auth:
                    logger.info("Retrying in 5s...")
                    next_connect = time.perf_counter() + 5
                else:
                    logger.info(f"Successfully reconnected to Anno 1800.")

            if ctx.auth and time.perf_counter() > next_sync:
                next_sync = time.perf_counter() + 1
                data = None
                try:
                    data = json.loads(ctx.rcon_mmap_client.send_command("/ap-sync") or "{}")
                except RCONTimeout:
                    logger.warning(
                        "Anno 1800 Client has lost connection. Did you open an expedition, pause or quit the game?")
                    logger.info("Attempting to reconnect...")
                    ctx.auth = None
                if not ctx.rcon_mmap_client.connected or not ctx.auth:
                    pass  # not connected or auth failed, wait for new attempt
                elif not data:
                    logger.warning("No data received for /ap-sync. Something went very wrong!")
                elif data.get("slot_name") != ctx.auth:
                    logger.warning(
                        f"Connected World is not the expected one: {data.get('slot_name', 'None')} != {ctx.auth}")
                elif data.get("seed_name") != ctx.seed_name:
                    logger.warning(
                        f"Connected Multiworld is not the expected one: {data.get('seed_name', 'None')} != {ctx.seed_name}")
                elif tuplize_version(data.get("mod_version", "0.0.0")) != ctx.mod_version:
                    logger.warning(
                        f"Connected Mod Version is not the expected one: {data.get('mod_version', '0.0.0')} != {ctx.mod_version.as_simple_string()}")
                else:
                    locations_checked: set[int] = {int(location_id)
                                                   for location_id in data.get("locations_checked", [])}
                    hints_found: set[tuple[int, int]] = {(int(location_id), int(player))
                                                         for (location_id, player) in data.get("hints_found", [])}
                    victory = data.get("victory")

                    if not ctx.finished_game and victory:
                        await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])
                        ctx.finished_game = True

                    if ctx.locations_checked != locations_checked:
                        ctx.locations_checked = locations_checked
                        await ctx.check_locations(ctx.locations_checked)

                    hints_sent = {(int(hint["location"]), int(hint["finding_player"]))
                                  for hint in ctx.stored_data.get(f"_read_hints_{ctx.team}_{ctx.slot}", [])}

                    if hints_found - hints_sent:
                        new_hints = hints_found - hints_sent
                        hints_by_player: dict[int, list[int]] = {}
                        for hint_location, hint_player in new_hints:
                            if (hint_player != ctx.slot) or (hint_location not in ctx.locations_checked):
                                if not hint_player in hints_by_player:
                                    hints_by_player[hint_player] = []
                                hints_by_player[hint_player].append(hint_location)
                        if hints_by_player:
                            await ctx.send_msgs([{"cmd": "CreateHints", "locations": locations, "player": hint_player} for hint_player, locations in hints_by_player.items()])

    except Exception as e:
        logging.exception(e)
        logging.fatal("Aborted Anno 1800 Game Watcher")
        ctx.exit_event.set()


async def a1800_server_watcher(ctx: A1800Context):
    try:
        while not ctx.exit_event.is_set():
            if ctx.auth:
                while ctx.send_index < len(ctx.items_received):
                    transfer_item: NetworkItem = ctx.items_received[ctx.send_index]
                    item_id = transfer_item.item
                    try:
                        ctx.rcon_mmap_client.send_command(f"/ap-receive-item {item_id} {ctx.send_index}")
                    except RCONTimeout:
                        logger.warning(
                            "Anno 1800 Client has lost connection. Did you open an expedition, pause or quit the game?")
                        logger.info("Attempting to reconnect...")
                        ctx.auth = None
                        break
                    ctx.send_index += 1
            await asyncio.sleep(0.1)

    except Exception as e:
        logging.exception(e)
        logging.fatal("Aborted Anno 1800 Server Watcher")
        ctx.exit_event.set()


async def a1800_init(ctx: A1800Context) -> bool:
    if not ctx.a1800_mods_folder_path.exists():
        ctx.gui_error(
            "Fatal Error", f"Path {ctx.a1800_mods_folder_path} does not exist or could not be accessed.")
        ctx.exit_event.set()
        return False
    if not ctx.a1800_mods_folder_path.is_dir():
        ctx.gui_error("Fatal Error", f"Path {ctx.a1800_mods_folder_path} is not a folder.")
        ctx.exit_event.set()
        return False

    mods = [mod for mod in ctx.a1800_mods_folder_path.iterdir()]

    mod_regex = re.compile(fr"AP-(\d*)-P(\d*)-(.*)-.*")
    mod_path = None
    for mod in mods:
        if mod.name.startswith("-"):
            continue
        modinfo_path = (mod / "modinfo.json")
        if modinfo_path.exists() and modinfo_path.is_file():
            data = {}
            with modinfo_path.open("r", encoding="utf-8") as modinfo_file:
                data = json.load(modinfo_file)
            if data and "ModID" in data and mod_regex.search(data["ModID"]):
                mod_path = mod

    if not mod_path:
        logger.warning(
            f"Could not find an enabled Anno 1800 Archipelago mod in mods folder {ctx.a1800_mods_folder_path}.")
        logger.warning(
            f"Make sure the mod folder name does not start with '-'.")
        return False
    else:
        logger.info(f"Found Anno 1800 Archipelago mod at {mod_path}.")

    ctx.rcon_mmap_client.file_path = mod_path / "A1800APCommunication.dat"
    if ctx.rcon_mmap_client.file_path.exists() and ctx.rcon_mmap_client.file_path.is_file():
        logger.info(f"Found communication file at {ctx.rcon_mmap_client.file_path}.")

    try:
        next_connect = time.perf_counter()
        while not ctx.auth and not ctx.exit_event.is_set():
            if time.perf_counter() > next_connect:
                await ctx.game_auth()
                if not ctx.auth:
                    logger.info("Retrying in 5s...")
                    next_connect = time.perf_counter() + 5
            await asyncio.sleep(0.1)

    except Exception as e:
        logger.exception(e, extra={"compact_gui": True})
        msg = "Aborted Anno 1800 Init"
        logger.error(msg)
        ctx.gui_error(msg, e)
        ctx.exit_event.set()
        return False

    logger.info(f"Successfully connected to Anno 1800. Slot name is {ctx.auth}.")
    logger.info("Ready to connect to the Archipelago server via the Connect button or /connect.")
    return True


async def main(make_context: Callable[[], A1800Context]):
    ctx = make_context()
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    successful_launch = await asyncio.create_task(a1800_init(ctx), name="A1800Spinup")
    if successful_launch:
        a1800_server_watch_task = asyncio.create_task(a1800_server_watcher(ctx), name="A1800ServerWatcher")
        a1800_game_watch_task = asyncio.create_task(a1800_game_watcher(ctx), name="A1800GameWatcher")

        await ctx.exit_event.wait()
        ctx.server_address = None

        await a1800_game_watch_task
        await a1800_server_watch_task

    if ctx.rcon_mmap_client:
        ctx.rcon_mmap_client.close()
    await ctx.shutdown()


settings: A1800Settings = get_settings().a1800_options


def launch():
    import colorama
    global executable
    colorama.just_fix_windows_console()

    parser = get_base_parser()
    args = parser.parse_args()

    a1800_mods_folder_path = Path(settings.a1800_mods_folder_path)

    asyncio.run(main(lambda: A1800Context(args.connect, args.password, a1800_mods_folder_path)))

    colorama.deinit()
