from dataclasses import dataclass
from Options import Choice, OptionCounter, OptionGroup, OptionSet, PerGameCommonOptions, Toggle

################
# Game Options #
################


class EnabledDLCsOption(OptionSet):
    """
    List of enabled DLCs. Per default, all DLCs except for docklands are enabled.
    It's recommended to match this list when creating the game.

    Valid keys: 'sunken-treasures', 'botanica', 'the-passage', 'seat-of-power', 'bright-harvest', 'land-of-lions',
    'docklands', 'tourist-season', 'the-high-life', 'seeds-of-change', 'empire-of-the-skies', 'new-world-rising'

    Enabling docklands is strongly discouraged unless you want the option to skip most of the randomizer.
    """
    display_name = "Enabled DLCs"
    valid_keys = {"sunken-treasures", "botanica", "the-passage", "seat-of-power",
                  "bright-harvest", "land-of-lions", "docklands", "tourist-season",
                  "the-high-life", "seeds-of-change", 'empire-of-the-skies', 'new-world-rising'}
    default = valid_keys - {"docklands"}


class EnableDocklandsLogicOption(Toggle):
    """
    Per default, docklands outputs will not be included in the randomizer logic. Turn this on to include them.
    Leads to short and simple randomizers since docklands can supply pretty much everything before skyscrapers and
    artistas.
    Has no effect unless the Docklands DLC is enabled.
    """
    display_name = "Enable Docklands Logic"


class EnableStartWithFlagshipOption(Toggle):
    """
    Per default, the starting flagship will not be included in the randomizer logic. If you intend to start with a
    flagship (or even a fleet), turn this on to tell the randomizer you have a decent expedition ship from the start.
    """
    display_name = "Enable Start with Flagship"


class RequiredStreetForSettlingOption(Choice):
    """
    Sets which level of street must be availablee for the randomizer to assume ability to settle. Only affects the
    New World.

    Basic: The dirt road must be available.

    Upgraded: The dirt road or the paved street must be available. Often requires shipping many bricks to the New World.

    Hacienda: The dirt road or any of the two hacienda streets must be available. Hacienda streets are limited to 999
    squares, which makes settling very restrictive and likely makes settling multiple islands required. Same as Basic
    unless the Seeds of Change DLC is enabled.

    Hacienda and Upgraded: The dirt road, paved street or any of the two hacienda streets must be available. Same as
    Upgraded unless the Seeds of Change DLC is enabled.
    """
    display_name = "Required Street for Settling"
    option_basic = 0
    option_upgraded = 1
    option_hacienda = 2
    option_hacienda_and_upgraded = 3
    default = 0


class AllowHaciendaResidencesUponUnlockOption(Toggle):
    """
    Per default, Hacienda residences must not only be unlocked, but their corresponding regular residence also has to be
    built at least once first. By turning this on, they will be buildable as soon as they are unlocked. This often
    results in skipping most of the New World goods as these residences allow the randomizer to progress without
    fulfilling the needs of the New World populations.
    """
    display_name = "Allow Hacienda Residences upon Unlock"


class IncidentDifficultyOption(Choice):
    """
    Select how challenging incidents (fire, riots, illness) should be. Can be combined indepoendently with the ingame
    setting to adjust difficulty to your liking.

    Easy: Incidents unlock once you have unlocked the responder building and had enough materials to build them in 
    storage at least once. They are guaranteed to be available before upgrading to the tier of population after the
    one they would unlock with in vanilla.

    Normal: Incidents unlock once you have unlocked the responder building. They are guaranteed to be available before
    upgrading to the tier of population after the one they would unlock with in vanilla.

    Challenging: Incidents unlock once you reach the local incident requirement. They are guaranteed to be available
    before upgrading to the tier of population after the one they would unlock with in vanilla.

    Brutal: Incidents unlock once you reach the local incident requirement. There are no guarantees about ever
    unlocking the responder building.
    """
    display_name = "Incident Difficulty"
    option_easy = 0
    option_normal = 1
    option_challenging = 2
    option_brutal = 3
    default = 1

