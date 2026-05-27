_GUID_RANGE_START = 1701000000  # Start of Anno 1800 Archipelago Randomizer GUID range

_g_next_anno_guid = _GUID_RANGE_START - 1  # Offset -1 as 1 will be added before returning


def get_next_anno_guid() -> int:
    global _g_next_anno_guid
    _g_next_anno_guid += 1
    return _g_next_anno_guid
