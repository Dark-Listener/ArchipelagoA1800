from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar, Iterator, Optional

from ._Chain import find_chains, get_chains
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, UnlockType
from ._Product import find_populations, find_products


def create_unlock_name(name: str, region: Region, prefix: str = "", postfix: str = "") -> str:
    if not region or region == ALL_REGIONS:
        return prefix + name + postfix
    else:
        return f"{prefix}{region.name}: {name}{postfix}"


@dataclass
class A1800Unlock:
    __item_id: ClassVar[int] = 1
    name: str
    dlc: DLC
    region: Region
    guids: set[int]
    lock_guids: set[int]
    unlocking_region: Region
    unlocking_population: str
    unlocking_amount: int
    cost: set[str] = field(default_factory=lambda: set())
    maintenance: set[str] = field(default_factory=lambda: set())
    input: set[str] = field(default_factory=lambda: set())
    output: set[str] = field(default_factory=lambda: set())
    unlock_chain: str = ""
    previous_building: str = ""
    consumption: set[str] = field(default_factory=lambda: set())
    luxury: set[str] = field(default_factory=lambda: set())
    lifestyle: set[str] = field(default_factory=lambda: set())
    type: UnlockType = UnlockType.UNLOCK
    is_early: bool = False

    def __post_init__(self) -> None:
        self.ap_code = A1800Unlock.__item_id
        A1800Unlock.__item_id += 1

        self.ap_item_name: str = create_unlock_name(self.name, self.region)

        self.is_progressive: bool = False

        if not self.unlocking_region or not self.unlocking_population or not self.unlocking_amount:
            self.ap_location_name = f"Game start ({self.name})"
        else:
            pop_str = self.unlocking_population if self.unlocking_amount != 1 else self.unlocking_population[:-1]
            if len(list(find_populations(self.unlocking_population))) != 1:
                pop_str += f" ({self.unlocking_region})"
            self.ap_location_name = f"{self.unlocking_amount} {pop_str} ({self.ap_item_name})"
            self.unlocking_guid = next(find_populations(self.unlocking_population, self.unlocking_region)).guid

        self.unlock_guids: set[int] = self.guids

        if self.type == UnlockType.UNLOCK:
            if self.cost or self.maintenance:
                self.type |= UnlockType.BUILDING

            if self.input or self.output or self.unlock_chain:
                self.type |= UnlockType.FACTORY

                if self.unlock_chain:
                    self.unlock_guids.add(next(find_chains(self.unlock_chain, self.region)).guid)

                for output in self.output:
                    output_guid = next(find_products(output, self.region)).guid
                    if output_guid:
                        self.unlock_guids.add(output_guid)

            if self.previous_building:
                self.type |= UnlockType.UPGRADE

            if self.consumption or self.luxury or self.lifestyle:
                self.type |= UnlockType.RESIDENCE


