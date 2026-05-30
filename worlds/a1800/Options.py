from dataclasses import dataclass
from itertools import groupby
from Options import OptionCounter, OptionGroup, OptionSet, PerGameCommonOptions, Toggle
from .data._Products import _a1800_populations  # pyright: ignore[reportPrivateUsage]
from .data import DLC


_valid_dlcs = [dlc.name for dlc in sorted(
    (dlc for dlc in DLC.__members__.values() if not dlc in DLC.VANILLA | DLC.EMPIRE_OF_THE_SKIES), key=lambda dlc: dlc.value)]
_default_enabled_dlcs = [dlc.name for dlc in sorted(
    (dlc for dlc in DLC.__members__.values() if not dlc in DLC.DOCKLANDS and dlc.name in _valid_dlcs), key=lambda dlc: dlc.value)]


class EnabledDLCsOption(OptionSet):
    """
    List of enabled DLCs. Per default, all implemented DLCs are enabled.
    It's recommended to match this list when creating the game.
    Duplicates will be ignored.
    Valid keys: SUNKEN_TREASURES, BOTANICA, THE_PASSAGE, SEAT_OF_POWER, BRIGHT_HARVEST, LAND_OF_LIONS,
    DOCKLANDS, TOURIST_SEASON, THE_HIGH_LIFE
    Enabling docklands is strongly discouraged unless you want the option to skip most of the randomizer.
    """
    display_name = "Enabled DLCs"
    valid_keys = _valid_dlcs
    default = _default_enabled_dlcs


_grouped_required_population = groupby(sorted(_a1800_populations, key=lambda population: (
    population.region.value, -population.guid)), key=lambda population: population.region)
_default_required_population_amount = {
    f"{region_idx}-{region.full_name.replace(' ', '_').lower()}"
    f"-{population_idx:02}-{population.name.replace(' ', '_').lower()}":
    5000 if population.name == "Investors" else 1500 if population.name == "Obreros" else
    750 if population.name == "Technicians" else 7000 if population.name == "Scholars" else
    4000 if population.name == "Tourists" else 0
    for region_idx, (region, populations) in enumerate(_grouped_required_population)
    for population_idx, population in enumerate(populations)
}


class EnableDocklandsLogicOption(Toggle):
    """
    Per default, docklands outputs will not be included in the randomizer logic. Turn this on to include them.
    Leads to short and simple randomizers since docklands can supply pretty much everything before skyscrapers and
    artistas.
    Has no effect unless the Docklands DLC is enabled.
    """
    display_name = "Enable Docklands Logic"


class RequiredPopulationAmountsOption(OptionCounter):
    """
    This many citizens of each population are required to win the randomizer.
    If a population's required amount is 0, the population will not be required.
    Populations that are not available in the DLCs selected in 'Enabled DLCs' will be ignored.
    Ignore the numbers before the world and population, they are there to make sure this is sorted properly.
    """
    display_name = "Required Population Amounts"
    valid_keys = _default_required_population_amount.keys()
    default = _default_required_population_amount
    min = 0


@dataclass
class A1800Options(PerGameCommonOptions):
    # Game Options (=> ungrouped)
    enabled_dlcs: EnabledDLCsOption
    enable_docklands_logic: EnableDocklandsLogicOption

    # Victory Conditions
    required_population_amounts: RequiredPopulationAmountsOption


a1800_option_groups: list[OptionGroup] = [
    OptionGroup("Victory Conditions", [
        RequiredPopulationAmountsOption,
    ]),
]
