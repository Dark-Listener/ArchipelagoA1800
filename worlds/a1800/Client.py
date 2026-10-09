# pyright: reportOptionalMemberAccess=false
from __future__ import annotations

import asyncio
from enum import IntEnum, auto
import json
import logging
import re
import time
from pathlib import Path
from typing import Callable, Optional, TYPE_CHECKING

from CommonClient import ClientCommandProcessor, logger, server_loop, gui_enabled, get_base_parser
from NetUtils import ClientStatus, NetworkItem
from settings import get_settings
from Utils import Version, __version__, tuplize_version

from . import A1800World
from .Settings import A1800Settings
from .rcon.rcon_mmap_client import RCONMMapClient, RCONTimeout

if TYPE_CHECKING:
    import kvui

try:
    from worlds.tracker.TrackerClient import TrackerGameContext  # pyright: ignore[reportAssignmentType]
    from worlds.tracker.TrackerClient import TrackerCommandProcessor as ClientCommandProcessor, UT_VERSION

    tracker_loaded = True
except ModuleNotFoundError as e:
    tracker_loaded = False
    UT_VERSION = ""  # pyright: ignore[reportConstantRedefinition]

    from CommonClient import CommonContext, ClientCommandProcessor

    class TrackerGameContextMixin:
        """Expecting the TrackerGameContext to have these methods."""

        def make_gui(self) -> "type[kvui.GameManager]":
            ...

        def run_generator(self):
            ...

    class TrackerGameContext(CommonContext, TrackerGameContextMixin):
        pass

VERSION_COMPATIBILITY = (Version(1, 4, 0), A1800World.world_version)


