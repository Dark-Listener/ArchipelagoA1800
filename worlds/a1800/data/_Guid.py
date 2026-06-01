_GUID_RANGE_START = 1701000000  # Start of Anno 1800 Archipelago Randomizer GUID range

_g_next_anno_guid = _GUID_RANGE_START - 1  # Offset -1 as 1 will be added before returning


def get_next_anno_guid() -> int:
    global _g_next_anno_guid
    _g_next_anno_guid += 1
    return _g_next_anno_guid


RECIPE_GUIDS = {
    "Recipe: Archduke's Schnitzel": (get_next_anno_guid(), 133864, 0, 0, False),
    "Recipe: Stroggof Goulash": (get_next_anno_guid(), 133867, 0, 0, False),
    "Recipe: Fish and Frites": (get_next_anno_guid(), 133868, 0, 0, False),
    "Recipe: Venison en Croute": (get_next_anno_guid(), 133869, 0, 0, False),
    "Recipe: Lobster Cheminee": (get_next_anno_guid(), 133870, 0, 0, False),
    "Recipe: Donut Fourre": (get_next_anno_guid(), 133865, 0, 0, False),
    "Recipe: Eclair": (get_next_anno_guid(), 134241, 0, 0, False),
    "Recipe: Palmier Biscuit": (get_next_anno_guid(), 134240, 0, 0, False),
    "Recipe: Venison Tartare": (get_next_anno_guid(), 133872, 0, 0, False),
    "Recipe: Banana Surprise": (get_next_anno_guid(), 133873, 0, 0, False),
    "Recipe: Daiquiri Tropic": (get_next_anno_guid(), 133866, 0, 0, False),
    "Recipe: Black Muscovy": (get_next_anno_guid(), 133874, 133369, 135036, False),
    "Recipe: Montmartre '75'": (get_next_anno_guid(), 133875, 0, 0, False),
    "Recipe: Glogg": (get_next_anno_guid(), 133876, 133371, 135038, False),
    "Recipe: Enbesa Sunrise": (get_next_anno_guid(), 133877, 0, 0, False),
    "Recipe: Brioche Royale": (get_next_anno_guid(), 134908, 133377, 135045, False),
    "Recipe: Trifle Tower": (get_next_anno_guid(), 134243, 0, 0, False),
    "Recipe: Lady Marmelade": (get_next_anno_guid(), 134244, 133379, 135043, False),
    "Recipe: Age of Exploration": (get_next_anno_guid(), 134981, 133380, 135046, False),
    "Recipe: Homard Lit de Terroir": (get_next_anno_guid(), 134985, 133381, 135047, False),
    "Recipe: Toasters": (get_next_anno_guid(), 135732, 0, 0, False),
    "Recipe: Vacuum Cleaners": (get_next_anno_guid(), 135734, 0, 0, False),
    "Recipe: Crockery": (get_next_anno_guid(), 135733, 0, 0, False),
    "Recipe: Refrigerators": (get_next_anno_guid(), 135735, 0, 0, False),
    "Recipe: Briefcases": (get_next_anno_guid(), 135737, 0, 0, False),
    "Recipe: Banker's Lamps": (get_next_anno_guid(), 135738, 0, 0, False),
    "Recipe: Vanity Screens": (get_next_anno_guid(), 135739, 0, 0, False),
    "Recipe: Writing Desks": (get_next_anno_guid(), 135740, 0, 0, False),
    "Recipe: Four-Poster Beds": (get_next_anno_guid(), 135741, 0, 0, True),
    "Recipe: Lounge Seating": (get_next_anno_guid(), 135742, 0, 0, False),
    "Recipe: Toothpaste": (get_next_anno_guid(), 135743, 0, 0, False),
    "Recipe: Detergent": (get_next_anno_guid(), 135744, 0, 0, False),
    "Recipe: Lipstick": (get_next_anno_guid(), 135745, 0, 0, False),
    "Recipe: Face Cream": (get_next_anno_guid(), 135746, 0, 0, False),
    "Recipe: Pomade": (get_next_anno_guid(), 135747, 0, 0, False),
}
