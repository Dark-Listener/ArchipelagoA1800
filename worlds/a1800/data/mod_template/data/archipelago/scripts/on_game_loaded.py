import json
import re
import sys
from pathlib import Path

mods_path = Path.cwd() / "mods"

mod_regex = re.compile(r"AP-(\d*)-P(\d*)-(.*)-.*")
mod_path = Path()
for mod in mods_path.iterdir():
    if mod.name.startswith("-"):
        continue
    modinfo_path = (mod / "modinfo.json")
    if modinfo_path.exists() and modinfo_path.is_file():
        data = {}
        with modinfo_path.open("r", encoding="utf-8") as modinfo_file:
            data = json.load(modinfo_file)
        if data and "ModID" in data and mod_regex.search(data["ModID"]):
            mod_path = mod

src_path = mod_path / "data" / "archipelago" / "scripts"

if not src_path in sys.path:
    sys.path.append(str(src_path))

try:
    from importlib import reload
    import anno_server
    import data
    reload(anno_server)
    reload(data)

    from anno_server import AnnoServer
    from data import g_location_data_by_guid, g_settled_region_by_guid, g_fixed_hints, GUIDS_BY_AP_CODE

    g_victory = False
    g_lua_init = False
    g_receive_index = 0

    console.startScript(str(src_path / "data.lua"))
    console.startScript(str(src_path / "on_game_loaded.lua"))

    try:
        g_anno_server.close()
    except NameError:
        pass

    g_anno_server = AnnoServer(globals(), mod_path / "A1800APCommunication.dat",
                               src_path, "{{ slot_name }}", "{{ seed_name }}", "{{ mod_version }}")

    console.startScript(str(src_path / "polling.lua"))
except Exception as e:
    import traceback
    traceback.print_exc()
