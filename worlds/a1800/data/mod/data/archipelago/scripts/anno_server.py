from contextlib import contextmanager
import json
from mmap import mmap
from pathlib import Path
from typing import Any, Dict, Generator

from rcon.rcon_mmap_file_access import MMapAccess
from rcon.rcon_mmap_server import RCONMMapServer
from rcon.rcon_packet import RCONPacket


class AnnoServer(RCONMMapServer):
    def __init__(self, env: Dict[str, Any], file_path: Path, script_path: Path, slot_name: str, seed_name: str, mod_version: str) -> None:
        super().__init__(file_path)
        self.env = env
        self.script_path = script_path
        self.slot_name = slot_name
        self.seed_name = seed_name
        self.mod_version = mod_version

        self._ap_receive_item_args_file_path = self.script_path / "ap_receive_item_args.lua"
        self._ap_receive_item_args_file_obj = self._ap_receive_item_args_file_path.open(mode="rb+")

        self.ap_receive_item_args_file_access = MMapAccess(
            mmap(self._ap_receive_item_args_file_obj.fileno(), length=0))

        self.register_handler("/ap-rcon-info", _handle_ap_rcon_info)
        self.register_handler("/ap-sync", _handle_ap_sync)
        self.register_handler("/ap-receive-item", _handle_ap_receive_item)

        self.env["console"].startScript(str(self.script_path / "ap_sync.lua"))

    def close(self):
        if not self.ap_receive_item_args_file_access.closed:
            self.ap_receive_item_args_file_access.close()

        if not self._ap_receive_item_args_file_obj.closed:
            self._ap_receive_item_args_file_obj.close()

        super().close()


def _handle_ap_rcon_info(server: RCONMMapServer, packet: RCONPacket, _body: str) -> None:
    assert isinstance(server, AnnoServer)

    info = {
        "slot_name": server.slot_name,
        "seed_name": server.seed_name,
        "mod_version": server.mod_version,
    }

    server.send_message(packet.id, RCONPacket.SERVERDATA_RESPONSE_VALUE, json.dumps(info))


def _handle_ap_sync(server: RCONMMapServer, packet: RCONPacket, _body: str) -> None:
    assert isinstance(server, AnnoServer)

    settled_regions = 0
    for (region, is_settled) in server.env["g_settled_region_by_guid"].values():
        if is_settled:
            settled_regions |= region

    locations_checked = set()  # type: set[int] # pyright: ignore[reportTypeCommentUsage]
    hints_found = set()  # type: set[tuple[int, int]] # pyright: ignore[reportTypeCommentUsage]

    hints_found |= {
        hint for hint, hint_region in server.env["g_fixed_hints"] if hint_region & settled_regions
    }

    server.env["console"].startScript(str(server.script_path / "ap_sync.lua"))

    for (ap_code, hints, is_unlocked) in server.env["g_location_data_by_guid"].values():
        if is_unlocked:
            locations_checked.add(ap_code)
            hints_found |= {hint for hint, hint_region in hints if hint_region & settled_regions}

    data = {
        "slot_name": server.slot_name,
        "seed_name": server.seed_name,
        "mod_version": server.mod_version,
        "locations_checked": list(locations_checked),
        "hints_found": list(hints_found),
        "victory": server.env["g_victory"],
    }  # type: dict[str, Any] # pyright: ignore[reportTypeCommentUsage]

    server.send_message(packet.id, RCONPacket.SERVERDATA_RESPONSE_VALUE, json.dumps(data))


def _handle_ap_receive_item(server: RCONMMapServer, _packet: RCONPacket, body: str) -> None:
    assert isinstance(server, AnnoServer)

    args = body.split()
    ap_code = int(args[0])
    rcv_idx = int(args[1])
    if ap_code in server.env["GUIDS_BY_AP_CODE"] and rcv_idx >= server.env["g_receive_index"]:
        server.ap_receive_item_args_file_access.set_str(
            0,
            server.ap_receive_item_args_file_access.size,
            "g_ap_receive_item_args = {{\n    [\"ap_code\"] = {:010},\n    [\"rcv_idx\"] = {:010},\n}}\n".format(
                ap_code, rcv_idx
            )
        )
        server.ap_receive_item_args_file_access.flush()
        server.env["console"].startScript(str(server.script_path / "ap_receive_item.lua"))


@contextmanager
def open_anno_server(env: Dict[str, Any], file_path: Path, script_path: Path, slot_name: str, seed_name: str, mod_version: str) -> Generator[AnnoServer, Any, None]:
    anno_server = AnnoServer(env, file_path, script_path, slot_name, seed_name, mod_version)
    try:
        yield anno_server
    finally:
        anno_server.close()
