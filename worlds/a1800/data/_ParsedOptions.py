from enum import Enum
from functools import reduce
from typing import TYPE_CHECKING

from ._Enums import DLC, NO_REGION, Region


if TYPE_CHECKING:
    from ..Options import A1800Options


class ParsedOptions:
    full_accessibility: bool
    enabled_dlcs: DLC
    enable_docklands_logic: bool
    required_population: dict[str, int]
    required_skyscrapers: dict[str, int]
    required_monuments: set[tuple[str, Region]]

    class IncidentDifficulty(Enum):
        EASY = 0
        NORMAL = 1
        CHALLENGING = 2
        BRUTAL = 3

    class FreeGoodsAndShips(Enum):
        MINIMAL = 0
        IN_LOGIC = 1
        IN_LOGIC_GENEROUS = 2
        VANILLA = 3
        GENEROUS = 4

    def __init__(self, options: "A1800Options"):
        ### Game Options ###
        self.full_accessibility = options.accessibility == "full"

        self.enabled_dlcs = DLC.VANILLA
        if options.enabled_dlcs.value:
            self.enabled_dlcs |= reduce(DLC.__or__, (
                dlc for dlc in DLC.__members__.values()
                if (dlc.name or "").replace("_", "-").lower() in options.enabled_dlcs
            ))

        self.enable_docklands_logic = bool(options.enable_docklands_logic)

        self.exclude_recipe_unlocks = bool(options.exclude_recipe_unlocks)

        self.start_with_flagship = bool(options.start_with_flagship)
        self.start_with_trading_post = bool(options.start_with_trading_post)

        self.paved_street_for_settling = options.required_street_for_settling.value & 1
        self.hacienda_street_for_settling = options.required_street_for_settling.value & 2

        self.allow_hacienda_residences_upon_unlock = bool(options.allow_hacienda_residences_upon_unlock)

        self.incident_difficulty = ParsedOptions.IncidentDifficulty(int(options.incident_difficulty.value))

        self.free_goods_and_ships = ParsedOptions.FreeGoodsAndShips(int(options.free_goods_and_ships.value))

        ### Victory Conditions ###
        self.required_population = {
            name.split("-")[1].title(): int(amount)
            for name, amount in options.required_population.value.items() if int(amount) > 0
        }

        self.required_skyscrapers = {
            name.split('-', 1)[1].replace("-", " ").title() if "skyline-tower" in name else
            f"{name.split('-')[1].title()} Skyscraper: Level {name.split('-')[3]}": 1 if "skyline-tower" in name else int(amount)
            for name, amount in options.required_skyscrapers.value.items() if int(amount) > 0
        }

        self.required_monuments = set()
        for name in options.required_monuments.value:
            proper_name = name.replace("-", " ").title().replace("Worlds", "World's")
            if proper_name.startswith("Ow "):
                region = Region.OW
            elif proper_name.startswith("Nw "):
                region = Region.NW
            elif proper_name.startswith("Ar "):
                region = Region.AR
            elif proper_name.startswith("En "):
                region = Region.EN
            else:
                region = NO_REGION
                proper_name = "   " + proper_name
            proper_name = proper_name[3:]
            self.required_monuments.add((proper_name, region))

        ### Mod Support ###
        self.enable_mine_slot_unification = bool(options.enable_mine_slot_unification)
