from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar, Iterator, Optional

from ._Chains import CHAINS
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, TriggerType, UnlockType
from ._Products import PRODUCTS
from ._Trigger import ANY, COUNTER, FALSE, POPULATION, SESSION_ENTER, Trigger, TRUE


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
    input: set[str | tuple[str, Region]] = field(default_factory=lambda: set())
    output: set[str | tuple[str, Region]] = field(default_factory=lambda: set())
    unlock_chain: str | set[tuple[str, Region]] = ""
    previous_building: str = ""
    consumption: set[str] = field(default_factory=lambda: set())
    luxury: set[str] = field(default_factory=lambda: set())
    lifestyle: set[str] = field(default_factory=lambda: set())
    ap_code: Optional[int] = None
    ap_item_name: str = ""
    ap_location_name: str = ""
    ap_region: Region = NO_REGION
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

    def init(self) -> None:
        self.unlock_guids = self.guids

        if self.type == UnlockType.UNLOCK:
            if self.cost or self.maintenance or self.unlock_chain:
                self.type |= UnlockType.BUILDING

            if self.input or self.output:
                self.type |= UnlockType.FACTORY

            if self.previous_building:
                self.type |= UnlockType.UPGRADE

            if self.consumption or self.luxury or self.lifestyle:
                self.type |= UnlockType.RESIDENCE

        if UnlockType.BUILDING in self.type:
            if self.unlock_chain:
                if isinstance(self.unlock_chain, str):
                    for chain in CHAINS.find_chains(self.unlock_chain, self.name, self.region):
                        self.unlock_guids.add(chain.guid)
                else:
                    for chain, region in self.unlock_chain:
                        self.unlock_guids.add(next(CHAINS.find_chains(chain, self.name, self.region, region)).guid)

        if UnlockType.FACTORY in self.type:
            for output in self.output:
                if isinstance(output, str):
                    output_guid = next(PRODUCTS.find_products(output, self.region)).guid
                else:
                    output_guid = next(PRODUCTS.find_products(output[0], output[1])).guid
                if output_guid:
                    self.unlock_guids.add(output_guid)


