from dataclasses import dataclass
from itertools import groupby
from worlds.AutoWorld import PerGameCommonOptions
from Options import OptionCounter, OptionGroup
from .data import ANNO_DATA

_grouped_required_population = groupby(sorted(ANNO_DATA.get_populations(), key=lambda population: (
    population.region.value, -population.guid)), key=lambda population: population.region)
_default_required_population_amount = {
    f"{region_idx}-{region.full_name.replace(' ', '_').lower()}"
    f"-{population_idx:02}-{population.name.replace(' ', '_').lower()}":
    5000 if population.name == "Investors" else 2000 if population.name == "Obreros" else 0
    for region_idx, (region, populations) in enumerate(_grouped_required_population)
    for population_idx, population in enumerate(populations)
}


class RequiredPopulationAmount(OptionCounter):
    """
    This many citizens of each population are required to win the randomizer.
    If a population's required amount is 0, the population will not be required.
    Ignore the numbers before the world and population, they are there to make sure this is sorted properly.
    """
    valid_keys = _default_required_population_amount.keys()

    min = 0

    default = _default_required_population_amount


@dataclass
class A1800Options(PerGameCommonOptions):
    # Victory Conditions
    required_population_amount: RequiredPopulationAmount


a1800_option_groups: list[OptionGroup] = [
    OptionGroup("Victory Conditions", [
        RequiredPopulationAmount,
        RequiredPopulationAmount
    ]),
]
