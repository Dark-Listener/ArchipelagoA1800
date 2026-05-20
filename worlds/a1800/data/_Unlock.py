from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar, Iterator, Optional

from ._Chain import find_chains, get_chains
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, TriggerType, UnlockType
from ._Product import find_populations, find_products
from ._Trigger import ANY, POPULATION, SESSION_ENTER, Trigger


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
    trigger: Trigger
    cost: set[str] = field(default_factory=lambda: set())
    maintenance: set[str] = field(default_factory=lambda: set())
    input: set[str] = field(default_factory=lambda: set())
    output: set[str] = field(default_factory=lambda: set())
    unlock_chain: str | set[tuple[str, Region]] = ""
    previous_building: str = ""
    consumption: set[str] = field(default_factory=lambda: set())
    luxury: set[str] = field(default_factory=lambda: set())
    lifestyle: set[str] = field(default_factory=lambda: set())
    ap_code: Optional[int] = None
    ap_item_name: str = ""
    ap_location_name: str = ""
    unlock_guids: set[int] = field(default_factory=lambda: set())
    type: UnlockType = UnlockType.UNLOCK
    is_early: bool = False
    is_progressive: bool = False

    def __post_init__(self) -> None:
        if not self.ap_code:
            self.ap_code = A1800Unlock.__item_id
            A1800Unlock.__item_id += 1

        if not self.ap_item_name:
            self.ap_item_name = create_unlock_name(self.name, self.region)

        self.ap_location_name = self.trigger.get_ap_location_name(self.ap_item_name)

        self.unlock_guids = self.guids

        if self.type == UnlockType.UNLOCK:
            if self.cost or self.maintenance:
                self.type |= UnlockType.BUILDING

            if self.input or self.output or self.unlock_chain:
                self.type |= UnlockType.FACTORY

                if self.unlock_chain:
                    if isinstance(self.unlock_chain, str):
                        self.unlock_guids.add(next(find_chains(self.unlock_chain, self.region)).guid)
                    else:
                        for chain, region in self.unlock_chain:
                            self.unlock_guids.add(next(find_chains(chain, region)).guid)

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
    A1800Unlock("Dirt Road", DLC.VANILLA, Region.OW, {1000178}, {1000178},
                SESSION_ENTER(Session.OW), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.OW, {1010371}, {130040},
                SESSION_ENTER(Session.OW), {"Timber"}, set()),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.OW, {1010516}, {1010516},
                POPULATION(Region.OW, "Workers", 1), {"Timber", "Bricks"}, set()),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.OW, {1010522}, {1010522},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks", "Weapons"}, set()),

    A1800Unlock("Quay", DLC.VANILLA, Region.OW, {1010567}, {130121},
                POPULATION(Region.OW, "Workers", 150), type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.OW, {1010519}, {130121},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}, set()),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.OW, {100586}, {100586},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}, set()),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.OW, {1010523}, {1010523},
                POPULATION(Region.OW, "Workers", 300), {"Timber", "Bricks", "Steel Beams", "Weapons"}, set()),

    A1800Unlock("Town Hall", DLC.VANILLA, Region.OW, {100415}, {100415},
                POPULATION(Region.OW, "Artisans", 1), {"Timber", "Bricks", "Steel Beams", "Windows"}, set()),

    A1800Unlock("Flame Tower", DLC.VANILLA, Region.OW, {625}, {625},
                POPULATION(Region.OW, "Artisans", 1), {"Timber", "Bricks", "Steel Beams", "Weapons"}, set()),

    A1800Unlock("Public Mooring", DLC.VANILLA, Region.OW, {100429}, {130052},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams", "Windows"}, set()),

    A1800Unlock("Pier", DLC.VANILLA, Region.OW, {100519}, {100519},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams", "Windows"}, set()),

    A1800Unlock("Repair Crane", DLC.VANILLA, Region.OW, {1010525}, {1010525},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams"}, set()),

    # Building, Factory
    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.OW, {1010517, 1010540}, {1010517, 1010540},
                SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}, {"Sea Travel"}, set(), {"Settling"}),

    A1800Unlock("Lumberjack's Hut", DLC.VANILLA, Region.OW, {1010266}, {140029},
                SESSION_ENTER(Session.OW), set(), {"Farmers"}, set(), {"Wood"}, "Timber"),

    A1800Unlock("Sawmill", DLC.VANILLA, Region.OW, {100451}, {140029},
                SESSION_ENTER(Session.OW), set(), {"Farmers"}, {"Wood"}, {"Timber"}, "Timber"),

    A1800Unlock("Marketplace", DLC.VANILLA, Region.OW, {1010372}, {130057},
                SESSION_ENTER(Session.OW), {"Timber"}, set(), set(), {"Market"}),

    A1800Unlock("Fishery", DLC.VANILLA, Region.OW, {1010278}, {130056},
                POPULATION(Region.OW, "Farmers", 50), {"Timber"}, {"Farmers"}, set(), {"Fish"}, "", is_early=True),

    A1800Unlock("Sheep Farm", DLC.VANILLA, Region.OW, {1010267}, {130060},
                POPULATION(Region.OW, "Farmers", 100),
                {"Timber"}, {"Farmers"}, set(), {"Wool"}, "Work Clothes", is_early=True),

    A1800Unlock("Framework Knitters", DLC.VANILLA, Region.OW, {1010315}, {130060},
                POPULATION(Region.OW, "Farmers", 100),
                {"Timber"}, {"Farmers"}, {"Wool"}, {"Work Clothes"}, "Work Clothes", is_early=True),

    A1800Unlock("Potato Farm", DLC.VANILLA, Region.OW, {1010265}, {140028},
                POPULATION(Region.OW, "Farmers", 100), {"Timber"}, {"Farmers"}, set(), {"Potatoes"}, "Schnapps"),

    A1800Unlock("Schnapps Distillery", DLC.VANILLA, Region.OW, {1010294}, {140028},
                POPULATION(Region.OW, "Farmers", 100), {"Timber"}, {"Farmers"}, {"Potatoes"}, {"Schnapps"}, "Schnapps"),

    A1800Unlock("Fire Station", DLC.VANILLA, Region.OW, {1010463}, {1010463},
                POPULATION(Region.OW, "Farmers", 150), {"Timber"}, set(), set(), {"Fire Protection"}, is_early=True),

    A1800Unlock("Pub", DLC.VANILLA, Region.OW, {1010358}, {130042},
                POPULATION(Region.OW, "Farmers", 150), {"Timber"}, set(), set(), {"Pub"}),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.OW, {100416}, {140031},
                POPULATION(Region.OW, "Workers", 1), {"Timber"}, {"Workers"}, set(), {"Clay"}, "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.OW, {1010283}, {140031},
                POPULATION(Region.OW, "Workers", 1), {"Timber"}, {"Workers"}, {"Clay"}, {"Bricks"}, "Bricks"),

    A1800Unlock("Pig Farm", DLC.VANILLA, Region.OW, {1010269}, {140027},
                POPULATION(Region.OW, "Workers", 1), {"Timber"}, {"Farmers"}, set(), {"Pigs"}, "Sausages"),

    A1800Unlock("Slaughterhouse", DLC.VANILLA, Region.OW, {1010316}, {140027},
                POPULATION(Region.OW, "Workers", 1),
                {"Timber", "Bricks"}, {"Workers"}, {"Pigs"}, {"Sausages"}, "Sausages"),

    A1800Unlock("Grain Farm", DLC.VANILLA, Region.OW, {1010262}, {140033},
                POPULATION(Region.OW, "Workers", 150), {"Timber"}, {"Farmers"}, set(), {"Grain"}, "Bread"),

    A1800Unlock("Flour Mill", DLC.VANILLA, Region.OW, {1010313}, {140033},
                POPULATION(Region.OW, "Workers", 150),
                {"Timber", "Bricks"}, {"Farmers"}, {"Grain"}, {"Flour"}, "Bread"),

    A1800Unlock("Bakery", DLC.VANILLA, Region.OW, {1010291}, {140033},
                POPULATION(Region.OW, "Workers", 150),
                {"Timber", "Bricks"}, {"Workers"}, {"Flour"}, {"Bread"}, "Bread"),

    A1800Unlock("Church", DLC.VANILLA, Region.OW, {1010359}, {130043},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}, set(), set(), {"Church"}),

    A1800Unlock("Sailmakers", DLC.VANILLA, Region.OW, {1010288}, {140050},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}, {"Workers"}, {"Wool"}, {"Sails"}, "Sails"),

    A1800Unlock("Sailing Shipyard", DLC.VANILLA, Region.OW, {1010520}, {130050},
                POPULATION(Region.OW, "Workers", 150),
                {"Timber", "Bricks"}, {"Workers"}, {"Timber", "Sails"}, {"Sea Travel"}),

    A1800Unlock("Charcoal Kiln", DLC.VANILLA, Region.OW, {1010298}, {140034},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks"}, {"Workers"}, set(), {"Coal"}, "Steel Beams"),

    A1800Unlock("Iron Mine", DLC.VANILLA, Region.OW, {1010305}, {140034},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks"}, {"Workers"}, set(), {"Iron"}, "Steel Beams"),

    A1800Unlock("Furnace", DLC.VANILLA, Region.OW, {1010297}, {140034},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks"}, {"Workers"}, {"Iron", "Coal"}, {"Steel"}, "Steel Beams"),

    A1800Unlock("Steelworks", DLC.VANILLA, Region.OW, {1010296}, {140034},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks"}, {"Workers"}, {"Steel"}, {"Steel Beams"}, "Steel Beams"),

    A1800Unlock("Rendering Works", DLC.VANILLA, Region.OW, {1010312}, {140030},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Pigs"}, {"Tallow"}, "Soap"),

    A1800Unlock("Soap Factory", DLC.VANILLA, Region.OW, {1010281}, {140030},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Tallow"}, {"Soap"}, "Soap"),

    A1800Unlock("Weapon Factory", DLC.VANILLA, Region.OW, {1010299}, {140051},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Steel"}, {"Weapons"}, "Weapons"),

    A1800Unlock("Hop Farm", DLC.VANILLA, Region.OW, {1010264}, {140035},
                POPULATION(Region.OW, "Workers", 500),
                {"Timber"}, {"Farmers", "Settling"}, set(), {"Hops"}, "Beer"),

    A1800Unlock("Malthouse", DLC.VANILLA, Region.OW, {1010314}, {140035},
                POPULATION(Region.OW, "Workers", 500),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Grain"}, {"Malt"}, "Beer"),

    A1800Unlock("Brewery", DLC.VANILLA, Region.OW, {1010292}, {140035},
                POPULATION(Region.OW, "Workers", 500),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"}, {"Malt", "Hops"}, {"Beer"}, "Beer"),

    A1800Unlock("Police Station", DLC.VANILLA, Region.OW, {1010462}, {1010462},
                POPULATION(Region.OW, "Workers", 500),
                {"Timber", "Bricks"}, set(), set(), {"Riot Control"}),

    A1800Unlock("School", DLC.VANILLA, Region.OW, {1010360}, {130044},
                POPULATION(Region.OW, "Workers", 750),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"School"}),

    A1800Unlock("Sand Mine", DLC.VANILLA, Region.OW, {1010560}, {140037},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks"}, {"Workers"}, set(), {"Quartz Sand"}, "Windows"),

    A1800Unlock("Glassmakers", DLC.VANILLA, Region.OW, {1010319}, {140037},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams"}, {"Artisans"}, {"Quartz Sand"}, {"Glass"}, "Windows"),

    A1800Unlock("Window Makers", DLC.VANILLA, Region.OW, {1010285}, {140037},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams"}, {"Artisans"}, {"Wood", "Glass"}, {"Windows"}, "Windows"),

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.OW, {1010263}, {140036},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber"}, {"Farmers"}, set(), {"Beef"}, "Canned Food"),

    A1800Unlock("Red Pepper Farm", DLC.VANILLA, Region.OW, {100654}, {140036},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber"}, {"Farmers", "Settling"}, set(), {"Red Peppers"}, "Canned Food"),

    A1800Unlock("Artisanal Kitchen", DLC.VANILLA, Region.OW, {1010293}, {140036},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Beef", "Red Peppers"}, {"Goulash"}, "Canned Food"),

    A1800Unlock("Cannery", DLC.VANILLA, Region.OW, {1010295}, {140036},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Iron", "Goulash"}, {"Canned Food"}, "Canned Food"),

    A1800Unlock("Coal Mine", DLC.VANILLA, Region.OW, {1010304}, {140032},
                POPULATION(Region.OW, "Artisans", 250),
                {"Timber", "Bricks"}, {"Workers", "Settling"}, set(), {"Coal"}, "Sewing Machines"),

    A1800Unlock("Sewing Machine Factory", DLC.VANILLA, Region.OW, {1010284}, {140032},
                POPULATION(Region.OW, "Artisans", 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Wood", "Steel"}, {"Sewing Machines"}, "Sewing Machines"),

    A1800Unlock("Variety Theatre", DLC.VANILLA, Region.OW, {1010361}, {130045},
                POPULATION(Region.OW, "Artisans", 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Variety Theatre"}),

    A1800Unlock("Zoo", DLC.VANILLA, Region.OW, {1010470}, {1010470},
                POPULATION(Region.OW, "Artisans", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Zoo"}),

    A1800Unlock("Hunting Cabin", DLC.VANILLA, Region.OW, {1010558}, {140046, 130201},
                ANY(POPULATION(Region.OW, "Artisans", 900), POPULATION(Region.NW, "Jornaleros", 100)),
                {"Timber"}, {"Farmers", "Settling"},
                set(), {"Furs"}, {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Cotton Plantation", DLC.VANILLA, Region.NW, {1010331}, {140046, 130201, 130098},
                ANY(POPULATION(Region.OW, "Artisans", 900), POPULATION(Region.NW, "Jornaleros", 100)),
                {"Timber"}, {"Jornaleros"},
                set(), {"Cotton"}, {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Cotton Mill", DLC.VANILLA, Region.NW, {1010318}, {140046, 130201, 130098},
                ANY(POPULATION(Region.OW, "Artisans", 900), POPULATION(Region.NW, "Jornaleros", 100)),
                {"Timber"}, {"Jornaleros"},
                {"Cotton"}, {"Cotton Fabric"}, {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Fur Dealer", DLC.VANILLA, Region.OW, {1010325}, {140046, 130201},
                ANY(POPULATION(Region.OW, "Artisans", 900), POPULATION(Region.NW, "Jornaleros", 100)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Furs", "Cotton Fabric"}, {"Fur Coats"}, {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Hospital", DLC.VANILLA, Region.OW, {1010464}, {1010464},
                POPULATION(Region.OW, "Artisans", 900),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Healthcare"}),

    A1800Unlock("University", DLC.VANILLA, Region.OW, {1010362}, {130046},
                POPULATION(Region.OW, "Artisans", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"University"}),

    A1800Unlock("Museum", DLC.VANILLA, Region.OW, {1010471}, {1010471},
                POPULATION(Region.OW, "Artisans", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Museum"}),

    # Building, Upgrade
    A1800Unlock("Paved Street", DLC.VANILLA, Region.OW, {1010035}, {1010035},
                POPULATION(Region.OW, "Workers", 1),
                {"Bricks"}, set(), previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.OW, {100516}, {130053},
                POPULATION(Region.OW, "Workers", 1),
                {"Timber", "Bricks"}, set(), previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.OW, {100510, 100514}, {130053},
                POPULATION(Region.OW, "Workers", 1),
                {"Timber", "Bricks"}, set(), previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.OW, {100517}, {130054},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.OW, {100511, 100515}, {130054},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), previous_building="Medium Trading Post"),

    # Building, Factory, Residence
    A1800Unlock("Farmer Residence", DLC.VANILLA, Region.OW, {1010343}, {1010343},
                SESSION_ENTER(Session.OW), {"Timber"}, set(), {"Market"}, {"Farmers"}, "",
                consumption={"Market", "Fish", "Work Clothes", "Fire Protection"},
                luxury={"Schnapps", "Pub"},
                lifestyle={"Flour", "Sugar", "Jam", "Local Mail", "Regional Mail",
                           "Overseas Mail", "Soap", "Herbs", "Hibiscus Petals"}),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Worker Residence", DLC.VANILLA, Region.OW, {1010344}, {1010344},
                POPULATION(Region.OW, "Farmers", 100),
                {"Timber"}, set(), set(), {"Workers"}, "", "Farmer Residence",
                {"Market", "Fish", "Work Clothes", "Sausages", "Bread",
                    "Soap", "School", "Fire Protection", "Riot Control"},
                {"Schnapps", "Pub", "Church", "Beer"},
                {"Rum", "Penny Farthings", "Hot Sauce", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Beef", "Soccer Balls", "Clay Pipes"},
                is_early=True),

    A1800Unlock("Artisan Residence", DLC.VANILLA, Region.OW, {1010345}, {1010345},
                POPULATION(Region.OW, "Workers", 750),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"Artisans"}, "", "Worker Residence",
                {"Sausages", "Bread", "Soap", "School", "Canned Food", "Sewing Machines",
                    "Fur Coats", "University", "Fire Protection", "Riot Control", "Healthcare"},
                {"Church", "Beer", "Variety Theatre", "Rum"},
                {"Wool", "Clay", "Paper", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Soccer Balls", "Perfumes", "Scooter"}),

    A1800Unlock("Engineer Residence", DLC.VANILLA, Region.OW, {1010346}, {1010346},
                POPULATION(Region.OW, "Artisans", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Engineers"}, "", "Artisan Residence",
                {"Canned Food", "Sewing Machines", "Fur Coats", "University", "Glasses", "Coffee",
                    "Electricity", "Light Bulbs", "Fire Protection", "Riot Control", "Healthcare"},
                {"Variety Theatre", "Rum", "Penny Farthings", "Pocket Watches", "Bank"},
                {"Soap", "Chocolate", "Shampoo", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Mezcal", "Ice Cream", "Medicine"}),
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
    assert unlock.region, f"Unlock {unlock.name} has no region"

    if unlock.trigger.trigger_type == TriggerType.POPULATION:
        assert next(find_populations(unlock.trigger.population, unlock.trigger.region), None), \
            f"Unlock {unlock.name} trigger references non-existent population {unlock.trigger.population}, " \
            f"{unlock.trigger.region}"

    for cost in unlock.cost:
        assert next(find_products(cost, unlock.region), None), \
            f"Unlock {unlock.name} references non-existent cost {cost}, "

    for maintenance in unlock.maintenance:
        assert next(find_products(maintenance, unlock.region), None), \
            f"Unlock {unlock.name} references non-existent maintenance {maintenance}, "

    for input in unlock.input:
        assert next(find_products(input, unlock.region), None), \
            f"Unlock {unlock.name} references non-existent input {input}, "

    for output in unlock.output:
        assert next(find_products(output, unlock.region), None), \
            f"Unlock {unlock.name} references non-existent output {output}, "

    if unlock.unlock_chain:
        if isinstance(unlock.unlock_chain, str):
            assert next(find_chains(unlock.unlock_chain, unlock.region), None), \
                f"Unlock {unlock.name} references non-existent chain {unlock.unlock_chain}, "
        else:
            for chain, region in unlock.unlock_chain:
                assert next(find_chains(chain, region), None), \
                    f"Unlock {unlock.name} references non-existent chain {chain}, "

    if unlock.previous_building:
        assert next(find_unlocks(unlock.previous_building, unlock.region), None), \
            f"Unlock {unlock.name} references non-existent previous building {unlock.previous_building}, "

#    for consumption in unlock.consumption:
#        assert next(find_products(consumption, unlock.region), None), \
#            f"Unlock {unlock.name} references non-existent consumption {consumption}, "

#    for luxury in unlock.luxury:
#        assert next(find_products(luxury, unlock.region), None), \
#            f"Unlock {unlock.name} references non-existent luxury {luxury}, "

#    for lifestyle in unlock.lifestyle:
#        assert next(find_products(lifestyle, unlock.region), None), \
#            f"Unlock {unlock.name} references non-existent lifestyle {lifestyle}, "

    missing_consumptions: set[str] = set()
    for consumption in unlock.consumption:
        if not next(find_products(consumption, unlock.region), None):
            missing_consumptions.add(consumption)
    if missing_consumptions:
        print(f"Warning for {unlock.name}: removing unknown needs: {missing_consumptions}")
        unlock.consumption -= missing_consumptions

    missing_luxuries: set[str] = set()
    for luxury in unlock.luxury:
        if not next(find_products(luxury, unlock.region), None):
            missing_luxuries.add(luxury)
    if missing_luxuries:
        print(f"Warning for {unlock.name}: removing unknown luxury needs: {missing_luxuries}")
        unlock.consumption -= missing_luxuries

    missing_lifestyles: set[str] = set()
    for lifestyle in unlock.lifestyle:
        if not next(find_products(lifestyle, unlock.region), None):
            missing_lifestyles.add(lifestyle)
    if missing_lifestyles:
        print(f"Warning for {unlock.name}: removing unknown lifestyle needs: {missing_lifestyles}")
        unlock.lifestyle -= missing_lifestyles

# Assure all chain references exist
for chain in get_chains():
    assert chain.region, f"Chain {chain.name} has no region"

    for name, region in chain.elements:
        assert next(find_unlocks(name, region), None), f"Chain {chain.name} references non-existent unlock {name}, " \
            f"{region}"


_a1800_unlock_locations = sorted(_a1800_unlocks, key=lambda location: location.trigger.get_sort_key())


def get_unlock_locations() -> Sequence[A1800Unlock]:
    global _a1800_unlock_locations
    return _a1800_unlock_locations
