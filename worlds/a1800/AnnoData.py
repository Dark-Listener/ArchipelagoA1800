from dataclasses import dataclass
from enum import Enum
from itertools import groupby
from typing import Callable, ClassVar, Iterable

from .Options import A1800Options


class ProductType(Enum):
    WORKFORCE = 0
    GOOD = 1
    SERVICE = 2


class DLC(Enum):
    VANILLA = 0


@dataclass
class A1800Object:
    name: str
    dlc: DLC
    region: set[str]


@dataclass
class A1800Region(A1800Object):
    requirements: set[str]


@dataclass
class A1800Product(A1800Object):
    guid: int
    type: ProductType


@dataclass
class A1800Chain(A1800Object):
    guid: int
    elements: set[str]


@dataclass
class A1800Unlock(A1800Object):
    __item_id: ClassVar[int] = 1
    guids: set[int]
    lock_guids: set[int]
    unlock_population: str
    unlock_amount: int

    def __post_init__(self) -> None:
        self.ap_code = A1800Unlock.__item_id
        A1800Unlock.__item_id += 1


@dataclass
class A1800Factory(A1800Unlock):
    cost: set[str]
    maintenance: set[str]
    input: set[str]
    output: set[str]
    unlock_chain: str


@dataclass
class A1800Upgrade(A1800Factory):
    previous_building: str


@dataclass
class A1800Residence(A1800Upgrade):
    consumption: set[str]
    luxury: set[str]
    lifestyle: set[str]


