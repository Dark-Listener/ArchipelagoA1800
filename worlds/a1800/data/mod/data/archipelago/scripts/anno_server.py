from contextlib import contextmanager
import json
from mmap import mmap
from pathlib import Path
from typing import Any, Dict, Generator

from rcon.rcon_mmap_file_access import MMapAccess
from rcon.rcon_mmap_server import RCONMMapServer
from rcon.rcon_packet import RCONPacket


class AnnoServer(RCONMMapServer):
    def __init__(self, env: Dict[str, Any], file_path: Path, script_path: Path, slot_name: str, seed_name: str) -> None:
        super().__init__(file_path)
        self.env = env
        self.script_path = script_path
        self.slot_name = slot_name
        self.seed_name = seed_name

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
    }

    server.send_message(packet.id, RCONPacket.SERVERDATA_RESPONSE_VALUE, json.dumps(info))


def _handle_ap_sync(server: RCONMMapServer, packet: RCONPacket, _body: str) -> None:
    assert isinstance(server, AnnoServer)

    locations_checked = set()  # type: set[int] # pyright: ignore[reportTypeCommentUsage]

    server.env["console"].startScript(str(server.script_path / "ap_sync.lua"))

    for _, (ap_code, is_unlocked) in server.env["g_location_data_by_guid"].items():
        if is_unlocked:
            locations_checked.add(ap_code)

    data = {
        "slot_name": server.slot_name,
        "seed_name": server.seed_name,
        "locations_checked": list(locations_checked),
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
def open_anno_server(env: Dict[str, Any], file_path: Path, script_path: Path, slot_name: str, seed_name: str) -> Generator[AnnoServer, Any, None]:
    anno_server = AnnoServer(env, file_path, script_path, slot_name, seed_name)
    try:
        yield anno_server
    finally:
        anno_server.close()