_a1800_unlocks: list[A1800Unlock] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    # Meta
    A1800Unlock("Starting Goods", DLC.VANILLA, Region.OW, set(), set(),  # Resolves circular dependency at game start
                TRUE, output={"Timber"}, type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Trading Post Materials and Sea Travel", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={"Timber", "Steel Beams", "Sea Travel"}, output={("Settling", Region.OW | Region.NW)},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Oil Transport OW => NW", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.OW), "Oil Transport"}, output={("Oil", Region.NW)},
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => OW", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.NW), "Oil Transport"}, output={("Oil", Region.OW)},
                type=UnlockType.META | UnlockType.FACTORY),

    # Unlock
    A1800Unlock("Expedition: New World", DLC.VANILLA, ALL_REGIONS, {1701000000}, set(),
                POPULATION(Region.OW, "Artisans", 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.OW, {1010517, 1010540}, set(),
                SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Dirt Road", DLC.VANILLA, Region.OW, {1000178}, {1000178},
                SESSION_ENTER(Session.OW), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.OW, {1010371}, {130040}, SESSION_ENTER(Session.OW), {"Timber"}),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.OW, {1010516}, {1010516},
                POPULATION(Region.OW, "Workers", 1), {"Timber", "Bricks"}),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.OW, {1010522}, {1010522},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.OW, {1010567}, {130121},
                POPULATION(Region.OW, "Workers", 150), type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.OW, {1010519}, {130121},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.OW, {100586}, {100586},
                POPULATION(Region.OW, "Workers", 150), {"Timber", "Bricks"}),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.OW, {1010523}, {1010523},
                POPULATION(Region.OW, "Workers", 300), {"Timber", "Bricks", "Steel Beams", "Weapons"}),

    A1800Unlock("Town Hall", DLC.VANILLA, Region.OW, {100415}, {100415},
                POPULATION(Region.OW, "Artisans", 1), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Flame Tower", DLC.VANILLA, Region.OW, {625}, {625},
                POPULATION(Region.OW, "Artisans", 1), {"Timber", "Bricks", "Steel Beams", "Weapons"}),

    A1800Unlock("Public Mooring", DLC.VANILLA, Region.OW, {100429}, {130052},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Pier", DLC.VANILLA, Region.OW, {100519}, {100519},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Repair Crane", DLC.VANILLA, Region.OW, {1010525}, {1010525},
                POPULATION(Region.OW, "Artisans", 250), {"Timber", "Bricks", "Steel Beams"}),

    A1800Unlock("Oil Store", DLC.VANILLA, Region.OW, {100784}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, unlock_chain="Electricity"),

    A1800Unlock("Commuter Pier", DLC.VANILLA, Region.OW, {101642}, {130120},
                POPULATION(Region.OW, "Engineers", 1), {"Steel Beams", "Windows", "Reinforced Concrete"}),

    A1800Unlock("Big Betty", DLC.VANILLA, Region.OW, {1010524}, {1010524},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Advanced Weapons"}),

    A1800Unlock("Anti-Armour Gun", DLC.VANILLA, Region.OW, {3700}, {3700},
                POPULATION(Region.OW, "Engineers", 500),
                {"Bricks", "Steel Beams", "Reinforced Concrete", "Advanced Weapons"}),

    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.NW, {101290, 101293}, set(),
                SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Dirt Road", DLC.VANILLA, Region.NW, {101308}, {101308},
                SESSION_ENTER(Session.NW), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.NW, {101323}, {130095}, SESSION_ENTER(Session.NW), {"Timber"}),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.NW, {101284}, {101284},
                POPULATION(Region.NW, "Jornaleros", 50), {"Timber", "Bricks"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.NW, {101339}, {130106},
                POPULATION(Region.NW, "Jornaleros", 100), type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.NW, {101278}, {130106},
                POPULATION(Region.NW, "Jornaleros", 100), {"Timber", "Bricks"}),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.NW, {101286}, {101286},
                POPULATION(Region.NW, "Jornaleros", 100), {"Timber", "Bricks"}),

    A1800Unlock("Repair Crane", DLC.VANILLA, Region.NW, {101573}, {130122},
                POPULATION(Region.NW, "Jornaleros", 200), {"Timber", "Bricks"}),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.NW, {101563}, {130122},
                POPULATION(Region.NW, "Jornaleros", 200), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Town Hall", DLC.VANILLA, Region.NW, {101285}, {101285},
                POPULATION(Region.NW, "Obreros", 1), {"Timber", "Bricks"}),

    A1800Unlock("Pier", DLC.VANILLA, Region.NW, {101344}, {130123},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.NW, {101570}, {130123},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Public Mooring", DLC.VANILLA, Region.NW, {102284}, {102284},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}),

    A1800Unlock("Flame Tower", DLC.VANILLA, Region.NW, {632}, {632},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Oil Store", DLC.VANILLA, Region.NW, {101330}, {130124},
                POPULATION(Region.NW, "Obreros", 600), {"Timber", "Bricks"}, unlock_chain="Electricity"),

    A1800Unlock("Zoo", DLC.VANILLA, Region.NW, {102282}, {102282},
                POPULATION(Region.NW, "Obreros", 1000), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Museum", DLC.VANILLA, Region.NW, {102283}, {102283},
                POPULATION(Region.NW, "Obreros", 1500), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Anti-Armour Gun", DLC.VANILLA, Region.NW, {4797}, {4797},
                POPULATION(Region.NW, "Obreros", 1500), {"Bricks", "Steel Beams", "Advanced Weapons"}),

    # Building, Factory
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

    A1800Unlock("Potato Farm", DLC.VANILLA, Region.OW, {1010265}, {140028, 117078},
                ANY(POPULATION(Region.OW, "Farmers", 100), POPULATION(Region.AR, "Explorers", 500)),
                {"Timber"}, {"Farmers"}, set(), {"Potatoes"}, {("Schnapps", Region.OW), ("Schnapps", Region.AR)}),

    A1800Unlock("Schnapps Distillery", DLC.VANILLA, Region.OW, {1010294}, {140028, 117078},
                ANY(POPULATION(Region.OW, "Farmers", 100), POPULATION(Region.AR, "Explorers", 500)),
                {"Timber"}, {"Farmers"},
                {"Potatoes"}, {"Schnapps"}, {("Schnapps", Region.OW), ("Schnapps", Region.AR)}),

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

    A1800Unlock("Hop Farm", DLC.VANILLA, Region.OW, {1010264}, {140035, 130141},
                ANY(POPULATION(Region.OW, "Workers", 500), POPULATION(Region.NW, "Obreros", 600)),
                {"Timber"}, {"Farmers", "Settling"},
                set(), {"Hops"}, {("Beer", Region.OW), ("Beer", Region.NW)}),

    A1800Unlock("Malthouse", DLC.VANILLA, Region.OW, {1010314}, {140035, 130141},
                ANY(POPULATION(Region.OW, "Workers", 500), POPULATION(Region.NW, "Obreros", 600)),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"},
                {"Grain"}, {"Malt"}, {("Beer", Region.OW), ("Beer", Region.NW)}),

    A1800Unlock("Brewery", DLC.VANILLA, Region.OW, {1010292}, {140035, 130141},
                ANY(POPULATION(Region.OW, "Workers", 500), POPULATION(Region.NW, "Obreros", 600)),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers"},
                {"Malt", "Hops"}, {"Beer"}, {("Beer", Region.OW), ("Beer", Region.NW)}),

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

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.OW, {1010263}, {140036, 117267},
                ANY(POPULATION(Region.OW, "Artisans", 1), POPULATION(Region.AR, "Technicians", 300)),
                {"Timber"}, {"Farmers"}, set(), {"Beef"}, {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Red Pepper Farm", DLC.VANILLA, Region.OW, {100654}, {140036, 117267},
                ANY(POPULATION(Region.OW, "Artisans", 1), POPULATION(Region.AR, "Technicians", 300)),
                {"Timber"}, {"Farmers", "Settling"}, set(), {"Red Peppers"},
                {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Artisanal Kitchen", DLC.VANILLA, Region.OW, {1010293}, {140036, 117267},
                ANY(POPULATION(Region.OW, "Artisans", 1), POPULATION(Region.AR, "Technicians", 300)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Beef", "Red Peppers"}, {"Goulash"}, {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Cannery", DLC.VANILLA, Region.OW, {1010295}, {140036, 117267},
                ANY(POPULATION(Region.OW, "Artisans", 1), POPULATION(Region.AR, "Technicians", 300)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Iron", "Goulash"}, {"Canned Food"}, {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Coal Mine", DLC.VANILLA, Region.OW, {1010304}, {140032, 130134},
                POPULATION(Region.OW, "Artisans", 250),
                {"Timber", "Bricks"}, {"Workers", "Settling"},
                set(), {"Coal"}, {("Sewing Machines", Region.OW), ("Sewing Machines", Region.NW)}),

    A1800Unlock("Sewing Machine Factory", DLC.VANILLA, Region.OW, {1010284}, {140032, 130134},
                POPULATION(Region.OW, "Artisans", 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Wood", "Steel"}, {"Sewing Machines"},
                {("Sewing Machines", Region.OW), ("Sewing Machines", Region.NW)}),

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

    A1800Unlock("Limestone Quarry", DLC.VANILLA, Region.OW, {1010309}, {140043},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Workers", "Settling"},
                set(), {"Cement"}, "Reinforced Concrete"),

    A1800Unlock("Concrete Factory", DLC.VANILLA, Region.OW, {1010280}, {140043},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Engineers"},
                {"Steel", "Cement"}, {"Reinforced Concrete"}, "Reinforced Concrete"),

    A1800Unlock("Rails", DLC.VANILLA, Region.OW | Region.NW, {1010136}, {130047, 130124, 269755, 270062},
                ANY(POPULATION(Region.OW, "Engineers", 1), POPULATION(Region.NW, "Obreros", 600)),
                {"Timber", "Steel Beams"}, set(), set(), {"Railway"}, "Electricity"),

    A1800Unlock("Oil Refinery", DLC.VANILLA, Region.OW, {101331}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Workers", "Railway", "Oil Field", "Oil Harbour"}, set(), {"Oil"}, "Electricity"),

    A1800Unlock("Oil Well", DLC.VANILLA, Region.OW, {101332}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"Oil Field"}),

    A1800Unlock("Small Oil Harbour", DLC.VANILLA, Region.OW, {100783}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, "Electricity"),

    A1800Unlock("Oil Power Plant", DLC.VANILLA, Region.OW, {100780}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Engineers", "Railway", "Oil Harbour"}, {"Oil"}, {"Electricity"},
                {("Electricity", Region.OW), ("Electricity", Region.NW)}),

    A1800Unlock("Zinc Mine", DLC.VANILLA, Region.OW, {1010307}, {130041, 117740},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), {"Zinc"}, {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Copper Mine", DLC.VANILLA, Region.OW, {1010308}, {130041, 117740},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), {"Copper"}, {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Brass Smeltery", DLC.VANILLA, Region.OW, {1010282}, {130041, 117740},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers"},
                {"Zinc", "Copper"}, {"Brass"}, {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Spectacle Factory", DLC.VANILLA, Region.OW, {101250}, {130041, 117740},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Glass", "Brass"}, {"Spectacles"}, {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Bicycle Factory", DLC.VANILLA, Region.OW, {1010323}, {140040},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Caoutchouc"}, {"Penny Farthings"}, "Penny Farthings"),

    A1800Unlock("Motor Assembly Line", DLC.VANILLA, Region.OW, {1010302}, {140052},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Brass"}, {"Steam Motors"}, "Steam Motors"),

    A1800Unlock("Steam Shipyard", DLC.VANILLA, Region.OW, {1010521}, {130051},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel Beams", "Steam Motors"}, {"Sea Travel", "Oil Transport"}),

    A1800Unlock("Saltpetre Works", DLC.VANILLA, Region.OW, {1010310}, {140053},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers", "Sea Travel"}, set(), {"Saltpetre"}, "Advanced Weapons"),

    A1800Unlock("Dynamite Factory", DLC.VANILLA, Region.OW, {1010300}, {140053},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Tallow", "Saltpetre"}, {"Dynamite"}, "Advanced Weapons"),

    A1800Unlock("Heavy Weapons Factory", DLC.VANILLA, Region.OW, {1010301}, {140053},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Dynamite"}, {"Advanced Weapons"}, "Advanced Weapons"),

    A1800Unlock("Goldsmiths", DLC.VANILLA, Region.OW, {1010327}, {140042},
                POPULATION(Region.OW, "Engineers", 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Coal", "Gold Ore"}, {"Gold"}, "Pocket Watches"),

    A1800Unlock("Clockmakers", DLC.VANILLA, Region.OW, {1010324}, {140042},
                POPULATION(Region.OW, "Engineers", 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Glass", "Gold"}, {"Pocket Watches"}, "Pocket Watches"),

    A1800Unlock("Filament Factory", DLC.VANILLA, Region.OW, {1010321}, {140044},
                POPULATION(Region.OW, "Engineers", 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Coal"}, {"Filaments"}, "Light Bulbs"),

    A1800Unlock("Light Bulb Factory", DLC.VANILLA, Region.OW, {1010286}, {140044},
                POPULATION(Region.OW, "Engineers", 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Glass", "Filaments"}, {"Light Bulbs"}, "Light Bulbs"),

    A1800Unlock("Bank", DLC.VANILLA, Region.OW, {1010365}, {130049},
                POPULATION(Region.OW, "Engineers", 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), {"Bank"}),

    A1800Unlock("Vineyard", DLC.VANILLA, Region.OW, {100655}, {130055},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber"}, {"Farmers", "Settling"}, set(), {"Grapes"}, "Champagne"),

    A1800Unlock("Champagne Cellar", DLC.VANILLA, Region.OW, {100659}, {130055},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Artisans"},
                {"Glass", "Grapes"}, {"Champagne"}, "Champagne"),

    A1800Unlock("World's Fair: Foundations", DLC.VANILLA, Region.OW, {1010489}, {1010489},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Farmers"},
                {"Timber", "Cement"}, {"World's Fair: Foundations"}),

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.OW, {1010320}, {130116},
                POPULATION(Region.OW, "Investors", 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Wood"}, {"Wood Veneers"}, "Cigars"),

    A1800Unlock("Members Club", DLC.VANILLA, Region.OW, {1010364}, {130048},
                POPULATION(Region.OW, "Investors", 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), {"Members Club"}),

    A1800Unlock("World's Fair: Superstructure", DLC.VANILLA, Region.OW, {1010490}, {1010490},
                POPULATION(Region.OW, "Investors", 750),
                {"World's Fair: Foundations"}, {"Workers"},
                {"Bricks", "Steel Beams", "Reinforced Concrete"}, {"World's Fair: Superstructure"}),

    A1800Unlock("Jewellers", DLC.VANILLA, Region.OW, {1010328}, {140048},
                POPULATION(Region.OW, "Investors", 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Artisans"},
                {"Pearls", "Gold"}, {"Jewellery"}, "Jewellery"),

    A1800Unlock("World's Fair: Glazing", DLC.VANILLA, Region.OW, {101336}, {101336},
                POPULATION(Region.OW, "Investors", 1750),
                {"World's Fair: Superstructure"}, {"Artisans"},
                {"Windows", "Steam Motors", "Wood Veneers"}, {"World's Fair: Glazing"}),

    A1800Unlock("Gramophone Factory", DLC.VANILLA, Region.OW, {1010326}, {140047},
                POPULATION(Region.OW, "Investors", 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Wood Veneers", "Brass"}, {"Gramophones"}, "Gramophones"),

    A1800Unlock("World's Fair: Infrastructure", DLC.VANILLA, Region.OW, {1010491}, {1010491},
                POPULATION(Region.OW, "Investors", 3000),
                {"World's Fair: Glazing"}, {"Engineers", "Electricity"},
                {"Filaments", "Light Bulbs", "Caoutchouc"}, {"World's Fair: Infrastructure"}),

    A1800Unlock("Coachmakers", DLC.VANILLA, Region.OW, {1010289}, {140049},
                POPULATION(Region.OW, "Investors", 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Wood Veneers", "Caoutchouc"}, {"Chassis"}, "Steam Carriages"),

    A1800Unlock("Cab Assembly Line", DLC.VANILLA, Region.OW, {1010303}, {140049},
                POPULATION(Region.OW, "Investors", 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Chassis", "Steam Motors"}, {"Steam Carriages"}, "Steam Carriages"),

    A1800Unlock("World's Fair", DLC.VANILLA, Region.OW, {1010492}, {1010492},
                POPULATION(Region.OW, "Investors", 5000),
                {"World's Fair: Infrastructure"}, {"Investors", "Electricity"},
                set(), {"World's Fair: Exhibitions", "World's Fair"}),

    A1800Unlock("Lumberjack's Hut", DLC.VANILLA, Region.NW, {101260}, {130093},
                SESSION_ENTER(Session.NW), set(), {"Jornaleros"}, set(), {"Wood"}, "Timber"),

    A1800Unlock("Sawmill", DLC.VANILLA, Region.NW, {101261}, {130093},
                SESSION_ENTER(Session.NW), set(), {"Jornaleros"}, {"Wood"}, {"Timber"}, "Timber"),

    A1800Unlock("Marketplace", DLC.VANILLA, Region.NW, {101257}, {130094},
                SESSION_ENTER(Session.NW), {"Timber"}, set(), set(), {"Market"}),

    A1800Unlock("Fish Oil Factory", DLC.VANILLA, Region.NW, {101262}, {130096},
                POPULATION(Region.NW, "Jornaleros", 50),
                {"Timber"}, {"Jornaleros"}, set(), {"Fish Oil"}, "Fried Plantains"),

    A1800Unlock("Plantain Plantation", DLC.VANILLA, Region.NW, {101263}, {130096},
                POPULATION(Region.NW, "Jornaleros", 50),
                {"Timber"}, {"Jornaleros"}, set(), {"Plantains"}, "Fried Plantains"),

    A1800Unlock("Fried Plantain Kitchen", DLC.VANILLA, Region.NW, {101264}, {130096},
                POPULATION(Region.NW, "Jornaleros", 50),
                {"Timber"}, {"Jornaleros"}, {"Plantains", "Fish Oil"}, {"Fried Plantains"}, "Fried Plantains"),

    A1800Unlock("Sugar Cane Plantation", DLC.VANILLA, Region.NW, {1010329}, {140039, 500013, 127050},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber"}, {"Jornaleros"}, set(), {"Sugar Cane"},
                {("Rum", Region.NW), ("Rum", Region.OW), ("Rum (Scholars)", Region.OW)}),

    A1800Unlock("Rum Distillery", DLC.VANILLA, Region.NW, {1010340}, {140039, 500013, 127050},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber"}, {"Jornaleros"}, {"Sugar Cane", "Wood"}, {"Rum"},
                {("Rum", Region.NW), ("Rum", Region.OW), ("Rum (Scholars)", Region.OW)}),

    A1800Unlock("Sailmakers", DLC.VANILLA, Region.NW, {101265}, {130098},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber", "Bricks"}, {"Jornaleros"}, {"Cotton Fabric"}, {"Sails"}, "Sails"),

    A1800Unlock("Sailing Shipyard", DLC.VANILLA, Region.NW, {101277}, {130106},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber", "Bricks"}, {"Jornaleros"}, {"Timber", "Sails"}, {"Sea Travel"}),

    A1800Unlock("Alpaca Farm", DLC.VANILLA, Region.NW, {101272}, {130097},
                POPULATION(Region.NW, "Jornaleros", 200),
                {"Timber"}, {"Jornaleros"}, set(), {"Alpaca Wool"}, "Ponchos"),

    A1800Unlock("Poncho Darner", DLC.VANILLA, Region.NW, {101266}, {130097},
                POPULATION(Region.NW, "Jornaleros", 200),
                {"Timber"}, {"Jornaleros"}, {"Alpaca Wool"}, {"Ponchos"}, "Ponchos"),

    A1800Unlock("Fire Station", DLC.VANILLA, Region.NW, {101275}, {101275},
                POPULATION(Region.NW, "Jornaleros", 200), {"Timber"}, set(), set(), {"Fire Protection"}),

    A1800Unlock("Caoutchouc Plantation", DLC.VANILLA, Region.NW, {1010333}, {130202},
                POPULATION(Region.NW, "Jornaleros", 200), {"Timber"}, {"Jornaleros"}, set(), {"Caoutchouc"}),

    A1800Unlock("Police Station", DLC.VANILLA, Region.NW, {101274}, {101274},
                POPULATION(Region.NW, "Jornaleros", 300), {"Timber"}, set(), set(), {"Riot Control"}),

    A1800Unlock("Chapel", DLC.VANILLA, Region.NW, {101258}, {130099},
                POPULATION(Region.NW, "Jornaleros", 300), {"Timber"}, set(), set(), {"Chapel"}),

    A1800Unlock("Pearl Farm", DLC.VANILLA, Region.NW, {1010339}, {1010339},
                POPULATION(Region.NW, "Jornaleros", 300), {"Timber"}, {"Jornaleros"}, set(), {"Pearls"}),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.NW, {101267}, {130100},
                POPULATION(Region.NW, "Obreros", 1), {"Timber"}, {"Obreros"}, set(), {"Clay"}, "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.NW, {101268}, {130100},
                POPULATION(Region.NW, "Obreros", 1), {"Timber"}, {"Obreros"}, {"Clay"}, {"Bricks"}, "Bricks"),

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.NW, {101269}, {130101},
                POPULATION(Region.NW, "Obreros", 1), {"Timber"}, {"Jornaleros"}, set(), {"Beef"}, "Tortillas"),

    A1800Unlock("Corn Farm", DLC.VANILLA, Region.NW, {101270}, {130101},
                POPULATION(Region.NW, "Obreros", 1), {"Timber"}, {"Jornaleros"}, set(), {"Corn"}, "Tortillas"),

    A1800Unlock("Tortilla Maker", DLC.VANILLA, Region.NW, {101271}, {130101},
                POPULATION(Region.NW, "Obreros", 1),
                {"Timber", "Bricks"}, {"Obreros"}, {"Beef", "Corn"}, {"Tortillas"}, "Tortillas"),

    A1800Unlock("Coffee Plantation", DLC.VANILLA, Region.NW, {101251}, {130063, 130126, 117074},
                POPULATION(Region.NW, "Obreros", 300), {"Timber"}, {"Jornaleros"}, set(), {"Coffee Beans"},
                {("Coffee", Region.NW), ("Coffee", Region.OW), ("Coffee", Region.AR)}),

    A1800Unlock("Coffee Roaster", DLC.VANILLA, Region.NW, {101252}, {130063, 130126, 117074},
                POPULATION(Region.NW, "Obreros", 300),
                {"Timber", "Bricks"}, {"Obreros"}, {"Coffee Beans"}, {"Coffee"},
                {("Coffee", Region.NW), ("Coffee", Region.OW), ("Coffee", Region.AR)}),

    A1800Unlock("Boxing Arena", DLC.VANILLA, Region.NW, {101259}, {130102},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}, set(), set(), {"Boxing Arena"}),

    A1800Unlock("Gold Mine", DLC.VANILLA, Region.NW, {101311}, {101311},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}, {"Obreros"}, set(), {"Gold Ore"}),

    A1800Unlock("Felt Producer", DLC.VANILLA, Region.NW, {101415}, {130103, 120290},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks"}, {"Jornaleros"}, {"Alpaca Wool"}, {"Felt"},
                {("Bombins", Region.NW), ("Bombins", Region.OW)}),

    A1800Unlock("Bombin Weaver", DLC.VANILLA, Region.NW, {101273}, {130103, 120290},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks"}, {"Obreros"}, {"Cotton Fabric", "Felt"}, {"Bombins"},
                {("Bombins", Region.NW), ("Bombins", Region.OW)}),

    A1800Unlock("Hospital", DLC.VANILLA, Region.NW, {101276}, {101276},
                POPULATION(Region.NW, "Obreros", 600), {"Timber", "Bricks"}, set(), set(), {"Healthcare"}),

    A1800Unlock("Oil Refinery", DLC.VANILLA, Region.NW, {1010561}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Obreros", "Railway", "Oil Field", "Oil Harbour"}, set(), {"Oil"}, "Electricity"),

    A1800Unlock("Oil Well", DLC.VANILLA, Region.NW, {100524}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), {"Oil Field"}),

    A1800Unlock("Small Oil Harbour", DLC.VANILLA, Region.NW, {101329}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks"}, set(), set(), {"Oil Harbour"}, "Electricity"),

    A1800Unlock("Tobacco Plantation", DLC.VANILLA, Region.NW, {1010330}, {140045},
                POPULATION(Region.NW, "Obreros", 1000), {"Timber"}, {"Jornaleros"}, set(), {"Tobacco"},
                {("Cigars", Region.NW), ("Cigars", Region.OW)}),

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.NW, {101296}, {140045},
                POPULATION(Region.NW, "Obreros", 1000),
                {"Timber", "Bricks"}, {"Obreros"}, {"Wood"}, {"Wood Veneers"}, "Cigars"),

    A1800Unlock("Cigar Factory", DLC.VANILLA, Region.NW, {1010342}, {140045},
                POPULATION(Region.NW, "Obreros", 1000),
                {"Timber", "Bricks"}, {"Obreros"}, {"Tobacco", "Wood Veneers"}, {"Cigars"},
                {("Cigars", Region.NW), ("Cigars", Region.OW)}),

    A1800Unlock("Sugar Refinery", DLC.VANILLA, Region.NW, {1010317}, {140041, 130127},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber"}, {"Obreros"}, {"Sugar Cane"}, {"Sugar"},
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    A1800Unlock("Cocoa Plantation", DLC.VANILLA, Region.NW, {1010332}, {140041, 130127},
                POPULATION(Region.NW, "Obreros", 1500), {"Timber"}, {"Jornaleros"}, set(), {"Cocoa"},
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    A1800Unlock("Chocolate Factory", DLC.VANILLA, Region.NW, {1010341}, {140041, 130127},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber"}, {"Obreros"}, {"Sugar", "Cocoa"}, {"Chocolate"},
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    # Building, Upgrade
    A1800Unlock("Paved Street", DLC.VANILLA, Region.OW, {1010035}, {1010035},
                POPULATION(Region.OW, "Workers", 1), {"Bricks"}, previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.OW, {100516}, {130053},
                POPULATION(Region.OW, "Workers", 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.OW, {100510, 100514}, {130053},
                POPULATION(Region.OW, "Workers", 1), {"Timber", "Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.OW, {100517}, {130054},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.OW, {100511, 100515}, {130054},
                POPULATION(Region.OW, "Artisans", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Trading Post"),

    A1800Unlock("Grand Warehouse", DLC.VANILLA, Region.OW, {269869}, {269869},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Warehouse"),

    A1800Unlock("Grand Trading Post", DLC.VANILLA, Region.OW, {269867, 269879}, {269867, 269879},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Trading Post"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.OW, {101403}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.OW, {101404}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Medium Oil Harbour"),

    A1800Unlock("Paved Street", DLC.VANILLA, Region.NW, {101309}, {130100},
                POPULATION(Region.NW, "Obreros", 1), {"Bricks"}, previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.NW, {101324}, {130104},
                POPULATION(Region.NW, "Obreros", 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.NW, {101291, 101294}, {130104},
                POPULATION(Region.NW, "Obreros", 1), {"Timber", "Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.NW, {101405}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.NW, {101406}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Medium Oil Harbour"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.NW, {101325}, {130105},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber", "Bricks", "Steel Beams"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.NW, {101292, 101295}, {130105},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Trading Post"),

    # Building, Factory, Residence
    A1800Unlock("Farmer Residence", DLC.VANILLA, Region.OW, {1010343}, {1010343},
                SESSION_ENTER(Session.OW), {"Timber"}, set(), {"Market"}, {"Farmers"},
                consumption={"Market", "Fish", "Work Clothes", "Fire Protection"},
                luxury={"Schnapps", "Pub"},
                lifestyle={"Flour", "Sugar", "Jam", "Local Mail", "Regional Mail",
                           "Overseas Mail", "Soap", "Herbs", "Hibiscus Petals"}),

    A1800Unlock("Jornalero Residence", DLC.VANILLA, Region.NW, {101254}, {101254},
                SESSION_ENTER(Session.NW), {"Timber"}, set(), {"Market"}, {"Jornaleros"},
                consumption={"Market", "Fried Plantains", "Ponchos", "Fire Protection", "Riot Control"},
                luxury={"Rum", "Chapel"},
                lifestyle={"Work Clothes", "Felt", "Teff", "Local Mail",
                           "Regional Mail", "Overseas Mail", "Soccer Balls", "Beach", "Cinema"}),

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
                {"Canned Food", "Sewing Machines", "Fur Coats", "University", "Spectacles", "Coffee",
                    "Electricity", "Light Bulbs", "Fire Protection", "Riot Control", "Healthcare"},
                {"Variety Theatre", "Rum", "Penny Farthings", "Pocket Watches", "Bank"},
                {"Soap", "Chocolate", "Shampoo", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Mezcal", "Ice Cream", "Medicine"}),

    A1800Unlock("Investor Residence", DLC.VANILLA, Region.OW, {1010347}, {1010347},
                POPULATION(Region.OW, "Engineers", 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Investors"}, "", "Engineer Residence",
                {"Spectacles", "Coffee", "Electricity", "Light Bulbs", "Champagne", "Cigars",
                    "Chocolate", "Steam Carriages", "Fire Protection", "Riot Control", "Healthcare"},
                {"Penny Farthings", "Pocket Watches", "Bank", "Members Club", "Jewellery", "Gramophones"},
                {"Furs", "Bear Fur", "Tapestries", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Perfumes", "Fans", "Film Reel"}),

    A1800Unlock("Obrero Residence", DLC.VANILLA, Region.NW, {101255}, {101255},
                POPULATION(Region.NW, "Jornaleros", 200),
                {"Timber"}, set(), set(), {"Obreros"}, "", "Jornalero Residence",
                {"Market", "Fried Plantains", "Ponchos", "Tortillas", "Coffee", "Bombins",
                    "Sewing Machines", "Fire Protection", "Riot Control", "Healthcare"},
                {"Rum", "Chapel", "Boxing Arena", "Beer", "Cigars"},
                {"Spectacles", "Typewriter", "Illuminated Script", "Local Mail",
                    "Regional Mail", "Overseas Mail", "Beach", "Samba School", "Scooter"}),

    ################################################################################################################
    ### SUNKEN_TREASURES                                                                                         ###
    ################################################################################################################
    # Unlock
    A1800Unlock("Expedition: Cape Trelawney", DLC.SUNKEN_TREASURES, ALL_REGIONS, {1701000001}, set(),
                POPULATION(Region.OW, "Artisans", 700)),

    ################################################################################################################
    ### BOTANICA                                                                                                 ###
    ################################################################################################################
    # Building
    A1800Unlock("Botanical Garden", DLC.BOTANICA, Region.NW, {114141}, {114141},
                POPULATION(Region.NW, "Obreros", 1500), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    # Building, Factory
    A1800Unlock("Botanical Garden", DLC.BOTANICA, Region.OW, {110935}, {110935},
                POPULATION(Region.OW, "Engineers", 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), {"Botanical Garden"}),

    ################################################################################################################
    ### THE_PASSAGE                                                                                              ###
    ################################################################################################################
    # Meta
    A1800Unlock("Trading Post Materials and Sea Travel", DLC.THE_PASSAGE, Region.AR, set(), set(),
                TRUE, input={"Timber", "Steel Beams", "Sea Travel"}, output={"Settling"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Sky Post Materials and Air Travel", DLC.THE_PASSAGE, Region.AR, set(), set(),
                TRUE, input={"Timber", "Steel Beams", "Air Travel"}, output={"Plateau Settling"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    # Unlock
    A1800Unlock("Expedition: The Arctic", DLC.THE_PASSAGE, ALL_REGIONS, {1701000002}, set(),
                POPULATION(Region.OW, "Engineers", 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.THE_PASSAGE, Region.AR, {112659, 112865}, set(),
                SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Small Sky Trading Post", DLC.THE_PASSAGE, Region.AR, {112726}, set(),
                SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Road", DLC.THE_PASSAGE, Region.AR, {112113}, {112113},
                SESSION_ENTER(Session.AR), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.THE_PASSAGE, Region.AR, {112656}, {112716},
                SESSION_ENTER(Session.AR), {"Timber"}),

    A1800Unlock("Depot", DLC.THE_PASSAGE, Region.AR, {112670}, {112670},
                POPULATION(Region.AR, "Technicians", 1), {"Timber"}),

    A1800Unlock("Cannon Tower", DLC.THE_PASSAGE, Region.AR, {112671}, {112671},
                POPULATION(Region.AR, "Technicians", 1), {"Timber", "Steel Beams", "Weapons"}),

    A1800Unlock("Pier", DLC.THE_PASSAGE, Region.AR, {116030}, {116030},
                POPULATION(Region.AR, "Technicians", 1), {"Timber", "Steel Beams"}),

    A1800Unlock("Flame Tower", DLC.THE_PASSAGE, Region.AR, {824}, {824},
                POPULATION(Region.AR, "Technicians", 1), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Arctic Lodge", DLC.THE_PASSAGE, Region.AR, {112678}, {112678},
                POPULATION(Region.AR, "Technicians", 100), {"Timber", "Steel Beams"}),

    # Building, Factory
    A1800Unlock("Gas-Fired Power Plant", DLC.THE_PASSAGE, Region.OW, {117547}, {117562},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Arctic Gas"}, {"Electricity"}, "Electricity (Gas)"),

    A1800Unlock("Charcoal Kiln", DLC.THE_PASSAGE, Region.AR, {114705}, {112715},
                SESSION_ENTER(Session.AR), {"Timber"}, {"Explorers"}, set(), {"Coal"}, "Heater"),

    A1800Unlock("Heater", DLC.THE_PASSAGE, Region.AR, {114751}, {112715},
                SESSION_ENTER(Session.AR), {"Timber"}, set(), {"Coal"}, {"Heat"}, "Heater"),

    A1800Unlock("Lumberjack's Hut", DLC.THE_PASSAGE, Region.AR, {114703}, {112717},
                SESSION_ENTER(Session.AR), set(), {"Explorers", "Heat"}, set(), {"Wood"}, "Timber"),

    A1800Unlock("Sawmill", DLC.THE_PASSAGE, Region.AR, {114704}, {112717},
                SESSION_ENTER(Session.AR), set(), {"Explorers", "Heat"}, {"Wood"}, {"Timber"}, "Timber"),

    A1800Unlock("Canteen", DLC.THE_PASSAGE, Region.AR, {114889}, {114889},
                SESSION_ENTER(Session.AR), {"Timber"}, set(), set(), {"Canteen"}),

    A1800Unlock("Caribou Hunting Cabin", DLC.THE_PASSAGE, Region.AR, {112667}, {112718},
                POPULATION(Region.AR, "Explorers", 100),
                {"Timber"}, {"Explorers", "Heat"}, set(), {"Caribou Meat"}, "Pemmican"),

    A1800Unlock("Whaling Station", DLC.THE_PASSAGE, Region.AR, {112666}, {112718},
                POPULATION(Region.AR, "Explorers", 100),
                {"Timber"}, {"Explorers", "Heat"}, set(), {"Whale Oil"}, "Pemmican"),

    A1800Unlock("Pemmican Cookhouse", DLC.THE_PASSAGE, Region.AR, {112668}, {112718},
                POPULATION(Region.AR, "Explorers", 100),
                {"Timber"}, {"Explorers", "Heat"}, {"Caribou Meat", "Whale Oil"}, {"Pemmican"}, "Pemmican"),

    A1800Unlock("Ranger Station", DLC.THE_PASSAGE, Region.AR, {112669}, {112669},
                POPULATION(Region.AR, "Explorers", 250),
                {"Timber", "Steel Beams"}, {"Heat"}, set(), {"Fire Protection", "Healthcare"}),

    A1800Unlock("Goose Farm", DLC.THE_PASSAGE, Region.AR, {112676}, {112720},
                POPULATION(Region.AR, "Explorers", 250),
                {"Timber"}, {"Explorers", "Heat"}, set(), {"Goose Feathers"}, "Sleeping Bags"),

    A1800Unlock("Seal Hunting Docks", DLC.THE_PASSAGE, Region.AR, {112674}, {112720},
                POPULATION(Region.AR, "Explorers", 250),
                {"Timber"}, {"Explorers", "Heat"}, set(), {"Seal Skin"}, "Sleeping Bags"),

    A1800Unlock("Sleeping Bag Factory", DLC.THE_PASSAGE, Region.AR, {112675}, {112720},
                POPULATION(Region.AR, "Explorers", 250),
                {"Timber"}, {"Explorers", "Heat"}, {"Goose Feathers", "Seal Skin"}, {"Sleeping Bags"}, "Sleeping Bags"),

    A1800Unlock("Oil Lamp Factory", DLC.THE_PASSAGE, Region.AR, {112679}, {112721},
                POPULATION(Region.AR, "Explorers", 500),
                {"Timber"}, {"Explorers", "Heat"}, {"Brass", "Whale Oil"}, {"Oil Lamps"}, "Oil Lamps"),

    A1800Unlock("Arctic Airship Hangar: Foundations", DLC.THE_PASSAGE, Region.AR, {112685}, {112685},
                POPULATION(Region.AR, "Technicians", 1),
                {"Timber", "Steel Beams"}, {"Explorers", "Heat"},
                {"Timber", "Cement"}, {"Arctic Airship Hangar: Foundations"}),

    A1800Unlock("Post Office", DLC.THE_PASSAGE, Region.AR, {112684}, {112684},
                POPULATION(Region.AR, "Technicians", 100), {"Timber", "Steel Beams"}, set(), set(), {"Post Office"}),

    A1800Unlock("Arctic Airship Hangar: Structure", DLC.THE_PASSAGE, Region.AR, {112687}, {112687},
                POPULATION(Region.AR, "Technicians", 100),
                {"Arctic Airship Hangar: Foundations"}, {"Technicians", "Heat"},
                {"Steel Beams", "Reinforced Concrete"}, {"Arctic Airship Hangar: Structure"}),

    A1800Unlock("Bear Hunting Cabin", DLC.THE_PASSAGE, Region.AR, {112673}, {112719},
                POPULATION(Region.AR, "Technicians", 300),
                {"Timber"}, {"Explorers", "Heat"}, set(), {"Bear Fur"}, "Parkas"),

    A1800Unlock("Parka Factory", DLC.THE_PASSAGE, Region.AR, {112672}, {112719},
                POPULATION(Region.AR, "Technicians", 300),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, {"Seal Skin", "Bear Fur"}, {"Parkas"}, "Parkas"),

    A1800Unlock("Prime Hunting Cabin", DLC.THE_PASSAGE, Region.AR, {116034}, {116034},
                POPULATION(Region.AR, "Technicians", 300), {"Timber"}, {"Explorers", "Heat"}, set(), {"Furs"}),

    A1800Unlock("Arctic Airship Hangar: Roof", DLC.THE_PASSAGE, Region.AR, {112688}, {112688},
                POPULATION(Region.AR, "Technicians", 300),
                {"Arctic Airship Hangar: Structure"}, {"Technicians", "Heat"},
                {"Sails", "Windows", "Steam Motors"}, {"Arctic Airship Hangar: Roof"}),

    A1800Unlock("Husky Farm", DLC.THE_PASSAGE, Region.AR, {112682}, {112722},
                POPULATION(Region.AR, "Technicians", 750),
                {"Timber"}, {"Technicians", "Heat"}, set(), {"Huskies"}, "Husky Sleds"),

    A1800Unlock("Sled Frame Factory", DLC.THE_PASSAGE, Region.AR, {112681}, {112722},
                POPULATION(Region.AR, "Technicians", 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, {"Seal Skin", "Wood"}, {"Sleds"}, "Husky Sleds"),

    A1800Unlock("Husky Sled Factory", DLC.THE_PASSAGE, Region.AR, {112680}, {112722},
                POPULATION(Region.AR, "Technicians", 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"},
                {"Huskies", "Sleds"}, {"Husky Sleds"}, "Husky Sleds"),

    A1800Unlock("Deep Gold Mine", DLC.THE_PASSAGE, Region.AR, {116029}, {116029},
                POPULATION(Region.AR, "Technicians", 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, set(), {"Gold Ore"}),

    A1800Unlock("Arctic Gas Mine", DLC.THE_PASSAGE, Region.AR, {112690}, {114192, 117561},
                POPULATION(Region.AR, "Technicians", 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat", "Plateau Settling"},
                set(), {"Arctic Gas"}, "Electricity (Gas)"),

    # No arctic gas input to avoid cyclic dependency - Nate will always give you some if you have none and no Boreas
    A1800Unlock("Arctic Airship Hangar", DLC.THE_PASSAGE, Region.AR, {112689}, {112689},
                POPULATION(Region.AR, "Technicians", 750),
                {"Arctic Airship Hangar: Roof"}, {"Technicians", "Heat"},
                {"Timber", "Sails", "Steam Motors"}, {"Air Travel"}),

    # Building, Upgrade
    A1800Unlock("Medium Warehouse", DLC.THE_PASSAGE, Region.AR, {112657}, {112723},
                POPULATION(Region.AR, "Explorers", 500), {"Timber"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.THE_PASSAGE, Region.AR, {112660, 112866}, {112723},
                POPULATION(Region.AR, "Explorers", 500),
                {"Timber", "Steel Beams"}, previous_building="Small Trading Post"),

    A1800Unlock("Medium Sky Trading Post", DLC.THE_PASSAGE, Region.AR, {116003}, {112723},
                POPULATION(Region.AR, "Explorers", 500),
                {"Timber", "Steel Beams"}, previous_building="Small Sky Trading Post"),

    A1800Unlock("Large Warehouse", DLC.THE_PASSAGE, Region.AR, {112658}, {112724},
                POPULATION(Region.AR, "Technicians", 100), {"Timber"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.THE_PASSAGE, Region.AR, {112661, 112867}, {112724},
                POPULATION(Region.AR, "Technicians", 100),
                {"Timber", "Steel Beams"}, previous_building="Medium Trading Post"),

    A1800Unlock("Large Sky Trading Post", DLC.THE_PASSAGE, Region.AR, {116004}, {112724},
                POPULATION(Region.AR, "Technicians", 100),
                {"Timber", "Steel Beams", "Windows"}, previous_building="Medium Sky Trading Post"),

    # Building, Factory, Residence
    A1800Unlock("Explorer Shelter", DLC.THE_PASSAGE, Region.AR, {112091}, {112091},
                SESSION_ENTER(Session.AR), {"Timber"}, {"Heat"}, {"Canteen"}, {"Explorers"},
                consumption={"Canteen", "Pemmican", "Oil Lamps", "Fire Protection", "Healthcare"},
                luxury={"Sleeping Bags", "Schnapps"},
                lifestyle={"Bread", "Tallow", "Local Mail", "Regional Mail", "Overseas Mail", "Hot Sauce"}),

    # Building, Factory, Residence, Upgrade
    A1800Unlock("Technician Shelter", DLC.THE_PASSAGE, Region.AR, {112652}, {112652},
                POPULATION(Region.AR, "Explorers", 500),
                {"Timber"}, {"Heat"}, set(), {"Technicians"}, "", "Explorer Shelter",
                consumption={"Canteen", "Pemmican", "Oil Lamps", "Post Office",
                             "Canned Food", "Husky Sleds", "Fire Protection", "Healthcare"},
                luxury={"Sleeping Bags", "Schnapps", "Parkas", "Coffee"},
                lifestyle={"Rum", "Dynamite", "Local Mail", "Regional Mail", "Overseas Mail", "Mezcal", "Motor"}),

    ################################################################################################################
    ### SEAT_OF_POWER                                                                                            ###
    ################################################################################################################
    # Building
    A1800Unlock("Palace", DLC.SEAT_OF_POWER, Region.OW, {249947}, {249947},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}),

    ################################################################################################################
    ### BRIGHT_HARVEST                                                                                           ###
    ################################################################################################################
    # Building
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST, Region.OW, {269957, 269999}, {269957, 269999},
                POPULATION(Region.OW, "Workers", 300),
                {"Timber", "Bricks"}, {"Grain"}),
    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST, Region.OW, {269837, 269839, 269832}, {269755, 269832},
                POPULATION(Region.OW, "Engineers", 500),
                {"Steel Beams", "Steam Motors"}, {"Fuel"}),
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST, Region.NW, {269958, 269999}, {269958, 269999},
                POPULATION(Region.NW, "Obreros", 1),
                {"Timber", "Bricks"}, {"Corn"}),
    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST, Region.NW, {269848, 269849, 269832}, {270062, 269832},
                POPULATION(Region.NW, "Obreros", 600),
                {"Steel Beams", "Steam Motors"}, {"Fuel"}),

    # Building, Factory
    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST, Region.OW, {118571, 269751}, {269755},
                POPULATION(Region.OW, "Engineers", 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers"},
                {"Oil", "Railway", "Oil Harbour"}, {"Fuel"}, "Fuel"),
    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST, Region.NW, {269840, 269751}, {270062},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Obreros"},
                {"Oil", "Railway", "Oil Harbour"}, {"Fuel"}, "Fuel"),

    # Building, Upgrade
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.OW, {119259}, {119259},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Oil Harbour"),
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.NW, {119281}, {119281},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
    # Meta
    A1800Unlock("Sea Travel => Free Clipper", DLC.LAND_OF_LIONS, Region.EN, set(), set(),
                TRUE, input={"Sea Travel"}, output={"Initial Settling", "Wanza Timber"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Trading Post Materials and Sea Travel", DLC.LAND_OF_LIONS, Region.EN, set(), set(),
                TRUE, input={"Wanza Timber", "Mud Bricks", "Sea Travel"}, output={"Settling"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.EN),

    # Research Institute for infinite permits
    A1800Unlock("1500 Elders", DLC.LAND_OF_LIONS, Region.EN, set(), set(),
                TRUE, input={("Elders", Region.EN), ("Engineers", Region.OW), ("Research Institute", Region.OW)},
                output={"Permit: Scholar Residence"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.EN),

    A1800Unlock("Research: Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW, set(), set(),
                TRUE, input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Coffee Roaster"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW, set(), set(),
                TRUE, input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Rum Distillery"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW, set(), set(),
                TRUE, input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Cotton Mill"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Pier", DLC.LAND_OF_LIONS, Region.OW, set(), set(),
                TRUE, input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Pier"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    # Unlock
    A1800Unlock("Expedition: Enbesa", DLC.LAND_OF_LIONS, ALL_REGIONS, {1701000003}, set(),
                POPULATION(Region.OW, "Artisans", 100)),

    # Building
    A1800Unlock("Small Trading Post", DLC.LAND_OF_LIONS, Region.EN, {114626, 114629}, set(),
                SESSION_ENTER(Session.OW), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Small Warehouse", DLC.LAND_OF_LIONS, Region.EN, {114509}, {114509},
                SESSION_ENTER(Session.EN), {"Wanza Timber"}),

    A1800Unlock("Desert Road", DLC.LAND_OF_LIONS, Region.EN, {114523}, {114523},
                SESSION_ENTER(Session.EN), type=UnlockType.BUILDING),

    A1800Unlock("Quay", DLC.LAND_OF_LIONS, Region.EN, {117729}, {117918},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}),

    A1800Unlock("Depot", DLC.LAND_OF_LIONS, Region.EN, {117870}, {117918},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}),

    A1800Unlock("Harbourmaster's Office", DLC.LAND_OF_LIONS, Region.EN, {117860}, {117918},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}),

    A1800Unlock("Repair Crane", DLC.LAND_OF_LIONS, Region.EN, {117864}, {117918},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Mounted Guns", DLC.LAND_OF_LIONS, Region.EN, {117861}, {117918},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Trade Union", DLC.LAND_OF_LIONS, Region.EN, {117858}, {117858},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}),

    A1800Unlock("Town Hall", DLC.LAND_OF_LIONS, Region.EN, {117859}, {117859},
                POPULATION(Region.EN, "Elders", 300), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Pier", DLC.LAND_OF_LIONS, Region.EN, {117871}, {117921},
                POPULATION(Region.EN, "Elders", 1000), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Cannon Tower", DLC.LAND_OF_LIONS, Region.EN, {117863}, {117921},
                POPULATION(Region.EN, "Elders", 1000), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Flame Tower", DLC.LAND_OF_LIONS, Region.EN, {823}, {823},
                POPULATION(Region.EN, "Elders", 1000), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Anti-Armour Gun", DLC.LAND_OF_LIONS, Region.EN, {4799}, {4799},
                POPULATION(Region.EN, "Elders", 1000),
                {"Wanza Timber", "Mud Bricks", "Steel Beams", "Advanced Weapons"}),

    # Building, Factory
    A1800Unlock("Research Institute: Foundations", DLC.LAND_OF_LIONS, Region.OW, {118938}, {118938},
                POPULATION(Region.EN, "Elders", 300),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers"},
                {"Bricks", "Cement"}, {"Research Institute: Foundations"}),

    A1800Unlock("Research Institute: Superstructure", DLC.LAND_OF_LIONS, Region.OW, {118939}, {118939},
                POPULATION(Region.EN, "Elders", 300),
                {"Research Institute: Foundations"}, {"Engineers"},
                {"Steel Beams", "Windows", "Reinforced Concrete"}, {"Research Institute: Superstructure"}),

    A1800Unlock("Research Institute", DLC.LAND_OF_LIONS, Region.OW, {118940, 119392}, {118940, 119392},
                POPULATION(Region.EN, "Elders", 300),
                {"Research Institute: Superstructure"}, {"Engineers", "Electricity"}, set(), {"Research Institute"}),

    A1800Unlock("Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW, {124738}, {127612},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Coffee Roaster"},
                {"Engineers", "Electricity"}, {"Malt"}, {"Coffee"}, "Coffee (alt)"),

    A1800Unlock("Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW, {124737}, {127613},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Reinforced Concrete", "Permit: Advanced Rum Distillery"},
                {"Engineers", "Electricity"}, {"Potatoes", "Coal"}, {"Rum"}, "Rum (alt)"),

    A1800Unlock("Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW, {124739}, {127614},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Cotton Mill"},
                {"Engineers", "Electricity"}, {"Wood", "Wool"}, {"Cotton Fabric"}, "Cotton Fabric (alt)"),

    A1800Unlock("Bootmakers", DLC.LAND_OF_LIONS, Region.OW, {118733}, {118740},
                POPULATION(Region.OW, "Scholars", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Sanga Cow"}, {"Leather Boots"}, "Leather Boots"),

    A1800Unlock("Tailor's Shop", DLC.LAND_OF_LIONS, Region.OW, {118734}, {118743},
                POPULATION(Region.OW, "Scholars", 300),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Artisans"},
                {"Cotton Fabric", "Linen"}, {"Tailored Suits"}, "Tailored Suits"),

    A1800Unlock("Telephone Manufacturer", DLC.LAND_OF_LIONS, Region.OW, {118735}, {118744},
                POPULATION(Region.OW, "Scholars", 4000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Filaments", "Wood Veneers"}, {"Telephones"}, "Telephones"),

    A1800Unlock("Radio Tower", DLC.LAND_OF_LIONS, Region.OW, {118736}, {118736},
                POPULATION(Region.OW, "Scholars", 7000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), {"Radio Tower"}),

    A1800Unlock("Canal", DLC.LAND_OF_LIONS, Region.EN, {112842, 117786}, {117783},
                SESSION_ENTER(Session.EN), output={"Canal System"}, unlock_chain="Irrigation"),

    A1800Unlock("Water Pump", DLC.LAND_OF_LIONS, Region.EN, {114544}, {117783},
                SESSION_ENTER(Session.EN), {"Wanza Timber"}, {"Canal System"}, set(), {"Irrigation"}, "Irrigation"),

    A1800Unlock("Marketplace", DLC.LAND_OF_LIONS, Region.EN, {114518}, {114518},
                SESSION_ENTER(Session.EN), {"Wanza Timber"}, set(), set(), {"Market"}),

    A1800Unlock("Wanza Woodcutter", DLC.LAND_OF_LIONS, Region.EN, {122963}, {122963, 114356},
                SESSION_ENTER(Session.EN), set(), {"Shepherds"}, set(), {"Wanza Timber"}),

    A1800Unlock("Goat Farm", DLC.LAND_OF_LIONS, Region.EN, {114456}, {114456, 114371},
                POPULATION(Region.EN, "Shepherds", 50), {"Wanza Timber"}, {"Shepherds"}, set(), {"Goat Milk"}),

    A1800Unlock("Linseed Farm", DLC.LAND_OF_LIONS, Region.EN, {114448}, {114527},
                POPULATION(Region.EN, "Shepherds", 150),
                {"Wanza Timber"}, {"Shepherds", "Irrigation"}, set(), {"Linseed"}, "Finery"),

    A1800Unlock("Linen Mill", DLC.LAND_OF_LIONS, Region.EN, {114441}, {114527},
                POPULATION(Region.EN, "Shepherds", 150),
                {"Wanza Timber"}, {"Shepherds", "Irrigation"}, {"Linseed"}, {"Linen"}, "Finery"),

    A1800Unlock("Embroiderer", DLC.LAND_OF_LIONS, Region.EN, {114466}, {114527},
                POPULATION(Region.EN, "Shepherds", 150),
                {"Wanza Timber"}, {"Shepherds", "Irrigation"}, {"Linen"}, {"Finery"}, "Finery"),

    A1800Unlock("Musicians' Court", DLC.LAND_OF_LIONS, Region.EN, {114519}, {114519},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}, set(), set(), {"Musicians' Court"}),

    A1800Unlock("Fire Station", DLC.LAND_OF_LIONS, Region.EN, {119892}, {119892},
                POPULATION(Region.EN, "Shepherds", 150), {"Wanza Timber"}, {"Irrigation"}, set(), {"Fire Protection"}),

    A1800Unlock("Sanga Farm", DLC.LAND_OF_LIONS, Region.EN, {114439}, {114524},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, {"Shepherds"}, set(), {"Sanga Cow"}, "Dried Meat"),

    A1800Unlock("Salt Works", DLC.LAND_OF_LIONS, Region.EN, {114440}, {114524},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, {"Shepherds"}, set(), {"Salt"}, "Dried Meat"),

    A1800Unlock("Dry-House", DLC.LAND_OF_LIONS, Region.EN, {114444}, {114524},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, {"Shepherds"}, {"Sanga Cow", "Salt"}, {"Dried Meat"}, "Dried Meat"),

    A1800Unlock("Hibiscus Farm", DLC.LAND_OF_LIONS, Region.EN, {114447}, {114525, 120286},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, {"Shepherds", "Irrigation", "Settling"}, set(), {"Hibiscus Petals"},
                {("Hibiscus Tea", Region.EN), ("Hibiscus Tea", Region.OW)}),

    A1800Unlock("Tea Spicer", DLC.LAND_OF_LIONS, Region.EN, {114468}, {114525, 120286},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, {"Shepherds"}, {"Hibiscus Petals"}, {"Hibiscus Tea"},
                {("Hibiscus Tea", Region.EN), ("Hibiscus Tea", Region.OW)}),

    A1800Unlock("Clay Collector", DLC.LAND_OF_LIONS, Region.EN, {117743}, {114528},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber"}, {"Shepherds"}, set(), {"Clay"}, "Mud Bricks"),

    A1800Unlock("Teff Farm", DLC.LAND_OF_LIONS, Region.EN, {114450}, {114528},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber"}, {"Shepherds", "Irrigation"}, set(), {"Teff"}, "Mud Bricks"),

    A1800Unlock("Brick Dry-House", DLC.LAND_OF_LIONS, Region.EN, {114467}, {114528},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber"}, {"Elders"}, {"Clay", "Teff"}, {"Mud Bricks"}, "Mud Bricks"),

    A1800Unlock("Indigo Farm", DLC.LAND_OF_LIONS, Region.EN, {114451}, {118730},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber"}, {"Shepherds", "Irrigation", "Settling"}, set(), {"Indigo Dye"}, "Ceramics"),

    A1800Unlock("Ceramics Workshop", DLC.LAND_OF_LIONS, Region.EN, {118725}, {118730},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Clay", "Indigo Dye"}, {"Ceramics"}, "Ceramics"),

    A1800Unlock("Tapestry Looms", DLC.LAND_OF_LIONS, Region.EN, {114469}, {114530, 120288},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"},
                {"Linen", "Indigo Dye"}, {"Tapestries"}, {("Tapestries", Region.EN), ("Tapestries", Region.OW)}),

    A1800Unlock("Police Station", DLC.LAND_OF_LIONS, Region.EN, {114508}, {114508},
                POPULATION(Region.EN, "Elders", 1), {"Wanza Timber"}, set(), set(), {"Riot Control"}),

    A1800Unlock("Spice Farm", DLC.LAND_OF_LIONS, Region.EN, {114452}, {114531, 120287},
                POPULATION(Region.EN, "Elders", 300),
                {"Wanza Timber"}, {"Shepherds", "Irrigation", "Settling"}, set(), {"Spices"},
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Teff Mill", DLC.LAND_OF_LIONS, Region.EN, {114459}, {114531, 120287},
                POPULATION(Region.EN, "Elders", 300),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Teff", "Spices"}, {"Spiced Flour"},
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Lobster Fishery", DLC.LAND_OF_LIONS, Region.EN, {118729}, {114531, 120287},
                POPULATION(Region.EN, "Elders", 300),
                {"Wanza Timber", "Mud Bricks"}, {"Shepherds", "Settling"}, set(), {"Lobster"},
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Wat Kitchen", DLC.LAND_OF_LIONS, Region.EN, {114471}, {114531, 120287},
                POPULATION(Region.EN, "Elders", 300),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"},
                {"Spiced Flour", "Lobster"}, {"Seafood Stew"},
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Pipe Maker", DLC.LAND_OF_LIONS, Region.EN, {114472}, {114532, 120289},
                POPULATION(Region.EN, "Elders", 300),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Clay", "Tobacco"}, {"Clay Pipes"},
                {("Clay Pipes", Region.EN), ("Clay Pipes", Region.OW)}),

    A1800Unlock("Hospital", DLC.LAND_OF_LIONS, Region.EN, {117668}, {117668},
                POPULATION(Region.EN, "Elders", 600), {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Healthcare"}),

    A1800Unlock("Paper Mill", DLC.LAND_OF_LIONS, Region.EN, {117744}, {117719},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Wood"}, {"Paper"}, "Illuminated Script"),

    A1800Unlock("Luminer", DLC.LAND_OF_LIONS, Region.EN, {114470}, {117719},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"},
                {"Paper", "Indigo Dye"}, {"Illuminated Script"}, "Illuminated Script"),

    A1800Unlock("Apiary", DLC.LAND_OF_LIONS, Region.EN, {114453}, {117720},
                POPULATION(Region.EN, "Elders", 1000),
                {"Wanza Timber"}, {"Shepherds", "Irrigation", "Settling"}, set(), {"Beeswax"}, "Lanterns"),

    A1800Unlock("Chandler", DLC.LAND_OF_LIONS, Region.EN, {114461}, {117720},
                POPULATION(Region.EN, "Elders", 1000),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Beeswax", "Cotton"}, {"Ornate Candles"}, "Lanterns"),

    A1800Unlock("Lanternsmith", DLC.LAND_OF_LIONS, Region.EN, {114464}, {117720},
                POPULATION(Region.EN, "Elders", 1000),
                {"Wanza Timber", "Mud Bricks"}, {"Elders"}, {"Ornate Candles", "Glass"}, {"Lanterns"}, "Lanterns"),

    A1800Unlock("Monastery", DLC.LAND_OF_LIONS, Region.EN, {114520}, {114520},
                POPULATION(Region.EN, "Elders", 1000),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Monastery"}),

    # Building, Upgrade
    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.OW, {125028}, {125028},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.NW, {125191}, {125191},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Paved Street", DLC.LAND_OF_LIONS, Region.EN, {119029}, {119029},
                POPULATION(Region.EN, "Elders", 1), {"Mud Bricks"}, previous_building="Desert Road"),

    A1800Unlock("Medium Warehouse", DLC.LAND_OF_LIONS, Region.EN, {114537}, {114633},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.LAND_OF_LIONS, Region.EN, {114627, 114630}, {114633},
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.LAND_OF_LIONS, Region.EN, {114635}, {114634},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.LAND_OF_LIONS, Region.EN, {114628, 114631}, {114634},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Medium Trading Post"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.EN, {125193}, {125193},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Wanza Timber", "Mud Bricks", "Permit: Advanced Pier"}, previous_building="Pier"),

    # Building, Factory, Residence
    # University + Canned Food guarantuee enough scholars to make infinite permits
    A1800Unlock("Scholar Residence", DLC.LAND_OF_LIONS, Region.OW, {114445}, {114445},
                POPULATION(Region.EN, "Elders", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Permit: Scholar Residence"}, set(),
                {"University", "Canned Food"}, {"Scholars", "Research Points"},
                consumption={"University", "Canned Food", "Tailored Suits", "Electricity", "Seafood Stew",
                             "Telephones", "Radio Tower", "Fire Protection", "Riot Control", "Healthcare"},
                luxury={"Leather Boots", "Rum", "Bombins", "Hibiscus Tea", "Tapestries", "Clay Pipes", "Gramophones"},
                lifestyle={"Local Mail", "Regional Mail", "Overseas Mail", "Saltpeter",
                           "New World Reports", "Arctic Reports", "Film Reel", "Fans", "Scooter"}),

    A1800Unlock("Shepherd Residence", DLC.LAND_OF_LIONS, Region.EN, {114436}, {114436},
                SESSION_ENTER(Session.EN), {"Wanza Timber"}, set(), {"Market"}, {"Shepherds"},
                consumption={"Market", "Goat Milk", "Finery", "Dried Meat", "Fire Protection"},
                luxury={"Musicians' Court", "Hibiscus Tea"},
                lifestyle={"Wanza Timber", "Grain", "Ponchos", "Canned Food", "Hot Sauce", "Jam"}),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Elder Residence", DLC.LAND_OF_LIONS, Region.EN, {114437}, {114437},
                POPULATION(Region.EN, "Shepherds", 300),
                {"Wanza Timber"}, set(), set(), {"Elders"}, "", "Shepherd Residence",
                {"Market", "Goat Milk", "Finery", "Dried Meat", "Ceramics", "Seafood Stew",
                    "Illuminated Script", "Lanterns", "Fire Protection", "Riot Control", "Healthcare"},
                {"Musicians' Court", "Hibiscus Tea", "Tapestries", "Clay Pipes", "Spectacles", "Monastery"},
                {"Cotton Fabric", "Sewing Machines", "Goose Feathers", "Soap", "Herbs", "Orchid"}),

    ### Needs The Passage ###
    # Building, Upgrade
    A1800Unlock("Advanced Pier", DLC.THE_PASSAGE | DLC.LAND_OF_LIONS, Region.AR, {125192}, {125192},
                COUNTER(118940, 1, "Research Institute", "Research Institute", Region.OW),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    ### Needs Bright Harvest ###
    # Meta
    A1800Unlock("Oil Transport OW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.OW), "Oil Transport"}, output={("Oil", Region.EN)},
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.NW), "Oil Transport"}, output={("Oil", Region.EN)},
                type=UnlockType.META | UnlockType.FACTORY),

    # Building
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119025, 269999}, {119025, 269999},
                POPULATION(Region.EN, "Elders", 1), {"Wanza Timber", "Mud Bricks"}, {"Teff"}),

    A1800Unlock("Oil Store", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119034}, {270173},
                POPULATION(Region.EN, "Elders", 600), {"Wanza Timber", "Mud Bricks"}, unlock_chain="Fuel"),

    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119026, 119027, 269832},
                {270173, 269832},
                POPULATION(Region.EN, "Elders", 600), {"Steel Beams", "Steam Motors"}, {"Fuel"}),

    # Building, Factory
    A1800Unlock("Rails", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119035}, {270173},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Steel Beams"}, set(), set(), {"Railway"}, "Fuel"),

    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119028, 269751}, {270173},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Elders"},
                {"Oil", "Railway", "Oil Harbour"}, {"Fuel"}, "Fuel"),

    A1800Unlock("Small Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119031}, {270173},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Oil Harbour"}, "Fuel"),

    # Building, Factory, Upgrade
    A1800Unlock("Medium Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119032}, {119032},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Oil Harbour"}, previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119033}, {119033},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Oil Harbour"}, previous_building="Medium Oil Harbour"),

    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {270172}, {270172},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), {"Oil Harbour"}, previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### EMPIRE_OF_THE_SKIES                                                                                      ###
    ################################################################################################################

    # TODO: Meta Upgrades for Alpaca and Cattle Farms with Electricity
]


class _Unlocks:
    _initialized: bool = False

    def init(self, enabled_dlcs: DLC) -> None:
        self._apply_options(enabled_dlcs)

        for a1800_unlock in self._a1800_unlocks:
            a1800_unlock.init()

        self._a1800_unlock_locations = sorted(
            [unlock for unlock in self._a1800_unlocks if not UnlockType.META in unlock.type],
            key=lambda location: location.trigger.get_sort_key()
        )

        self._initialized = True
        self._verify_data()

    def get_unlocks(self) -> Sequence[A1800Unlock]:
        assert self._initialized, "The Anno 1800 unlocks module was used before it was initialized."
        return self._a1800_unlocks

    def find_unlocks(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Unlock]:
        assert self._initialized, "The Anno 1800 unlocks module was used before it was initialized."
        return (unlock for unlock in self._a1800_unlocks if unlock.name == name and region in unlock.region)

    def find_ap_item(self, ap_name: str) -> Optional[A1800Unlock]:
        assert self._initialized, "The Anno 1800 unlocks module was used before it was initialized."
        return next((unlock for unlock in self._a1800_unlocks if unlock.ap_item_name == ap_name), None)

    def get_unlock_locations(self) -> Sequence[A1800Unlock]:
        assert self._initialized, "The Anno 1800 unlocks module was used before it was initialized."
        return self._a1800_unlock_locations

    def _clean_dlc_trigger(self, enabled_dlcs: DLC, trigger: Trigger) -> Trigger:
        if trigger.trigger_type == TriggerType.ALL:
            trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.TRUE]

            if len(trigger.triggers) == 0:
                return TRUE
            elif len(trigger.triggers) == 1:
                return trigger.triggers[0]
            elif any([subtrigger.trigger_type == TriggerType.FALSE for subtrigger in trigger.triggers]):
                return FALSE
            else:
                return trigger
        elif trigger.trigger_type == TriggerType.ANY:
            trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.FALSE]

            if len(trigger.triggers) == 0:
                return FALSE
            elif len(trigger.triggers) == 1:
                return trigger.triggers[0]
            elif any([subtrigger.trigger_type == TriggerType.TRUE for subtrigger in trigger.triggers]):
                return TRUE
            else:
                return trigger
        elif trigger.trigger_type == TriggerType.POPULATION:
            return FALSE if not next(PRODUCTS.find_populations(trigger.population, trigger.region), None) else trigger
        elif trigger.trigger_type == TriggerType.COUNTER:
            return FALSE if not next(PRODUCTS.find_products(trigger.product_name, trigger.region), None) or \
                not len([unlock for unlock in self._a1800_unlocks
                         if unlock.name == trigger.unlock_name and trigger.region in unlock.region]) else trigger
        else:
            return trigger

    def _clean_dlc_references(self, enabled_dlcs: DLC) -> None:
        for unlock in self._a1800_unlocks:
            unlock.trigger = self._clean_dlc_trigger(enabled_dlcs, unlock.trigger)

            missing_outputs: set[str | tuple[str, Region]] = set()
            for output in unlock.output:
                name = output if isinstance(output, str) else output[0]
                region = unlock.region if isinstance(output, str) else output[1]
                if not next(PRODUCTS.find_products(name, region), None):
                    missing_outputs.add(output)
            if missing_outputs:
                unlock.output -= missing_outputs

            missing_chains: set[tuple[str, Region]] = set()
            if isinstance(unlock.unlock_chain, set):
                for chain in unlock.unlock_chain:
                    if not next(CHAINS.find_chains(chain[0], unlock.name, unlock.region, chain[1]), None):
                        missing_chains.add(chain)
                if missing_chains:
                    unlock.unlock_chain -= missing_chains

            missing_lifestyles: set[str] = set()
            for lifestyle in unlock.lifestyle:
                if not next(PRODUCTS.find_products(lifestyle, unlock.region), None):
                    missing_lifestyles.add(lifestyle)
            if missing_lifestyles:
                unlock.lifestyle -= missing_lifestyles

    def _apply_options(self, enabled_dlcs: DLC) -> None:
        global _a1800_unlocks

        self._a1800_unlocks = [unlock for unlock in _a1800_unlocks if unlock.dlc in enabled_dlcs]

        if DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES in enabled_dlcs:
            for unlock in self._a1800_unlocks:
                if unlock.name == "Post Office" and unlock.region == Region.AR:
                    unlock.maintenance.add("Explorers")
                    unlock.output.add("Local Mail")
                    break

        self._clean_dlc_references(enabled_dlcs)

    def _verify_data(self) -> None:
        # Assure all references exist
        for unlock in self._a1800_unlocks:
            assert unlock.region, f"Unlock {unlock.name} has no region"

            if unlock.trigger.trigger_type == TriggerType.POPULATION:
                assert next(PRODUCTS.find_populations(unlock.trigger.population, unlock.trigger.region), None), \
                    f"Unlock {unlock.name} trigger references non-existent population {unlock.trigger.population}, " \
                    f"{unlock.trigger.region}"

            for cost in unlock.cost:
                assert next(PRODUCTS.find_products(cost, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent cost {cost}"

            for maintenance in unlock.maintenance:
                assert next(PRODUCTS.find_products(maintenance, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent maintenance {maintenance}"

            for input in unlock.input:
                if isinstance(input, str):
                    assert next(PRODUCTS.find_products(input, unlock.region), None), \
                        f"Unlock {unlock.name} references non-existent input {input}"
                else:
                    assert next(PRODUCTS.find_products(input[0], input[1]), None), \
                        f"Unlock {unlock.name} references non-existent input {input}"

            for output in unlock.output:
                if isinstance(output, str):
                    assert next(PRODUCTS.find_products(output, unlock.region), None), \
                        f"Unlock {unlock.name} references non-existent output {output}"
                else:
                    assert next(PRODUCTS.find_products(output[0], output[1]), None), \
                        f"Unlock {unlock.name} references non-existent output {output}"

            if unlock.unlock_chain:
                if isinstance(unlock.unlock_chain, str):
                    assert next(CHAINS.find_chains(unlock.unlock_chain, unlock.name, unlock.region), None), \
                        f"Unlock {unlock.name} references non-existent chain {unlock.unlock_chain}"
                else:
                    for chain, region in unlock.unlock_chain:
                        assert next(CHAINS.find_chains(chain, unlock.name, unlock.region, region), None), \
                            f"Unlock {unlock.name} references non-existent chain {chain}"

            if unlock.previous_building:
                assert next(self.find_unlocks(unlock.previous_building, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent previous building {unlock.previous_building}"

            for consumption in unlock.consumption:
                assert next(PRODUCTS.find_products(consumption, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent consumption {consumption}"

            for luxury in unlock.luxury:
                assert next(PRODUCTS.find_products(luxury, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent luxury {luxury}"

            for lifestyle in unlock.lifestyle:
                assert next(PRODUCTS.find_products(lifestyle, unlock.region), None), \
                    f"Unlock {unlock.name} references non-existent lifestyle {lifestyle}"

        # Assure all chain references exist
        for chain in CHAINS.get_chains():
            assert chain.region, f"Chain {chain.name} has no region"

            for name, region in chain.elements:
                assert next(self.find_unlocks(name, region), None), f"Chain {chain.name} references non-existent unlock {name}, " \
                    f"{region}"

        # Assure all trigger references exist
        for unlock in self.get_unlocks():
            if unlock.trigger.trigger_type == TriggerType.POPULATION:
                population = next(PRODUCTS.find_populations(unlock.trigger.population, unlock.trigger.region), None)
                assert population, f"Population {unlock.trigger.population} referenced in {unlock.name} was filtered "\
                    "during init and no longer is available!"


UNLOCKS = _Unlocks()
