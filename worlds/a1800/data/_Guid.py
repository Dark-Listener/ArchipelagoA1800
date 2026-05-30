_GUID_RANGE_START = 1701000000  # Start of Anno 1800 Archipelago Randomizer GUID range

_g_next_anno_guid = _GUID_RANGE_START - 1  # Offset -1 as 1 will be added before returning


def get_next_anno_guid() -> int:
    global _g_next_anno_guid
    _g_next_anno_guid += 1
    return _g_next_anno_guid


RECIPE_GUIDS = {
    "Recipe: Archduke's Schnitzel": (get_next_anno_guid(), 133864, 0, 0),
    "Recipe: Stroggof Goulash": (get_next_anno_guid(), 133867, 0, 0),
    "Recipe: Fish and Frites": (get_next_anno_guid(), 133868, 0, 0),
    "Recipe: Venison en Croute": (get_next_anno_guid(), 133869, 0, 0),
    "Recipe: Lobster Cheminee": (get_next_anno_guid(), 133870, 0, 0),
    "Recipe: Donut Fourre": (get_next_anno_guid(), 133865, 0, 0),
    "Recipe: Eclair": (get_next_anno_guid(), 134241, 0, 0),
    "Recipe: Palmier Biscuit": (get_next_anno_guid(), 134240, 0, 0),
    "Recipe: Venison Tartare": (get_next_anno_guid(), 133872, 0, 0),
    "Recipe: Banana Surprise": (get_next_anno_guid(), 133873, 0, 0),
    "Recipe: Daiquiri Tropic": (get_next_anno_guid(), 133866, 0, 0),
    "Recipe: Black Muscovy": (get_next_anno_guid(), 133874, 133369, 135036),
    "Recipe: Montmartre '75'": (get_next_anno_guid(), 133875, 0, 0),
    "Recipe: Glogg": (get_next_anno_guid(), 133876, 133371, 135038),
    "Recipe: Enbesa Sunrise": (get_next_anno_guid(), 133877, 0, 0),
    "Recipe: Brioche Royale": (get_next_anno_guid(), 134908, 133377, 135045),
    "Recipe: Trifle Tower": (get_next_anno_guid(), 134243, 0, 0),
    "Recipe: Lady Marmelade": (get_next_anno_guid(), 134244, 133379, 135043),
    "Recipe: Age of Exploration": (get_next_anno_guid(), 134981, 133380, 135046),
    "Recipe: Homard Lit de Terroir": (get_next_anno_guid(), 134985, 133381, 135047),
    "Recipe: Toasters": (get_next_anno_guid(), 135104, 0, 0),
    "Recipe: Vacuum Cleaners": (get_next_anno_guid(), 135204, 0, 0),
    "Recipe: Crockery": (get_next_anno_guid(), 135203, 0, 0),
    "Recipe: Refrigerators": (get_next_anno_guid(), 135205, 0, 0),
    "Recipe: Briefcases": (get_next_anno_guid(), 135206, 0, 0),
    "Recipe: Banker's Lamps": (get_next_anno_guid(), 135106, 0, 0),
    "Recipe: Vanity Screens": (get_next_anno_guid(), 135124, 0, 0),
    "Recipe: Writing Desks": (get_next_anno_guid(), 135125, 0, 0),
    "Recipe: Four-Poster Beds": (get_next_anno_guid(), 135126, 0, 0),
    "Recipe: Lounge Seating": (get_next_anno_guid(), 135127, 0, 0),
    "Recipe: Toothpaste": (get_next_anno_guid(), 134633, 0, 0),
    "Recipe: Detergent": (get_next_anno_guid(), 135207, 0, 0),
    "Recipe: Lipstick": (get_next_anno_guid(), 135208, 0, 0),
    "Recipe: Face Cream": (get_next_anno_guid(), 135888, 0, 0),
    "Recipe: Pomade": (get_next_anno_guid(), 135210, 0, 0),
}