class A1800Context(TrackerGameContext):
    class State(IntEnum):
        INIT = auto()
        ERROR_NO_MOD_FOLDER = auto()
        ERROR_NO_COMMUNICATION_FILE = auto()
        ERROR_NO_AUTH_RESPONSE = auto()
        ERROR_NO_INFO_RESPONSE = auto()
        ERROR_VERSION_INCOMPATIBLE = auto()
        ERROR_SERVER_TIMEOUT = auto()
        ERROR_NO_DATA = auto()
        ERROR_AUTH_MISMATCH = auto()
        CONNECTED = auto()

    command_processor = ClientCommandProcessor
    game = "Anno 1800"
    items_handling = 0b111  # full remote
    mod_version: Version = Version(0, 0, 0)
    tags = {"AP"}
    state: State = State.INIT

    def __init__(self, server_address: Optional[str], password: Optional[str]):
        super(A1800Context, self).__init__(server_address, password)
        self.send_index: int = 0
        self.rcon_mmap_client: RCONMMapClient = RCONMMapClient()
        self.a1800_mods_folder_path: Optional[Path] = None
        # Pattern to exclude last '-' once support for 1.4.x is dropped
        self.mod_regex: re.Pattern[str] = re.compile(fr"AP-(\d*)-P(\d*)-(.*)[-_].*")
        self.mod_path: Optional[Path] = None
        self.seed: Optional[str] = None
        self.failed_connects = 0

    def find_a1800_mod(self):
        self.mod_path = None
        self.rcon_mmap_client.close()
        self.rcon_mmap_client.file_path = None
        for mod in self.a1800_mods_folder_path.iterdir():
            if mod.name.startswith("-"):
                continue
            modinfo_path = (mod / "modinfo.json")
            if modinfo_path.exists() and modinfo_path.is_file():
                modinfo = {}
                with modinfo_path.open("r", encoding="utf-8") as modinfo_file:
                    modinfo = json.load(modinfo_file)
                if modinfo and "ModID" in modinfo and self.mod_regex.search(modinfo["ModID"]):
                    self.mod_path = mod

        if self.mod_path:
            logger.info(f"Found Anno 1800 Archipelago mod at {self.mod_path}.")

    async def read_auth(self):
        assert self.mod_path

        apinfo_path = (self.mod_path / "apinfo.json")
        if apinfo_path.exists() and apinfo_path.is_file():
            apinfo = {}
            with apinfo_path.open("r", encoding="utf-8") as modinfo_file:
                apinfo = json.load(modinfo_file)
            if apinfo:
                new_auth = apinfo.get("slot_name", None)
                self.seed = apinfo.get("seed_name", None)
                self.mod_version = tuplize_version(apinfo.get("mod_version", "0.0.0"))
                logger.info(
                    f"Mod offers slot {new_auth} on seed {self.seed} on mod version {self.mod_version.as_simple_string()}.")
                if self.auth and self.auth != new_auth:
                    logger.warning(f"Slot offered by mod will override previously used slot {self.auth}.")
                    logger.warning(
                        "Disconnecting from Archipelago server. Please reconnect to use the updated slot name.")
                    await self.disconnect()
                    self.seed_name = None
                self.auth = new_auth

    # Function to be removed once support for 1.4.x is dropped
    async def retrieve_auth(self):
        try:
            ap_rcon_info = self.rcon_mmap_client.send_command("/ap-rcon-info")
        except RCONTimeout:
            return

        if not ap_rcon_info:
            return

        info = json.loads(ap_rcon_info)

        if not info:
            return

        new_auth = info.get("slot_name", None)
        self.seed = info.get("seed_name", None)
        self.mod_version = tuplize_version(info.get("mod_version", "0.0.0"))

        logger.info(
            f"Mod offers slot {new_auth} on seed {self.seed} on mod version {self.mod_version.as_simple_string()}.")
        if self.auth and self.auth != new_auth:
            logger.warning(f"Slot offered by mod will override previously used slot {self.auth}.")
            logger.warning("Disconnecting from Archipelago server. Please reconnect to use the updated slot name.")
            await self.disconnect()
            self.seed_name = None
        self.auth = new_auth

    async def connect_to_game(self) -> None:
        if not self.mod_path or not self.mod_path.exists() or not self.mod_path.is_dir():
            self.find_a1800_mod()
            if not self.mod_path:
                if self.state != self.State.ERROR_NO_MOD_FOLDER:
                    self.state = self.State.ERROR_NO_MOD_FOLDER
                    logger.warning(
                        f"Could not find an enabled Anno 1800 Archipelago mod in mods folder {self.a1800_mods_folder_path}.")
                    logger.info(
                        f"To connect, please install a mod and make sure the mod folder name does not start with '-'.")
                    self.failed_connects = 0
                return

        if not self.auth or not self.seed or not self.mod_version or self.mod_version.as_simple_string() == "0.0.0":
            await self.read_auth()

            # Add error handling here after support for 1.4.x is dropped

        if not self.rcon_mmap_client.file_path:
            self.rcon_mmap_client.file_path = self.mod_path / "A1800APCommunication.dat"

            if not self.rcon_mmap_client.file_path.exists() or not self.rcon_mmap_client.file_path.is_file():
                if self.state != self.State.ERROR_NO_COMMUNICATION_FILE:
                    self.state = self.State.ERROR_NO_COMMUNICATION_FILE
                    logger.warning(f"Could not find communication file: {self.rcon_mmap_client.file_path}")
                    logger.info("To create it, please create/load into an Anno 1800 savegame and unpause.")
                    self.failed_connects = 0
                self.rcon_mmap_client.file_path = None
                return
            else:
                logger.info(f"Found communication file at {self.rcon_mmap_client.file_path}.")

        if not self.rcon_mmap_client.connected:
            self.rcon_mmap_client.connect()

            if not self.rcon_mmap_client.connected:
                if self.state != self.State.ERROR_NO_AUTH_RESPONSE:
                    self.state = self.State.ERROR_NO_AUTH_RESPONSE
                    logger.warning("No response attempting to connect to Anno 1800.")
                    logger.info("To connect, please create/load into an Anno 1800 savegame and unpause.")
                    self.failed_connects = 0
                return
            else:
                logger.info("Successfully authenticated with Anno 1800.")

        # Section to be removed once support for 1.4.x is dropped
        if not self.auth or not self.seed or not self.mod_version or self.mod_version.as_simple_string() == "0.0.0":
            await self.retrieve_auth()

            if not self.auth or not self.seed or not self.mod_version:
                if self.state != self.State.ERROR_NO_INFO_RESPONSE:
                    self.state = self.State.ERROR_NO_INFO_RESPONSE
                    logger.warning("Couldn't retrieve slot name or seed name or mod version.")
                    logger.info("To retrieve, please create/load into an Anno 1800 savegame and unpause.")
                    self.failed_connects = 0
                return

        # Section to be moved to right after mod_path once support for 1.4.x is dropped
        if not (VERSION_COMPATIBILITY[0] <= self.mod_version <= VERSION_COMPATIBILITY[1]):
            if self.state != self.State.ERROR_VERSION_INCOMPATIBLE:
                self.state = self.State.ERROR_VERSION_INCOMPATIBLE
                logger.warning(
                    f"Connected Mod Version {self.mod_version.as_simple_string()} is not compatible with the current client version {A1800World.world_version.as_simple_string()}.")
                logger.warning(
                    f"Current client is only compatible with mod versions {VERSION_COMPATIBILITY[0].as_simple_string()} - {VERSION_COMPATIBILITY[1].as_simple_string()}")
                self.failed_connects = 0
            return

        self.state = self.State.CONNECTED

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(A1800Context, self).server_auth(password_requested)

        if not self.auth:
            await self.get_username()

        await self.send_connect()

    def make_gui(self) -> "type[kvui.GameManager]":
        ui = super().make_gui()
        ui.base_title = f"Archipelago Anno 1800 Client{f" with UT {UT_VERSION}" if tracker_loaded else ""} - AP Version"
        return ui


