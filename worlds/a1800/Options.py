from dataclasses import dataclass
from Options import OptionCounter, OptionGroup, OptionSet, PerGameCommonOptions, Toggle


class EnabledDLCsOption(OptionSet):
    """
    List of enabled DLCs. Per default, all implemented DLCs are enabled.
    It's recommended to match this list when creating the game.

    Valid keys: 'sunken-treasures', 'botanica', 'the-passage', 'seat-of-power', 'bright-harvest', 'land-of-lions', 'docklands', 'tourist-season', 'the-high-life'
    Enabling docklands is strongly discouraged unless you want the option to skip most of the randomizer.
    """
    display_name = "Enabled DLCs"
    valid_keys = {"sunken-treasures", "botanica", "the-passage", "seat-of-power",
                  "bright-harvest", "land-of-lions", "docklands", "tourist-season", "the-high-life"}
    default = valid_keys - {"docklands"}


class EnableDocklandsLogicOption(Toggle):
    """
    Per default, docklands outputs will not be included in the randomizer logic. Turn this on to include them.
    Leads to short and simple randomizers since docklands can supply pretty much everything before skyscrapers and
    artistas.
    Has no effect unless the Docklands DLC is enabled.
    """
    display_name = "Enable Docklands Logic"


class RequiredPopulationOption(OptionCounter):
    """
    This many citizens of each population must be reached to win the randomizer.
    If a population's required amount is 0, the population will not be required.
    Populations that are not available in the DLCs selected in 'Enabled DLCs' will be ignored.
    Ignore the numbers in front, they are there to make sure this is sorted properly.
    """
    _populations = ["farmers", "workers", "artisans", "engineers", "investors", "jornaleros",
                    "obreros", "explorers", "technicians", "shepherds", "elders", "scholars", "tourists"]
    _default_required_population = {
        f"{idx:02}-{population}": 5000 if population == "investors" else 1500 if population == "obreros" else
        750 if population == "technicians" else 7000 if population == "scholars" else
        4000 if population == "tourists" else 0 for idx, population in enumerate(_populations)
    }

    display_name = "Required Population Amounts"
    valid_keys = _default_required_population.keys()
    default = _default_required_population
    min = 0


class RequiredSkyscrapersOption(OptionCounter):
    """
    This many buildings of each skyscraper type must be built to win the randomizer.
    If a building's required amount is 0, the building will not be required.
    Has no effect unless The High Life DLC is enabled.
    Ignore the numbers in front, they are there to make sure this is sorted properly.
    """
    _skyscrapers = ["engineer-level-1", "engineer-level-2", "engineer-level-3", "investor-level-1",
                    "investor-level-2", "investor-level-3", "investor-level-4", "investor-level-5"]
    _default_required_skyscrapers = {
        f"{idx:02}-{skyscraper}":
        15 if skyscraper == "investor-level-5" else 0
        for idx, skyscraper in enumerate(_skyscrapers)
    }

    display_name = "Required Skyscrapers"
    valid_keys = _default_required_skyscrapers.keys()
    default = _default_required_skyscrapers
    min = 0


class RequiredMonumentsOption(OptionSet):
    """
    Each of the monuments in this list must be built to win the randomizer.
    Monuments that are not available in the DLCs selected in 'Enabled DLCs' will be ignored.

    Valid keys: 'worlds-fair', 'research-institute', 'arctic-airship-hangar', 'the-iron-tower', 'skyline-tower'
    """
    display_name = "Required Monuments"
    valid_keys = ["worlds-fair", "research-institute", "arctic-airship-hangar", "the-iron-tower", "skyline-tower"]
    default = []


@dataclass
class A1800Options(PerGameCommonOptions):
    # Game Options (=> ungrouped)
    enabled_dlcs: EnabledDLCsOption
    enable_docklands_logic: EnableDocklandsLogicOption

    # Victory Conditions
    required_population: RequiredPopulationOption
    required_skyscrapers: RequiredSkyscrapersOption
    required_monuments: RequiredMonumentsOption


a1800_option_groups: list[OptionGroup] = [
    OptionGroup("Victory Conditions", [
        RequiredPopulationOption,
        RequiredSkyscrapersOption,
        RequiredMonumentsOption,
    ]),
]