######################
# Victory Conditions #
######################


class RequiredPopulationOption(OptionCounter):
    """
    This many citizens of each population must be reached to win the randomizer.
    If a population's required amount is 0, the population will not be required.
    Populations that are not available in the DLCs selected in 'Enabled DLCs' will be ignored.
    Ignore the numbers in front, they are there to make sure this is sorted properly.

    If you are using the options creator, remove all entries you don't want as it will otherwise save 1 instead of 0.
    """
    _populations = ["farmers", "workers", "artisans", "engineers", "investors", "jornaleros",
                    "obreros", "artistas", "explorers", "technicians", "shepherds", "elders", "scholars", "tourists"]
    _default_required_population = {
        f"{idx:02}-{population}": 5000 if population == "investors" else 1500 if population == "obreros" else
        6000 if population == "artistas" else 750 if population == "technicians" else
        7000 if population == "scholars" else 4000 if population == "tourists" else 0
        for idx, population in enumerate(_populations)
    }

    display_name = "Required Population Amounts"
    valid_keys = _default_required_population.keys()
    default = _default_required_population
    min = 0


class RequiredSkyscrapersOption(OptionCounter):
    """
    This many buildings of each skyscraper type must be built to win the randomizer.
    If a building's required amount is 0, the building will not be required.
    Amounts greater than 1 will be treated as 1 for the Skyline Tower as it is a unique building.
    Has no effect unless The High Life DLC is enabled.
    Ignore the numbers in front, they are there to make sure this is sorted properly.

    If you are using the options creator, remove all entries you don't want as it will otherwise save 1 instead of 0.
    """
    _skyscrapers = ["engineer-level-1", "engineer-level-2", "engineer-level-3", "investor-level-1",
                    "investor-level-2", "investor-level-3", "investor-level-4", "investor-level-5", "skyline-tower"]
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
    Find the Skyline Tower under 'Required Skyscrapers' instead as it is also a residence.

    Valid keys: 'worlds-fair', 'research-institute', 'arctic-airship-hangar', 'the-iron-tower',
    'ow-rigid-airship-hangar', 'nw-rigid-airship-hangar', 'dam', 'grand-stadium'
    """
    display_name = "Required Monuments"
    valid_keys = ["worlds-fair", "research-institute", "arctic-airship-hangar", "the-iron-tower",
                  "ow-rigid-airship-hangar", "nw-rigid-airship-hangar", "dam", "grand-stadium"]
    default = []

###############
# Mod Support #
###############


class EnableMineSlotUnificationOption(Toggle):
    """
    Enables support for the mod 'Mine Slot Unification (Taludas)'.

    Removes the requirement for settling other islands from mines in the Old World.
    """
    display_name = "Enable Mine Slot Unification (Taludas)"


@dataclass
class A1800Options(PerGameCommonOptions):
    # Game Options (=> ungrouped)
    enabled_dlcs: EnabledDLCsOption
    enable_docklands_logic: EnableDocklandsLogicOption
    enable_start_with_flagship: EnableStartWithFlagshipOption
    required_street_for_settling: RequiredStreetForSettlingOption
    allow_hacienda_residences_upon_unlock: AllowHaciendaResidencesUponUnlockOption
    incident_difficulty: IncidentDifficultyOption

    # Victory Conditions
    required_population: RequiredPopulationOption
    required_skyscrapers: RequiredSkyscrapersOption
    required_monuments: RequiredMonumentsOption

    # Mod Support
    enable_mine_slot_unification: EnableMineSlotUnificationOption


a1800_option_groups: list[OptionGroup] = [
    OptionGroup("Victory Conditions", [
        RequiredPopulationOption,
        RequiredSkyscrapersOption,
        RequiredMonumentsOption,
    ]),
    OptionGroup("Mod Support", [
        EnableMineSlotUnificationOption,
    ]),
]
