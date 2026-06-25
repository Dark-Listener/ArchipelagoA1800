import sys
from pathlib import Path

mod_path = Path.cwd() / "mods" / "{{ mod_name }}"
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
    from data import g_location_data_by_guid, GUIDS_BY_AP_CODE

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
                               src_path, "{{ slot_name }}", "{{ seed_name }}")

    console.startScript(str(src_path / "polling.lua"))
except Exception as e:
    import traceback
    traceback.print_exc()