_a1800_unlocks: list[A1800Unlock] = [
    # Building
    A1800Unlock("Dirt Road", DLC.VANILLA, Region.OW, {1000178}, {1000178}, NO_REGION, "", 0, type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.OW, {1010371}, {130040}, NO_REGION, "", 0, {"Timber"}, set()),

    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.OW, {1010517, 1010540}, set(), NO_REGION, "", 0,
                {"Timber"}, set()),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.OW, {1010516}, {1010516}, Region.OW, "Workers", 1,
                {"Timber", "Bricks"}, set()),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.OW, {1010522}, {1010522}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, set()),

    A1800Unlock("Quay", DLC.VANILLA, Region.OW, {1010567}, {130121}, Region.OW, "Workers", 150,
                type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.OW, {1010519}, {130121}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, set()),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.OW, {100586}, {100586}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, set()),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.OW, {1010523}, {1010523}, Region.OW, "Workers", 300,
                {"Timber", "Bricks", "Steel Beams", "Weapons"}, set()),


    # Building, Factory
    A1800Unlock("Lumberjack's Hut", DLC.VANILLA, Region.OW, {1010266}, {140029}, NO_REGION, "", 0,
                set(), {"Farmers"}, set(), {"Wood"}, "Timber"),

    A1800Unlock("Sawmill", DLC.VANILLA, Region.OW, {100451}, {140029}, NO_REGION, "", 0,
                set(), {"Farmers"}, {"Wood"}, {"Timber"}, "Timber"),

    A1800Unlock("Marketplace", DLC.VANILLA, Region.OW, {1010372}, {130057}, NO_REGION, "", 0,
                {"Timber"}, set(), set(), {"Market"}, ""),

    A1800Unlock("Fishery", DLC.VANILLA, Region.OW, {1010278}, {130056}, Region.OW, "Farmers", 50,
                {"Timber"}, {"Farmers"}, set(), {"Fish"}, "", is_early=True),

    A1800Unlock("Sheep Farm", DLC.VANILLA, Region.OW, {1010267}, {130060}, Region.OW, "Farmers", 100,
                {"Timber"}, {"Farmers"}, set(), {"Wool"}, "Work Clothes", is_early=True),

    A1800Unlock("Framework Knitters", DLC.VANILLA, Region.OW, {1010315}, {130060}, Region.OW, "Farmers", 100,
                {"Timber"}, {"Farmers"}, {"Wool"}, {"Work Clothes"}, "Work Clothes", is_early=True),

    A1800Unlock("Potato Farm", DLC.VANILLA, Region.OW, {1010265}, {140028}, Region.OW, "Farmers", 100,
                {"Timber"}, {"Farmers"}, set(), {"Potatoes"}, "Schnapps"),

    A1800Unlock("Schnapps Distillery", DLC.VANILLA, Region.OW, {1010294}, {140028}, Region.OW, "Farmers", 100,
                {"Timber"}, {"Farmers"}, {"Potatoes"}, {"Schnapps"}, "Schnapps"),

    A1800Unlock("Fire Station", DLC.VANILLA, Region.OW, {1010463}, {1010463}, Region.OW, "Farmers", 150,
                {"Timber"}, set(), set(), {"Fire Protection"}, ""),

    A1800Unlock("Pub", DLC.VANILLA, Region.OW, {1010358}, {130042}, Region.OW, "Farmers", 150,
                {"Timber"}, set(), set(), {"Pub"}, ""),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.OW, {100416}, {140031}, Region.OW, "Workers", 1,
                {"Timber"}, {"Workers"}, set(), {"Clay"}, "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.OW, {1010283}, {140031}, Region.OW, "Workers", 1,
                {"Timber"}, {"Workers"}, {"Clay"}, {"Bricks"}, "Bricks"),

    A1800Unlock("Pig Farm", DLC.VANILLA, Region.OW, {1010269}, {140027}, Region.OW, "Workers", 1,
                {"Timber"}, {"Farmers"}, set(), {"Pigs"}, "Sausages"),

    A1800Unlock("Slaughterhouse", DLC.VANILLA, Region.OW, {1010316}, {140027}, Region.OW, "Workers", 1,
                {"Timber", "Bricks"}, {"Workers"}, {"Pigs"}, {"Sausages"}, "Sausages"),

    A1800Unlock("Grain Farm", DLC.VANILLA, Region.OW, {1010262}, {140033}, Region.OW, "Workers", 150,
                {"Timber"}, {"Farmers"}, set(), {"Grain"}, "Bread"),

    A1800Unlock("Flour Mill", DLC.VANILLA, Region.OW, {1010313}, {140033}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, {"Farmers"}, {"Grain"}, {"Flour"}, "Bread"),

    A1800Unlock("Bakery", DLC.VANILLA, Region.OW, {1010291}, {140033}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, {"Workers"}, {"Flour"}, {"Bread"}, "Bread"),

    A1800Unlock("Church", DLC.VANILLA, Region.OW, {1010359}, {130043}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, set(), set(), {"Church"}, ""),

    A1800Unlock("Sailmakers", DLC.VANILLA, Region.OW, {1010288}, {140050}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, {"Workers"}, {"Wool"}, {"Sails"}, "Sails"),

    A1800Unlock("Sailing Shipyard", DLC.VANILLA, Region.OW, {1010520}, {130050}, Region.OW, "Workers", 150,
                {"Timber", "Bricks"}, {"Workers"}, {"Timber", "Sails"}, {"Sea Travel"}, ""),

    A1800Unlock("Charcoal Kiln", DLC.VANILLA, Region.OW, {1010298}, {140034}, Region.OW, "Workers", 300,
                {"Timber", "Bricks"}, {"Workers"}, set(), {"Coal"}, "Steel Beams"),

    A1800Unlock("Iron Mine", DLC.VANILLA, Region.OW, {1010305}, {140034}, Region.OW, "Workers", 300,
                {"Timber", "Bricks"}, {"Workers"}, set(), {"Iron"}, "Steel Beams"),

    A1800Unlock("Furnace", DLC.VANILLA, Region.OW, {1010297}, {140034}, Region.OW, "Workers", 300,
                {"Timber", "Bricks"}, {"Workers"}, {"Iron", "Coal"}, {"Steel"}, "Steel Beams"),

    A1800Unlock("Steelworks", DLC.VANILLA, Region.OW, {1010296}, {140034}, Region.OW, "Workers", 300,
                {"Timber", "Bricks"}, {"Workers"}, {"Steel"}, {"Steel Beams"}, "Steel Beams"),

    A1800Unlock("Rendering Works", DLC.VANILLA, Region.OW, {1010312}, {140030}, Region.OW, "Workers", 300,
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Pigs"}, {"Tallow"}, "Soap"),

    A1800Unlock("Soap Factory", DLC.VANILLA, Region.OW, {1010281}, {140030}, Region.OW, "Workers", 300,
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Tallow"}, {"Soap"}, "Soap"),

    A1800Unlock("Weapon Factory", DLC.VANILLA, Region.OW, {1010299}, {140051}, Region.OW, "Workers", 300,
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Steel"}, {"Weapons"}, "Weapons"),

    A1800Unlock("Hop Farm", DLC.VANILLA, Region.OW, {1010264}, {140035}, Region.OW, "Workers", 500,
                {"Timber"}, {"Farmers"}, set(), {"Hops"}, "Beer"),

    A1800Unlock("Malthouse", DLC.VANILLA, Region.OW, {1010314}, {140035}, Region.OW, "Workers", 500,
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Grain"}, {"Malt"}, "Beer"),

    A1800Unlock("Brewery", DLC.VANILLA, Region.OW, {1010292}, {140035}, Region.OW, "Workers", 500,
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Malt", "Hops"}, {"Beer"}, "Beer"),

    A1800Unlock("Police Station", DLC.VANILLA, Region.OW, {1010462}, {1010462}, Region.OW, "Workers", 500,
                {"Timber", "Bricks"}, set(), set(), {"Riot Control"}, ""),

    A1800Unlock("School", DLC.VANILLA, Region.OW, {1010360}, {130044}, Region.OW, "Workers", 750,
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"School"}, ""),


    # Building, Upgrade
    A1800Unlock("Paved Street", DLC.VANILLA, Region.OW, {1010035}, {1010035}, Region.OW, "Workers", 1,
                {"Bricks"}, set(), previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.OW, {100516}, {130053}, Region.OW, "Workers", 1,
                {"Timber", "Bricks"}, set(), previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.OW, {100510, 100514}, {130053}, Region.OW, "Workers", 1,
                {"Timber", "Bricks"}, set(), previous_building="Small Trading Post"),


    # Building, Factory, Residence
    A1800Unlock("Farmer Residence", DLC.VANILLA, Region.OW, {1010343}, {1010343}, NO_REGION, "", 0,
                {"Timber"}, set(), set(), {"Farmers"}, "",
                consumption={"Market", "Fish", "Work Clothes", "Fire Protection"},
                luxury={"Schnapps", "Pub"},
                # lifestyle={"Flour", "Sugar", "Jam", "Local Mail", "Regional Mail",
                #          "Overseas Mail", "Soap", "Herbs", "Hibiscus Petals"}),
                ),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Worker Residence", DLC.VANILLA, Region.OW, {1010344}, {1010344}, Region.OW, "Farmers", 100,
                {"Timber"}, set(), set(), {"Workers"}, "", "Farmer Residence",
                {"Market", "Fish", "Work Clothes", "Sausages", "Bread",
                    "Soap", "School", "Fire Protection", "Riot Control"},
                {"Schnapps", "Pub", "Church", "Beer"},
                # {"Rum", "Penny Farthings", "Hot Sauce", "Local Mail", "Regional Mail",
                # "Overseas Mail", "Beef", "Soccer Balls", "Clay Pipes"}, is_early=True),
                is_early=True),

    A1800Unlock("Artisan Residence", DLC.VANILLA, Region.OW, {1010345}, {1010345}, Region.OW, "Workers", 750,
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"Artisans"}, "", "Worker Residence",
                # {"Sausages", "Bread", "Soap", "School", "Canned Food",
                # "Sewing Machines", "Fur Coats", "University", "Fire Protection", "Riot Control", "Healthcare"},
                # {"Church", "Beer", "Variety Theatre", "Rum"},
                # {"Wool", "Clay", "Paper", "Local Mail", "Regional Mail",
                # "Overseas Mail", "Soccer Balls", "Perfumes", "Scooter"}),
                type=UnlockType.BUILDING | UnlockType.FACTORY | UnlockType.UPGRADE | UnlockType.RESIDENCE),
]


def get_unlocks() -> Sequence[A1800Unlock]:
    global _a1800_unlocks
    return _a1800_unlocks


def find_unlocks(name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
    global _a1800_unlocks
    return (unlock for unlock in _a1800_unlocks if unlock.name == name and region in unlock.region)


def find_ap_item(ap_name: str) -> Optional[A1800Unlock]:
    global _a1800_unlocks
    return next((unlock for unlock in _a1800_unlocks if unlock.ap_item_name == ap_name), None)


# Assure all references exist
for unlock in _a1800_unlocks:
    assert unlock.region

    if unlock.unlocking_region and unlock.unlocking_population and unlock.unlocking_amount:
        assert next(find_populations(unlock.unlocking_population, unlock.unlocking_region), None)

    for cost in unlock.cost:
        assert next(find_products(cost, unlock.region), None)

    for maintenance in unlock.maintenance:
        assert next(find_products(maintenance, unlock.region), None)

    for input in unlock.input:
        assert next(find_products(input, unlock.region), None)

    for output in unlock.output:
        assert next(find_products(output, unlock.region), None)

    if unlock.unlock_chain:
        assert next(find_chains(unlock.unlock_chain, unlock.region), None)

    if unlock.previous_building:
        assert next(find_unlocks(unlock.previous_building, unlock.region), None)

    for consumption in unlock.consumption:
        assert next(find_products(consumption, unlock.region), None)

    for luxury in unlock.luxury:
        assert next(find_products(luxury, unlock.region), None)

    for lifestyle in unlock.lifestyle:
        assert next(find_products(lifestyle, unlock.region), None)

# Assure all chain references exist
for chain in get_chains():
    assert chain.region

    for name, region in chain.elements:
        assert next(find_unlocks(name, region), None)


def trigger_key(location: A1800Unlock) -> tuple[int, int]:
    assert location.unlocking_region and location.unlocking_population and location.unlocking_amount
    return next(
        find_populations(location.unlocking_population, location.unlocking_region)).guid, location.unlocking_amount


_a1800_unlock_locations = sorted(
    [unlock for unlock in _a1800_unlocks
     if unlock.unlocking_region and unlock.unlocking_population and unlock.unlocking_amount], key=trigger_key)


def get_unlock_locations() -> Sequence[A1800Unlock]:
    global _a1800_unlock_locations
    return _a1800_unlock_locations


_starting_items = [unlock for unlock in _a1800_unlocks
                   if not unlock.unlocking_region or not unlock.unlocking_population or not unlock.unlocking_amount]


def find_starting_items(name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
    global _starting_items
    return (item for item in _starting_items if item.name == name and region in item.region)


def get_starting_items() -> Sequence[A1800Unlock]:
    global _starting_items
    return _starting_items
