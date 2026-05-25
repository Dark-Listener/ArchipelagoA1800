from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import ClassVar, Iterator, Optional

from ._Chains import CHAINS
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, TriggerType, UnlockType
from ._Products import PRODUCTS
from ._Trigger import ANY, POPULATION, SESSION_ENTER, Trigger, TRUE


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
    A1800Unlock("Trading Post Materials and Sea Travel", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={"Timber", "Steel Beams", "Sea Travel"}, output={("Settling", Region.OW | Region.NW)},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Oil Transport OW => NW", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.OW), "Oil Transport"}, output={("Oil", Region.NW)},
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => OW", DLC.VANILLA, ALL_REGIONS, set(), set(),
                TRUE, input={("Oil", Region.NW), "Oil Transport"}, output={("Oil", Region.OW)},
                type=UnlockType.META | UnlockType.FACTORY),

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

    A1800Unlock("World's Fair: Foundations", DLC.VANILLA, Region.OW, {1010489}, {1010489},
                POPULATION(Region.OW, "Investors", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}),

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

    A1800Unlock("Zinc Mine", DLC.VANILLA, Region.OW, {1010307}, {130041},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), {"Zinc"}, "Spectacles"),

    A1800Unlock("Copper Mine", DLC.VANILLA, Region.OW, {1010308}, {130041},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), {"Copper"}, "Spectacles"),

    A1800Unlock("Brass Smeltery", DLC.VANILLA, Region.OW, {1010282}, {130041},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers"},
                {"Zinc", "Copper"}, {"Brass"}, "Spectacles"),

    A1800Unlock("Spectacle Factory", DLC.VANILLA, Region.OW, {101250}, {130041},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Glass", "Brass"}, {"Spectacles"}, "Spectacles"),

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

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.OW, {1010320}, {130116},
                POPULATION(Region.OW, "Investors", 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Wood"}, {"Wood Veneers"}, "Cigars"),

    A1800Unlock("Members Club", DLC.VANILLA, Region.OW, {1010364}, {130048},
                POPULATION(Region.OW, "Investors", 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), {"Members Club"}),

    A1800Unlock("Jewellers", DLC.VANILLA, Region.OW, {1010328}, {140048},
                POPULATION(Region.OW, "Investors", 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Artisans"},
                {"Pearls", "Gold"}, {"Jewellery"}, "Jewellery"),

    A1800Unlock("Gramophone Factory", DLC.VANILLA, Region.OW, {1010326}, {140047},
                POPULATION(Region.OW, "Investors", 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Wood Veneers", "Brass"}, {"Gramophones"}, "Gramophones"),

    A1800Unlock("Coachmakers", DLC.VANILLA, Region.OW, {1010289}, {140049},
                POPULATION(Region.OW, "Investors", 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers"},
                {"Wood Veneers", "Caoutchouc"}, {"Chassis"}, "Steam Carriages"),

    A1800Unlock("Cab Assembly Line", DLC.VANILLA, Region.OW, {1010303}, {140049},
                POPULATION(Region.OW, "Investors", 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Chassis", "Steam Motors"}, {"Steam Carriages"}, "Steam Carriages"),

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

    A1800Unlock("Sugar Cane Plantation", DLC.VANILLA, Region.NW, {1010329}, {140039, 500013},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber"}, {"Jornaleros"}, set(), {"Sugar Cane"}, {("Rum", Region.NW), ("Rum", Region.OW)}),

    A1800Unlock("Rum Distillery", DLC.VANILLA, Region.NW, {1010340}, {140039, 500013},
                POPULATION(Region.NW, "Jornaleros", 100),
                {"Timber"}, {"Jornaleros"}, {"Sugar Cane", "Wood"}, {"Rum"}, {("Rum", Region.NW), ("Rum", Region.OW)}),

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

    A1800Unlock("Coffee Plantation", DLC.VANILLA, Region.NW, {101251}, {130063, 130126},
                POPULATION(Region.NW, "Obreros", 300), {"Timber"}, {"Jornaleros"}, set(), {"Coffee Beans"},
                {("Coffee", Region.NW), ("Coffee", Region.OW)}),

    A1800Unlock("Coffee Roaster", DLC.VANILLA, Region.NW, {101252}, {130063, 130126},
                POPULATION(Region.NW, "Obreros", 300),
                {"Timber", "Bricks"}, {"Obreros"}, {"Coffee Beans"}, {"Coffee"},
                {("Coffee", Region.NW), ("Coffee", Region.OW)}),

    A1800Unlock("Boxing Arena", DLC.VANILLA, Region.NW, {101259}, {130102},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}, set(), set(), {"Boxing Arena"}),

    A1800Unlock("Gold Mine", DLC.VANILLA, Region.NW, {101311}, {101311},
                POPULATION(Region.NW, "Obreros", 300), {"Timber", "Bricks"}, {"Obreros"}, set(), {"Gold Ore"}),

    A1800Unlock("Felt Producer", DLC.VANILLA, Region.NW, {101415}, {130103},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks"}, {"Jornaleros"}, {"Alpaca Wool"}, {"Felt"}, "Bombins"),

    A1800Unlock("Bombin Weaver", DLC.VANILLA, Region.NW, {101273}, {130103},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks"}, {"Obreros"}, {"Cotton Fabric", "Felt"}, {"Bombins"}, "Bombins"),

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

    A1800Unlock("World's Fair: Superstructure", DLC.VANILLA, Region.OW, {1010490}, {1010490},
                POPULATION(Region.OW, "Investors", 750),
                {"Timber", "Cement"}, {"Farmers"}, previous_building="World's Fair: Foundations"),

    A1800Unlock("World's Fair: Glazing", DLC.VANILLA, Region.OW, {101336}, {101336},
                POPULATION(Region.OW, "Investors", 1750),
                {"Bricks", "Steel Beams", "Reinforced Concrete"}, {"Workers"},
                previous_building="World's Fair: Superstructure"),

    A1800Unlock("World's Fair: Infrastructure", DLC.VANILLA, Region.OW, {1010491}, {1010491},
                POPULATION(Region.OW, "Investors", 3000),
                {"Windows", "Steam Motors", "Wood Veneers"}, {"Artisans"}, previous_building="World's Fair: Glazing"),

    A1800Unlock("Paved Street", DLC.VANILLA, Region.NW, {101309}, {130100},
                POPULATION(Region.NW, "Obreros", 1), {"Bricks"}, previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.NW, {101324}, {130104},
                POPULATION(Region.NW, "Obreros", 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.NW, {101291, 101294}, {130104},
                POPULATION(Region.NW, "Obreros", 1), {"Timber", "Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.NW, {101325}, {130105},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber", "Bricks", "Steel Beams"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.NW, {101292, 101295}, {130105},
                POPULATION(Region.NW, "Obreros", 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Trading Post"),

    # Building, Factory, Upgrade
    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.OW, {101403}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.OW, {101404}, {130047},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Medium Oil Harbour"),

    A1800Unlock("World's Fair", DLC.VANILLA, Region.OW, {1010492}, {1010492},
                POPULATION(Region.OW, "Investors", 5000),
                {"Filaments", "Light Bulbs", "Caoutchouc"}, {"Engineers", "Electricity"}, output={"World's Fair"},
                previous_building="World's Fair: Infrastructure"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.NW, {101405}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.NW, {101406}, {130124},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Medium Oil Harbour"),

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

    # Building, Factory, Upgrade
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.OW, {119259}, {119259},
                POPULATION(Region.OW, "Engineers", 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Large Oil Harbour"),
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.NW, {119281}, {119281},
                POPULATION(Region.NW, "Obreros", 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), {"Oil Harbour"}, previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
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
                POPULATION(Region.EN, "Elders", 1),
                {"Wanza Timber", "Mud Bricks"}, {"Teff"}),
    A1800Unlock("Oil Store", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119034}, {270173},
                POPULATION(Region.EN, "Elders", 600),
                {"Wanza Timber", "Mud Bricks"}, unlock_chain="Fuel"),
    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, {119026, 119027, 269832},
                {270173, 269832},
                POPULATION(Region.EN, "Elders", 600),
                {"Steel Beams", "Steam Motors"}, {"Fuel"}),

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

    def _clean_dlc_references(self) -> None:
        for unlock in self._a1800_unlocks:
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
                    if not next(PRODUCTS.find_products(chain[0], chain[1]), None):
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

        self._clean_dlc_references()

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