async def a1800_game_watcher(ctx: A1800Context):
    next_sync = time.perf_counter() + 1
    next_connect = time.perf_counter()
    try:
        while not ctx.exit_event.is_set():
            await asyncio.sleep(0.1)

            if ctx.state != ctx.State.CONNECTED and time.perf_counter() > next_connect:
                if ctx.state == ctx.State.INIT:
                    logger.info("Attempting to connect to Anno 1800...")
                if ctx.state in [ctx.State.ERROR_SERVER_TIMEOUT, ctx.State.ERROR_AUTH_MISMATCH]:
                    logger.warning("Lost connection to Anno 1800. Attempting to reconnect...")

                await ctx.connect_to_game()

                if ctx.state != ctx.State.CONNECTED:
                    ctx.failed_connects += 1
                    if ctx.failed_connects == 1:
                        logger.info("Connection attempt failed. Retrying every 5s...")
                    elif (ctx.failed_connects % 10) == 0:
                        logger.info(
                            f"Still failing to connect ({ctx.failed_connects} total attempts). Retrying every 5s...")
                    next_connect = time.perf_counter() + 5
                else:
                    ctx.failed_connects = 0
                    logger.info(f"Successfully connected to Anno 1800.")

            if ctx.state == ctx.State.CONNECTED and time.perf_counter() > next_sync:
                next_sync = time.perf_counter() + 1
                data = None
                try:
                    data = json.loads(ctx.rcon_mmap_client.send_command("/ap-sync") or "{}")
                except RCONTimeout:
                    logger.warning(
                        "Anno 1800 Client has lost connection. Did you open an expedition, pause or quit the game?")
                    ctx.state = ctx.State.ERROR_SERVER_TIMEOUT
                if ctx.state != ctx.State.CONNECTED:
                    pass  # lost connection, wait for new attempt
                elif not data or "slot_name" not in data or "seed_name" not in data or "mod_version" not in data:
                    logger.warning("No/missing data received for /ap-sync. Something went very wrong!")
                    ctx.state = ctx.State.ERROR_NO_DATA
                    next_connect = time.perf_counter() + 1
                elif data["slot_name"] != ctx.auth:
                    logger.warning(
                        f"Connected slot {data["slot_name"]} is not the expected one: {ctx.auth}")
                    logger.warning("Prioritizing connected game slot over previous slot.")
                    logger.warning("If you were connected to an Archipelago server already, this will disconnect you.")
                    ctx.state = ctx.State.ERROR_AUTH_MISMATCH
                    ctx.auth = data["slot_name"]
                    ctx.seed_name = None
                    await ctx.disconnect()
                elif data["seed_name"] != ctx.seed:
                    logger.warning(
                        f"Connected seed {data["seed_name"]} is not the expected one: {ctx.seed}")
                    logger.warning("Prioritizing connected game seed over previous seed.")
                    ctx.state = ctx.State.ERROR_AUTH_MISMATCH
                    ctx.seed = data["seed_name"]
                elif tuplize_version(data["mod_version"]) != ctx.mod_version:
                    logger.warning(
                        f"Connected mod version {data["mod_version"]} is not the expected one: {ctx.mod_version.as_simple_string()}")
                    logger.warning("Prioritizing connected game mod version over previous mod version.")
                    ctx.state = ctx.State.ERROR_AUTH_MISMATCH
                    ctx.mod_version = tuplize_version(data["mod_version"])
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
            if ctx.state == ctx.State.CONNECTED:
                while ctx.send_index < len(ctx.items_received):
                    transfer_item: NetworkItem = ctx.items_received[ctx.send_index]
                    item_id = transfer_item.item
                    try:
                        ctx.rcon_mmap_client.send_command(f"/ap-receive-item {item_id} {ctx.send_index}")
                    except RCONTimeout:
                        logger.warning(
                            "Anno 1800 Client has lost connection. Did you open an expedition, pause or quit the game?")
                        ctx.state = ctx.State.ERROR_SERVER_TIMEOUT
                        break
                    ctx.send_index += 1
            await asyncio.sleep(0.1)

    except Exception as e:
        logging.exception(e)
        logging.fatal("Aborted Anno 1800 Server Watcher")
        ctx.exit_event.set()