a1800_objects: list[A1800Object] = [
    A1800Object("Sea Travel", DLC.VANILLA, {"OW", "NW", "En", "Ar"}),
    A1800Object("Fire Protection", DLC.VANILLA, {"OW"}),
    A1800Object("Riot Control", DLC.VANILLA, {"OW"}),
    A1800Object("Healthcare", DLC.VANILLA, {"OW"}),
    A1800Object("Victory", DLC.VANILLA, {"OW", "NW", "En", "Ar"}),


    A1800Region("OW", DLC.VANILLA, set(), set()),


    A1800Product("Farmers", DLC.VANILLA, {"OW"}, 15000000, ProductType.WORKFORCE),
    A1800Product("Workers", DLC.VANILLA, {"OW"}, 15000001, ProductType.WORKFORCE),
    A1800Product("Artisans", DLC.VANILLA, {"OW"}, 15000002, ProductType.WORKFORCE),

    A1800Product("Wood", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 120008, ProductType.GOOD),
    A1800Product("Timber", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010196, ProductType.GOOD),
    A1800Product("Fish", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010200, ProductType.GOOD),
    A1800Product("Wool", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010197, ProductType.GOOD),
    A1800Product("Work Clothes", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010237, ProductType.GOOD),
    A1800Product("Potatoes", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010195, ProductType.GOOD),
    A1800Product("Schnapps", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010216, ProductType.GOOD),
    A1800Product("Clay", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010201, ProductType.GOOD),
    A1800Product("Bricks", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010205, ProductType.GOOD),
    A1800Product("Pigs", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010199, ProductType.GOOD),
    A1800Product("Sausages", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010238, ProductType.GOOD),
    A1800Product("Grain", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010192, ProductType.GOOD),
    A1800Product("Flour", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010235, ProductType.GOOD),
    A1800Product("Bread", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010213, ProductType.GOOD),
    A1800Product("Sails", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010210, ProductType.GOOD),
    A1800Product("Coal", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010226, ProductType.GOOD),
    A1800Product("Iron", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010227, ProductType.GOOD),
    A1800Product("Steel", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010219, ProductType.GOOD),
    A1800Product("Steel Beams", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010218, ProductType.GOOD),
    A1800Product("Tallow", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010234, ProductType.GOOD),
    A1800Product("Soap", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010203, ProductType.GOOD),
    A1800Product("Weapons", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010221, ProductType.GOOD),
    A1800Product("Hops", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010194, ProductType.GOOD),
    A1800Product("Malt", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010236, ProductType.GOOD),
    A1800Product("Beer", DLC.VANILLA, {"OW", "NW", "En", "Ar"}, 1010214, ProductType.GOOD),

    A1800Product("Market", DLC.VANILLA, {"OW"}, 120020, ProductType.SERVICE),
    A1800Product("Pub", DLC.VANILLA, {"OW"}, 1010349, ProductType.SERVICE),
    A1800Product("Church", DLC.VANILLA, {"OW"}, 1010350, ProductType.SERVICE),
    A1800Product("School", DLC.VANILLA, {"OW"}, 1010351, ProductType.SERVICE),


    A1800Chain("Timber", DLC.VANILLA, {"OW"}, 500091, {"Lumberjack's Hut", "Sawmill"}),
    A1800Chain("Work Clothes", DLC.VANILLA, {"OW"}, 500505, {"Sheep Farm", "Framework Knitters"}),
    A1800Chain("Schnapps", DLC.VANILLA, {"OW"}, 500002, {"Potato Farm", "Schnapps Distillery"}),
    A1800Chain("Bricks", DLC.VANILLA, {"OW"}, 500024, {"Clay Pit", "Brick Factory"}),
    A1800Chain("Sausages", DLC.VANILLA, {"OW"}, 25000244, {"Pig Farm", "Slaughterhouse"}),
    A1800Chain("Bread", DLC.VANILLA, {"OW"}, 500004, {"Grain Farm", "Flour Mill", "Bakery"}),
    A1800Chain("Sails", DLC.VANILLA, {"OW"}, 500009, {"Sheep Farm", "Sailmakers"}),
    A1800Chain("Steel Beams", DLC.VANILLA, {"OW"}, 500005, {"Charcoal Kiln", "Iron Mine", "Furnace", "Steelworks"}),
    A1800Chain("Soap", DLC.VANILLA, {"OW"}, 25000220, {"Pig Farm", "Rendering Works", "Soap Factory"}),
    A1800Chain("Weapons", DLC.VANILLA, {"OW"}, 500145, {"Charcoal Kiln", "Iron Mine", "Furnace", "Weapon Factory"}),
    A1800Chain("Beer", DLC.VANILLA, {"OW"}, 500006, {"Grain Farm", "Malthouse", "Hop Farm", "Brewery"}),


    A1800Factory("Dirt Road", DLC.VANILLA, {"OW"}, {1000178}, {1000178}, "", 0, set(), set(), set(), set(), ""),

    A1800Factory("Lumberjack's Hut", DLC.VANILLA, {"OW"}, {1010266}, {140029}, "", 0,
                 set(), {"Farmers"}, set(), {"Wood"}, "Timber"),

    A1800Factory("Sawmill", DLC.VANILLA, {"OW"}, {100451}, {140029}, "", 0,
                 set(), {"Farmers"}, {"Wood"}, {"Timber"}, "Timber"),

    A1800Factory("Small Warehouse", DLC.VANILLA, {"OW"}, {1010371}, {130040}, "", 0,
                 {"Timber"}, set(), set(), set(), ""),

    A1800Factory("Small Trading Post", DLC.VANILLA, {"OW"}, {1010517, 1010540}, set(), "", 0,
                 {"Timber"}, set(), set(), set(), ""),

    A1800Factory("Marketplace", DLC.VANILLA, {"OW"}, {1010372}, {130057}, "", 0,
                 {"Timber"}, set(), set(), {"Market"}, ""),

    A1800Factory("Fishery", DLC.VANILLA, {"OW"}, {1010278}, {130056}, "Farmers", 50,
                 {"Timber"}, {"Farmers"}, set(), {"Fish"}, ""),

    A1800Factory("Sheep Farm", DLC.VANILLA, {"OW"}, {1010267}, {130060}, "Farmers", 100,
                 {"Timber"}, {"Farmers"}, set(), {"Wool"}, "Work Clothes"),

    A1800Factory("Framework Knitters", DLC.VANILLA, {"OW"}, {1010315}, {130060}, "Farmers", 100,
                 {"Timber"}, {"Farmers"}, {"Wool"}, {"Work Clothes"}, "Work Clothes"),

    A1800Factory("Potato Farm", DLC.VANILLA, {"OW"}, {1010265}, {140028}, "Farmers", 100,
                 {"Timber"}, {"Farmers"}, set(), {"Potatoes"}, "Schnapps"),

    A1800Factory("Schnapps Distillery", DLC.VANILLA, {"OW"}, {1010294}, {140028}, "Farmers", 100,
                 {"Timber"}, {"Farmers"}, {"Potatoes"}, {"Schnapps"}, "Schnapps"),

    A1800Factory("Fire Station", DLC.VANILLA, {"OW"}, {1010463}, {1010463}, "Farmers", 150,
                 {"Timber"}, set(), set(), {"Fire Protection"}, ""),

    A1800Factory("Pub", DLC.VANILLA, {"OW"}, {1010358}, {130042}, "Farmers", 150,
                 {"Timber"}, set(), set(), {"Pub"}, ""),

    A1800Factory("Clay Pit", DLC.VANILLA, {"OW"}, {100416}, {140031}, "Workers", 1,
                 {"Timber"}, {"Workers"}, set(), {"Clay"}, "Bricks"),

    A1800Factory("Brick Factory", DLC.VANILLA, {"OW"}, {1010283}, {140031}, "Workers", 1,
                 {"Timber"}, {"Workers"}, {"Clay"}, {"Bricks"}, "Bricks"),

    A1800Factory("Pig Farm", DLC.VANILLA, {"OW"}, {1010269}, {140027}, "Workers", 1,
                 {"Timber"}, {"Farmers"}, set(), {"Pigs"}, "Sausages"),

    A1800Factory("Slaughterhouse", DLC.VANILLA, {"OW"}, {1010316}, {140027}, "Workers", 1,
                 {"Timber", "Bricks"}, {"Workers"}, {"Pigs"}, {"Sausages"}, "Sausages"),

    A1800Factory("Trade Union", DLC.VANILLA, {"OW"}, {1010516}, {1010516}, "Workers", 1,
                 {"Timber", "Bricks"}, set(), set(), set(), ""),

    A1800Factory("Grain Farm", DLC.VANILLA, {"OW"}, {1010262}, {140033}, "Workers", 150,
                 {"Timber"}, {"Farmers"}, set(), {"Grain"}, "Bread"),

    A1800Factory("Flour Mill", DLC.VANILLA, {"OW"}, {1010313}, {140033}, "Workers", 150,
                 {"Timber", "Bricks"}, {"Farmers"}, {"Grain"}, {"Flour"}, "Bread"),

    A1800Factory("Bakery", DLC.VANILLA, {"OW"}, {1010291}, {140033}, "Workers", 150,
                 {"Timber", "Bricks"}, {"Workers"}, {"Flour"}, {"Bread"}, "Bread"),

    A1800Factory("Church", DLC.VANILLA, {"OW"}, {1010359}, {130043}, "Workers", 150,
                 {"Timber", "Bricks"}, set(), set(), {"Church"}, ""),

    A1800Factory("Sailmakers", DLC.VANILLA, {"OW"}, {1010288}, {140050}, "Workers", 150,
                 {"Timber", "Bricks"}, {"Workers"}, {"Wool"}, {"Sails"}, "Sails"),

    A1800Factory("Sailing Shipyard", DLC.VANILLA, {"OW"}, {1010520}, {130050}, "Workers", 150,
                 {"Timber", "Bricks"}, {"Workers"}, {"Timber", "Sails"}, {"Sea Travel"}, ""),

    A1800Factory("Mounted Guns", DLC.VANILLA, {"OW"}, {1010522}, {1010522}, "Workers", 150,
                 {"Timber", "Bricks"}, set(), set(), set(), ""),

    A1800Factory("Quay", DLC.VANILLA, {"OW"}, {1010567}, {130121}, "Workers", 150, set(), set(), set(), set(), ""),

    A1800Factory("Depot", DLC.VANILLA, {"OW"}, {1010519}, {130121}, "Workers", 150,
                 {"Timber", "Bricks"}, set(), set(), set(), ""),

    A1800Factory("Harbourmaster's Office", DLC.VANILLA, {"OW"}, {100586}, {100586}, "Workers", 150,
                 {"Timber", "Bricks"}, set(), set(), set(), ""),

    A1800Factory("Charcoal Kiln", DLC.VANILLA, {"OW"}, {1010298}, {140034}, "Workers", 300,
                 {"Timber", "Bricks"}, {"Workers"}, set(), {"Coal"}, "Steel Beams"),

    A1800Factory("Iron Mine", DLC.VANILLA, {"OW"}, {1010305}, {140034}, "Workers", 300,
                 {"Timber", "Bricks"}, {"Workers"}, set(), {"Iron"}, "Steel Beams"),

    A1800Factory("Furnace", DLC.VANILLA, {"OW"}, {1010297}, {140034}, "Workers", 300,
                 {"Timber", "Bricks"}, {"Workers"}, {"Iron", "Coal"}, {"Steel"}, "Steel Beams"),

    A1800Factory("Steelworks", DLC.VANILLA, {"OW"}, {1010296}, {140034}, "Workers", 300,
                 {"Timber", "Bricks"}, {"Workers"}, {"Steel"}, {"Steel Beams"}, "Steel Beams"),

    A1800Factory("Rendering Works", DLC.VANILLA, {"OW"}, {1010312}, {140030}, "Workers", 300,
                 {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Pigs"}, {"Tallow"}, "Soap"),

    A1800Factory("Soap Factory", DLC.VANILLA, {"OW"}, {1010281}, {140030}, "Workers", 300,
                 {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Tallow"}, {"Soap"}, "Soap"),

    A1800Factory("Weapon Factory", DLC.VANILLA, {"OW"}, {1010299}, {140051}, "Workers", 300,
                 {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Steel"}, {"Weapons"}, "Weapons"),

    A1800Factory("Cannon Tower", DLC.VANILLA, {"OW"}, {1010523}, {1010523}, "Workers", 300,
                 {"Timber", "Bricks", "Steel Beams", "Weapons"}, set(), set(), set(), ""),

    A1800Factory("Hop Farm", DLC.VANILLA, {"OW"}, {1010264}, {140035}, "Workers", 500,
                 {"Timber"}, {"Farmers"}, set(), {"Hops"}, "Beer"),

    A1800Factory("Malthouse", DLC.VANILLA, {"OW"}, {1010314}, {140035}, "Workers", 500,
                 {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Grain"}, {"Malt"}, "Beer"),

    A1800Factory("Brewery", DLC.VANILLA, {"OW"}, {1010292}, {140035}, "Workers", 500,
                 {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Malt", "Hops"}, {"Beer"}, "Beer"),

    A1800Factory("Police Station", DLC.VANILLA, {"OW"}, {1010462}, {1010462}, "Workers", 500,
                 {"Timber", "Bricks"}, set(), set(), {"Riot Control"}, ""),

    A1800Factory("School", DLC.VANILLA, {"OW"}, {1010360}, {130044}, "Workers", 750,
                 {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"School"}, ""),


    A1800Upgrade("Paved Street", DLC.VANILLA, {"OW"}, {1010035}, {1010035}, "Workers", 1,
                 {"Bricks"}, set(), set(), set(), "", "Dirt Road"),

    A1800Upgrade("Medium Warehouse", DLC.VANILLA, {"OW"}, {100516}, {130053}, "Workers", 1,
                 {"Timber", "Bricks"}, set(), set(), set(), "", "Small Warehouse"),

    A1800Upgrade("Medium Trading Post", DLC.VANILLA, {"OW"}, {100510, 100514}, {130053}, "Workers", 1,
                 {"Timber", "Bricks"}, set(), set(), set(), "", "Small Trading Post"),


    A1800Residence("Farmer Residence", DLC.VANILLA, {"OW"}, {1010343}, {1010343}, "", 0,
                   {"Timber"}, set(), set(), {"Farmers"}, "", "",
                   {"Market", "Fish", "Work Clothes", "Fire Protection"},
                   {"Schnapps", "Pub"},
                   {"Flour", "Sugar", "Jam", "Local Mail", "Regional Mail",
                       "Overseas Mail", "Soap", "Herbs", "Hibiscus Petals"}),

    A1800Residence("Worker Residence", DLC.VANILLA, {"OW"}, {1010344}, {1010344}, "Farmers", 100,
                   {"Timber"}, set(), set(), {"Workers"}, "", "Farmer Residence",
                   {"Market", "Fish", "Work Clothes", "Sausages", "Bread", "Soap", "School", "Riot Control"},
                   {"Schnapps", "Pub", "Church", "Beer"},
                   {"Rum", "Penny Farthings", "Hot Sauce", "Local Mail", "Regional Mail",
                       "Overseas Mail", "Beef", "Soccer Balls", "Clay Pipes"}),

    A1800Residence("Artisan Residence", DLC.VANILLA, {"OW"}, {1010345}, {1010345}, "Workers", 750,
                   {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"Artisans"}, "", "Worker Residence",
                   {"Sausages", "Bread", "Soap", "School", "Canned Food",
                       "Sewing Machines", "Fur Coats", "University", "Healthcare"},
                   {"Church", "Beer", "Variety Theatre", "Rum"},
                   {"Wool", "Clay", "Paper", "Local Mail", "Regional Mail",
                       "Overseas Mail", "Soccer Balls", "Perfumes", "Scooter"}),
]


Requirement = tuple[str, frozenset[str]]

A1800Rule = Callable[[object, int], bool]


def get_item_name(obj: A1800Object) -> str:
    if not obj.region:
        return obj.name
    prefix = ""
    region_list = [region for region in ["OW", "NW", "En", "Ar"] if region in obj.region]
    for region, _ in zip(region_list[:-1], region_list[1:]):
        prefix += f"{region}, "
    return f"{prefix}{region_list[-1]}: {obj.name}"


def get_requirement_name(requirement: Requirement) -> str:
    obj = next(obj for obj in a1800_objects if obj.name ==
               requirement[0] and requirement[1].issubset(frozenset(obj.region)))
    assert obj
    return get_item_name(obj)


def get_location_name(obj: A1800Object) -> str:
    if isinstance(obj, A1800Unlock):
        unlock = obj
        pop = unlock.unlock_population
        amount = unlock.unlock_amount
        if not pop or not amount:
            return f"Game start ({unlock.name})"

        return f"{amount} {pop if amount != 1 else pop[:-1]} ({get_item_name(unlock)})"
    else:
        return obj.name


def get_region_name(region: A1800Region | str) -> str:
    if isinstance(region, A1800Region):
        name = region.name
    else:
        name = region

    match(name):
        case "OW":
            return "Old World"
        case "NW":
            return "New World"
        case "En":
            return "Enbesa"
        case "Ar":
            return "Arctic"
        case _:
            return "Unknown"


def trigger_key(location: A1800Unlock) -> tuple[int, int]:
    unlock_population_id = next(
        (population.guid for population in a1800_populations if population.name == location.unlock_population), 0)
    return unlock_population_id, location.unlock_amount or 0


def get_event_locations(factory: A1800Factory) -> list[A1800Object]:
    return [
        A1800Object(f"{get_item_name(factory)} => {output}", factory.dlc, factory.region)
        for output in factory.output
    ]


def get_unlock_guids(unlock: A1800Unlock) -> set[int]:
    guids = unlock.guids

    if isinstance(unlock, A1800Factory):
        factory = unlock

        if factory.unlock_chain in a1800_chain_dict:
            guids.add(a1800_chain_dict[factory.unlock_chain].guid)

        for output in factory.output:
            out_product = next((obj for obj in a1800_objects if isinstance(obj, A1800Product) and obj.name ==
                                output and factory.region.issubset(obj.region)), None)
            if out_product:
                guids.add(out_product.guid)

    return guids


def is_progressive(obj: A1800Object) -> bool:
    return bool(next((
                requirement for requirement in a1800_required_items
                if requirement[0] == obj.name and requirement[1].issubset(frozenset(obj.region))), None))


a1800_regions = [region for region in a1800_objects if isinstance(region, A1800Region)]

a1800_region_dict = {region.name: region for region in a1800_regions}

a1800_chains = [chain for chain in a1800_objects if isinstance(chain, A1800Chain)]

a1800_chain_dict = {chain.name: chain for chain in a1800_chains}

start_region_name = get_region_name(next(region for region in a1800_regions if not region.requirements))

a1800_populations = [obj for obj in a1800_objects if isinstance(
    obj, A1800Product) and obj.type == ProductType.WORKFORCE]

a1800_unlocks = [unlock for unlock in a1800_objects if isinstance(unlock, A1800Unlock)]

a1800_unlock_locations = [unlock for unlock in sorted(
    a1800_unlocks, key=trigger_key) if unlock.unlock_population and unlock.unlock_amount]

starting_items = [unlock for unlock in a1800_unlocks if not unlock.unlock_population and not unlock.unlock_amount]

a1800_event_items = [obj for obj in a1800_objects if not isinstance(
    obj, A1800Region) and not isinstance(obj, A1800Chain) and not isinstance(obj, A1800Unlock)]

a1800_event_locations = [event_location for location in a1800_unlocks if isinstance(
    location, A1800Factory) and location.output for event_location in get_event_locations(location)]

a1800_triggers = [(guid, amount, list(location)) for (guid, amount), location in groupby(
    sorted(a1800_unlock_locations, key=trigger_key), key=trigger_key) if guid and amount]

a1800_items: list[A1800Object] = [
    *a1800_unlocks,
    *a1800_event_items
]

a1800_locations: list[A1800Object] = [
    *a1800_unlock_locations,
    *a1800_event_locations
]

a1800_item_dict = {get_item_name(item): item for item in a1800_items}

a1800_location_dict = {get_location_name(location): location for location in a1800_locations}

a1800_population_dict = {population.name: population for population in a1800_populations}

item_name_to_ap_code = {name: item.ap_code for name,
                        item in a1800_item_dict.items() if isinstance(item, A1800Unlock) and item.ap_code}

location_name_to_ap_code = {name: location.ap_code for name,
                            location in a1800_location_dict.items() if isinstance(location, A1800Unlock) and location.ap_code}


a1800_rules: list[tuple[str, A1800Rule]] = []

a1800_required_items: set[Requirement] = set()


def player_has(*requirements: Requirement, bool_func: Callable[[Iterable[object]], bool] = all) -> A1800Rule:
    return lambda state, player, requirements=requirements: bool_func(
        state.has(get_requirement_name(requirement), player) for requirement in requirements)  # type: ignore


def generate_requirements_and_rules(to_check: set[Requirement], checked: set[Requirement], rules: list[tuple[str, A1800Rule]]) -> tuple[set[Requirement], list[tuple[str, A1800Rule]]]:
    if not to_check:
        return checked, rules

    requirement = to_check.pop()
    checked.add(requirement)

    a1800_object = next(obj for obj in a1800_objects if obj.name ==
                        requirement[0] and requirement[1].issubset(obj.region))

    new_requirements: set[Requirement] = set()
    if isinstance(a1800_object, A1800Unlock):
        unlock = a1800_object
        event_locations = [event_location for event_location in a1800_event_locations if event_location.name.split(
            " => ")[0].split(": ", 1)[1] == unlock.name and event_location.region.issubset(unlock.region)]

        if isinstance(unlock, A1800Factory):
            new_requirements |= {(name, frozenset(unlock.region))
                                 for name in {unlock.name} | unlock.cost | unlock.maintenance | unlock.input}

        if isinstance(unlock, A1800Upgrade):
            previous_unlock = next((prev for prev in a1800_unlocks if prev.name == unlock.previous_building), None)
            if previous_unlock:
                new_requirements.add((previous_unlock.name, frozenset(previous_unlock.region)))

                if isinstance(unlock, A1800Residence) and isinstance(previous_unlock, A1800Residence):
                    new_requirements |= {(name, frozenset(previous_unlock.region))
                                         for name in previous_unlock.consumption}

        for event_location in event_locations:
            rules.append((event_location.name, player_has(*new_requirements)))
            print(f"Adding rule: {event_location.name} needs {new_requirements}")

    elif not isinstance(a1800_object, A1800Region):
        event_locations = [
            event_location for event_location in a1800_event_locations if event_location.name.split(" => ")[1] == a1800_object.name and event_location.region.issubset(a1800_object.region)]

        for event_location in event_locations:
            unlock_name = event_location.name.split(" => ")[0].split(": ", 1)[1]

            new_requirements.add((unlock_name, frozenset(event_location.region)))

    for new_requirement in new_requirements:
        if not new_requirement in checked and not new_requirement in to_check:
            to_check.add(new_requirement)

    return generate_requirements_and_rules(to_check, checked, rules)


def process_options(options: A1800Options) -> None:
    global a1800_required_items, a1800_rules

    population_requirements = [
        ("Artisans", 1, False, False, False)
    ]

    victory_event_location_name = ""
    victory_required_items: set[Requirement] = set()
    for population_requirement in population_requirements:
        population, amount, supplied, luxury, lifestyle = population_requirement

        victory_event_location_name += f"{population}(Amount: {amount if amount else 1}, "\
            f"Supplied: {'Yes' if supplied else 'No'}, Luxury: {'Yes' if luxury else 'No'}, "\
            f"Lifestyle: {'Yes' if lifestyle else 'No'}) "

        victory_required_items.add(
            (population, frozenset(next(pop for pop in a1800_populations if pop.name == population).region)))

        residence = next(item for item in a1800_items if isinstance(
            item, A1800Residence) and population in item.output)

        if supplied:
            victory_required_items |= set((requirement, frozenset(next(
                obj for obj in a1800_objects if obj.name == requirement).region)) for requirement in residence.consumption)
        if luxury:
            victory_required_items |= set((requirement, frozenset(next(
                obj for obj in a1800_objects if obj.name == requirement).region)) for requirement in residence.luxury)
        if lifestyle:
            victory_required_items |= set((requirement, frozenset(next(
                obj for obj in a1800_objects if obj.name == requirement).region)) for requirement in residence.lifestyle)

    victory_event_location = A1800Object(victory_event_location_name + "=> Victory", DLC.VANILLA, {"OW"})

    victory_checked_items: set[Requirement] = {("Victory", frozenset({"OW", "NW", "En", "Ar"}))}

    victory_rules = [(victory_event_location.name, player_has(*victory_required_items))]

    a1800_event_locations.append(victory_event_location)
    a1800_locations.append(victory_event_location)
    a1800_location_dict[victory_event_location.name] = victory_event_location

    a1800_required_items, a1800_rules = generate_requirements_and_rules(
        victory_required_items, victory_checked_items, victory_rules)
