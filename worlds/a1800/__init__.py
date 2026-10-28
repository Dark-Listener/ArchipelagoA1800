from typing import Any, ClassVar, Optional, cast
from typing_extensions import override

from BaseClasses import Item, MultiWorld, Tutorial
from Options import Option
from worlds.AutoWorld import CollectionState, World, WebWorld
from worlds.LauncherComponents import Component, components, Type, icon_paths
from worlds.LauncherComponents import launch as launch_component  # pyright: ignore[reportUnknownVariableType]

from .data import A1800Data, ITEM_NAME_GROUPS, ITEM_NAME_TO_AP_CODE, LOCATION_NAME_GROUPS, LOCATION_NAME_TO_AP_CODE, START_REGION
from .Items import create_item, Items
from .Locations import Locations
from .Mod import generate_mod
from .Options import a1800_option_groups, a1800_option_presets, A1800Options
from .Regions import create_regions
from .Rules import set_rules
from .Settings import A1800Settings


def launch_client(*args: str):
    from .Client import launch
    launch_component(launch, name="Anno 1800 Client", args=args)


components.append(Component("Anno 1800 Client", func=launch_client, component_type=Type.CLIENT, icon="a1800"))

icon_paths["a1800"] = f"ap:{__name__}/icons/a1800.png"


class A1800Web(WebWorld):
    bug_report_page = "https://https://github.com/Dark-Listener/ArchipelagoA1800/issues"
    option_groups = a1800_option_groups
    options_presets = a1800_option_presets
    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up the Archipelago Anno 1800 randomizer on your computer.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Dark Listener"]
    )
    theme = "ocean"
    tutorials = [setup_en]


class A1800World(World):
    """
    Anno 1800 is a city-building real-time strategy game developed by Ubisoft Blue Byte as part of the Anno series.
    Lead the industrial revolution of the 19th century as you settle islands in Europe, South America and more to
    create teeming metropolises!
    """

    game = "Anno 1800"
    item_name_groups = ITEM_NAME_GROUPS
    item_name_to_id = ITEM_NAME_TO_AP_CODE
    location_name_groups = LOCATION_NAME_GROUPS
    location_name_to_id = LOCATION_NAME_TO_AP_CODE
    options_dataclass = A1800Options
    options: A1800Options
    origin_region_name = START_REGION.full_name
    topology_present = True
    web = A1800Web()
    settings: ClassVar[A1800Settings]
    ut_can_gen_without_yaml = True
    tracker_world: ClassVar[dict[str, Any]] = {
        "map_page_folder": "tracker",
        "map_page_maps": "maps/maps.json",
        "map_page_locations": "locations/locations.json",
        "map_page_groups": [('Main', ['main'])],
    }

    def __init__(self, multiworld: MultiWorld, player: int) -> None:
        super().__init__(multiworld, player)

    @override
    def generate_early(self) -> None:
        # UT regen: restore options from original generation's slot_data
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if re_gen_passthrough and isinstance(re_gen_passthrough, dict) and self.game in re_gen_passthrough:
            # Get the passed through slot data from the real generation
            slot_data: dict[str, Any] = cast(dict[Any, Any], re_gen_passthrough)[self.game]

            slot_options: dict[str, Any] = slot_data.get("options", {})
            # Set all your options here instead of getting them from the yaml
            for key, value in slot_options.items():
                opt: Optional[Option[Any]] = getattr(self.options, key, None)
                if opt is not None:
                    # You can also set .value directly but that won't work if you have OptionSets
                    setattr(self.options, key, opt.from_any(value))

        self.A1800_DATA = A1800Data(self.options)
        self.LOCATIONS = Locations(self)
        self.ITEMS = Items(self)
        self.ITEMS.create_and_push_start_items(self)

    @override
    def create_regions(self) -> None:
        create_regions(self)

    @override
    def create_items(self) -> None:
        self.multiworld.itempool += self.ITEMS.create_itempool(self)

    @override
    def create_item(self, name: str) -> Item:
        return create_item(self, name)

    @override
    def set_rules(self) -> None:
        set_rules(self)

    @override
    def generate_output(self, output_directory: str) -> None:
        generate_mod(self, output_directory)

    @override
    def fill_slot_data(self) -> dict[str, object]:
        slot_data: dict[str, object] = {
            "options": self.options.as_dict(
                "enabled_dlcs",
                "enable_docklands_logic",
                "enforce_cape_trelawney",
                "enable_progressive_unlocks",
                "start_with_flagship",
                "start_with_trading_post",
                "required_street_for_settling",
                "allow_hacienda_residences_upon_unlock",
                "incident_difficulty",
                "required_population",
                "required_skyscrapers",
                "required_monuments",
                "enable_mine_slot_unification"
            ),
            "world_version": self.world_version.as_simple_string(),
        }

        return slot_data

    @override
    def collect(self, state: CollectionState, item: Item) -> bool:
        return super().collect(state, item)

    @override
    def remove(self, state: CollectionState, item: Item) -> bool:
        return super().remove(state, item)

    @staticmethod
    def interpret_slot_data(slot_data: dict[str, Any]) -> dict[str, Any]:
        # Trigger a regen in UT
        return slot_data