async def a1800_init(ctx: A1800Context) -> bool:
    while not ctx.a1800_mods_folder_path:
        a1800_mods_folder_path = Path(settings.a1800_mods_folder_path)

        if not a1800_mods_folder_path.exists():
            error_popup = ctx.gui_error(
                "Fatal Error", f"Path {a1800_mods_folder_path} does not exist or could not be accessed.")
            while error_popup and error_popup._is_open:  # type: ignore
                await asyncio.sleep(0.1)
            delattr(settings, "a1800_mods_folder_path")
            continue
        if not a1800_mods_folder_path.is_dir():
            error_popup = ctx.gui_error("Fatal Error", f"Path {a1800_mods_folder_path} is not a folder.")
            while error_popup and error_popup._is_open:  # type: ignore
                await asyncio.sleep(0.1)
            delattr(settings, "a1800_mods_folder_path")
            continue
        a1800_exe_path = a1800_mods_folder_path.parent / "Bin" / "Win64" / "Anno1800.exe"
        if not a1800_exe_path.exists() or not a1800_exe_path.is_file():
            error_popup = ctx.gui_error(
                "Fatal Error", f"Path {a1800_mods_folder_path} is not located in your Anno 1800 installation folder.{"\nDon't use the mods folder in your Documents!" if a1800_mods_folder_path.parent.parent.name == "Documents" else ""}")
            while error_popup and error_popup._is_open:  # type: ignore
                await asyncio.sleep(0.1)
            delattr(settings, "a1800_mods_folder_path")
            continue

        ctx.a1800_mods_folder_path = a1800_mods_folder_path

    logger.info("Ready to connect to the Archipelago server via the Connect button or /connect.")
    return True


async def main(make_context: Callable[[], A1800Context]):
    ctx = make_context()
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="ServerLoop")

    if tracker_loaded:
        ctx.run_generator()
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

    asyncio.run(main(lambda: A1800Context(args.connect, args.password)))

    colorama.deinit()
