from functools import reduce
from typing import TYPE_CHECKING

from ._Enums import DLC


if TYPE_CHECKING:
    from ..Options import A1800Options


class ParsedOptions:
    full_accessibility: bool
    enabled_dlcs: DLC
    enable_docklands_logic: bool
    required_population: dict[str, int]
    required_skyscrapers: dict[str, int]
    required_monuments: set[str]

    def __init__(self, options: "A1800Options"):
        self.full_accessibility = options.accessibility == "full"

        self.enabled_dlcs = DLC.VANILLA
        if options.enabled_dlcs.value:
            self.enabled_dlcs |= reduce(DLC.__or__, (
                dlc for dlc in DLC.__members__.values()
                if (dlc.name or "").replace("_", "-").lower() in options.enabled_dlcs
            ))

        self.enable_docklands_logic = bool(options.enable_docklands_logic)

        self.required_population = {
            name.split("-")[1].title(): int(amount)
            for name, amount in options.required_population.value.items() if int(amount) > 0
        }

        self.required_skyscrapers = {
            f"{name.split('-')[1].title()} Skyscraper: Level {name.split('-')[3]}": int(amount)
            for name, amount in options.required_skyscrapers.value.items() if int(amount) > 0
        }

        self.required_monuments = {
            name.replace("-", " ").title().replace("Worlds", "World's")
            for name in options.required_monuments.value
        }
