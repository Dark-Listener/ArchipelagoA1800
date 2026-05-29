from collections.abc import Sequence
from typing import ClassVar, Iterator, Optional

from ._Chains import CHAINS
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, TriggerType, UnlockType
from ._Guid import RECIPE_GUIDS
from ._Products import PRODUCTS
from ._Trigger import Trigger


def create_unlock_name(name: str, region: Region, prefix: str = "", postfix: str = "") -> str:
    if not region or region == ALL_REGIONS:
        return prefix + name + postfix
    else:
        return f"{prefix}{region.name}: {name}{postfix}"


class A1800Unlock:
    __item_id: ClassVar[int] = 1
    name: str
    dlc: DLC
    region: Region
    guids: list[int]
    unlock_guids: list[int]
    lock_guids: list[int]
    trigger: Trigger
    cost: set[str]
    maintenance: set[str]
    input: set[tuple[str, Region]]
    output: set[tuple[str, Region]]
    unlock_chain: set[tuple[str, Region]]
    previous_building: str
    consumption: set[str]
    luxury: set[str]
    lifestyle: set[str]
    type: UnlockType
    ap_region: Region
    is_early: bool
    ap_code: Optional[int] = None
    ap_item_name: str = ""
    ap_location_name: str = ""
    is_progressive: bool = False
    is_excluded: bool = False

    def __init__(
        self,
        name: str,
        dlc: DLC,
        region: Region,
        guids: int | list[int] = [],
        lock_guids: int | list[int] = [],
        trigger: Trigger = Trigger.TRUE(),
        cost: str | set[str] = set(),
        maintenance: str | set[str] = set(),
        input: str | tuple[str, Region] | set[str | tuple[str, Region]] = set(),
        output: str | tuple[str, Region] | set[str | tuple[str, Region]] = set(),
        unlock_chain: str | tuple[str, Region] | set[str | tuple[str, Region]] = set(),
        previous_building: str = "",
        consumption: str | set[str] = set(),
        luxury: str | set[str] = set(),
        lifestyle: str | set[str] = set(),
        *,
        type: UnlockType = UnlockType.UNLOCK,
        ap_region: Region = NO_REGION,
        is_early: bool = False,
        is_excluded: bool = False,
    ) -> None:
        self.name = name
        self.dlc = dlc
        self.region = region
        self.guids = list(dict.fromkeys([guids] if isinstance(guids, int) else guids))
        self.unlock_guids: list[int] = self.guids
        self.lock_guids = list(dict.fromkeys([lock_guids] if isinstance(lock_guids, int) else lock_guids))
        self.trigger = trigger
        self.cost = {cost} if isinstance(cost, str) else cost
        self.maintenance = {maintenance} if isinstance(maintenance, str) else maintenance
        self.input = {(in_val, self.region) if isinstance(in_val, str) else in_val for in_val in (
            input if isinstance(input, set) else {input})}
        self.output = {(out_val, self.region) if isinstance(out_val, str) else out_val for out_val in (
            output if isinstance(output, set) else {output})}
        self.unlock_chain = {(chain, self.region) if isinstance(chain, str) else chain for chain in (
            unlock_chain if isinstance(unlock_chain, set) else {unlock_chain})}
        self.previous_building = previous_building
        self.consumption = {consumption} if isinstance(consumption, str) else consumption
        self.luxury = {luxury} if isinstance(luxury, str) else luxury
        self.lifestyle = {lifestyle} if isinstance(lifestyle, str) else lifestyle

        self.type = type
        self.ap_region = ap_region
        self.is_early = is_early
        self.is_excluded = is_excluded

        self.ap_code = A1800Unlock.__item_id
        A1800Unlock.__item_id += 1

        self.ap_item_name = create_unlock_name(self.name, self.region)

        self.ap_location_name = self.trigger.get_ap_location_name(self.ap_item_name)

    def post_init(self) -> None:
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
            for chain, region in self.unlock_chain:
                self.unlock_guids.append(next(CHAINS.find_chains(chain, self.name, self.region, region)).guid)

        if UnlockType.FACTORY in self.type:
            for name, region in self.output:
                output_guid = next(PRODUCTS.find_products(name, region)).guid
                if output_guid:
                    self.unlock_guids.append(output_guid)

    def __str__(self) -> str:
        return f"({self.name}, {self.region})"


_a1800_unlocks: list[A1800Unlock] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    # Meta
    A1800Unlock("Starting Goods", DLC.VANILLA, Region.OW,  # Resolves circular dependency at game start
                output="Timber", type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Trading Post Materials and Sea Travel", DLC.VANILLA, ALL_REGIONS,
                input={"Timber", "Steel Beams", "Sea Travel"}, output=("Settling", Region.OW | Region.NW),
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Oil Transport OW => NW", DLC.VANILLA, ALL_REGIONS,
                input={("Oil", Region.OW), "Oil Transport"}, output=("Oil", Region.NW),
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => OW", DLC.VANILLA, ALL_REGIONS,
                input={("Oil", Region.NW), "Oil Transport"}, output=("Oil", Region.OW),
                type=UnlockType.META | UnlockType.FACTORY),

    # Unlock
    A1800Unlock("Expedition: New World", DLC.VANILLA, ALL_REGIONS, Session.NW.expedition_unlock_guid, [],
                Trigger.POPULATION("Artisans", Region.OW, 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.OW, [1010517, 1010540], [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Dirt Road", DLC.VANILLA, Region.OW, 1000178, 1000178,
                Trigger.SESSION_ENTER(Session.OW), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.OW, 1010371, 130040,
                Trigger.SESSION_ENTER(Session.OW), "Timber"),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.OW, 1010516, 1010516,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.OW, 1010522, 1010522,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.OW, 1010567, 130121,
                Trigger.POPULATION("Workers", Region.OW, 150), type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.OW, 1010519, 130121,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks"}),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.OW, 100586, 100586,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks"}),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.OW, 1010523, 1010523,
                Trigger.POPULATION("Workers", Region.OW, 300), {"Timber", "Bricks", "Steel Beams", "Weapons"}),

    A1800Unlock("Town Hall", DLC.VANILLA, Region.OW, 100415, 100415,
                Trigger.POPULATION("Artisans", Region.OW, 1), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Flame Tower", DLC.VANILLA, Region.OW, 625, 625,
                Trigger.POPULATION("Artisans", Region.OW, 1), {"Timber", "Bricks", "Steel Beams", "Weapons"}),

    A1800Unlock("Public Mooring", DLC.VANILLA, Region.OW, 100429, 130052,
                Trigger.POPULATION("Artisans", Region.OW, 250), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Pier", DLC.VANILLA, Region.OW, 100519, 100519,
                Trigger.POPULATION("Artisans", Region.OW, 250), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Repair Crane", DLC.VANILLA, Region.OW, 1010525, 1010525,
                Trigger.POPULATION("Artisans", Region.OW, 250), {"Timber", "Bricks", "Steel Beams"}),

    A1800Unlock("Oil Store", DLC.VANILLA, Region.OW, 100784, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, unlock_chain="Electricity"),

    A1800Unlock("Commuter Pier", DLC.VANILLA, Region.OW, 101642, 130120,
                Trigger.POPULATION("Engineers", Region.OW, 1), {"Steel Beams", "Windows", "Reinforced Concrete"}),

    A1800Unlock("Big Betty", DLC.VANILLA, Region.OW, 1010524, 1010524,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Advanced Weapons"}),

    A1800Unlock("Anti-Armour Gun", DLC.VANILLA, Region.OW, 3700, 3700,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Bricks", "Steel Beams", "Reinforced Concrete", "Advanced Weapons"}),

    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.NW, [101290, 101293], [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Dirt Road", DLC.VANILLA, Region.NW, 101308, 101308,
                Trigger.SESSION_ENTER(Session.NW), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.NW, 101323,
                130095, Trigger.SESSION_ENTER(Session.NW), "Timber"),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.NW, 101284, 101284,
                Trigger.POPULATION("Jornaleros", Region.NW, 50), {"Timber", "Bricks"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.NW, 101339, 130106,
                Trigger.POPULATION("Jornaleros", Region.NW, 100), type=UnlockType.BUILDING),

    A1800Unlock("Depot", DLC.VANILLA, Region.NW, 101278, 130106,
                Trigger.POPULATION("Jornaleros", Region.NW, 100), {"Timber", "Bricks"}),

    A1800Unlock("Harbourmaster's Office", DLC.VANILLA, Region.NW, 101286, 101286,
                Trigger.POPULATION("Jornaleros", Region.NW, 100), {"Timber", "Bricks"}),

    A1800Unlock("Repair Crane", DLC.VANILLA, Region.NW, 101573, 130122,
                Trigger.POPULATION("Jornaleros", Region.NW, 200), {"Timber", "Bricks"}),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.NW, 101563, 130122,
                Trigger.POPULATION("Jornaleros", Region.NW, 200), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Town Hall", DLC.VANILLA, Region.NW, 101285, 101285,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}),

    A1800Unlock("Pier", DLC.VANILLA, Region.NW, 101344, 130123,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks"}),

    A1800Unlock("Cannon Tower", DLC.VANILLA, Region.NW, 101570, 130123,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Public Mooring", DLC.VANILLA, Region.NW, 102284, 102284,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks"}),

    A1800Unlock("Flame Tower", DLC.VANILLA, Region.NW, 632, 632,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Oil Store", DLC.VANILLA, Region.NW, 101330, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks"}, unlock_chain="Electricity"),

    A1800Unlock("Zoo", DLC.VANILLA, Region.NW, 102282, 102282,
                Trigger.POPULATION("Obreros", Region.NW, 1000), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Museum", DLC.VANILLA, Region.NW, 102283, 102283,
                Trigger.POPULATION("Obreros", Region.NW, 1500), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    A1800Unlock("Anti-Armour Gun", DLC.VANILLA, Region.NW, 4797, 4797,
                Trigger.POPULATION("Obreros", Region.NW, 1500), {"Bricks", "Steel Beams", "Advanced Weapons"}),

    # Building, Factory
    A1800Unlock("Lumberjack's Hut", DLC.VANILLA, Region.OW, 1010266, 140029,
                Trigger.SESSION_ENTER(Session.OW), set(), "Farmers", set(), "Wood", "Timber"),

    A1800Unlock("Sawmill", DLC.VANILLA, Region.OW, 100451, 140029,
                Trigger.SESSION_ENTER(Session.OW), set(), "Farmers", "Wood", "Timber", "Timber"),

    A1800Unlock("Marketplace", DLC.VANILLA, Region.OW, 1010372, 130057,
                Trigger.SESSION_ENTER(Session.OW), "Timber", set(), set(), "Market"),

    A1800Unlock("Fishery", DLC.VANILLA, Region.OW, 1010278, 130056,
                Trigger.POPULATION("Farmers", Region.OW, 50), "Timber", "Farmers", set(), "Fish", "", is_early=True),

    A1800Unlock("Sheep Farm", DLC.VANILLA, Region.OW, 1010267, 130060,
                Trigger.POPULATION("Farmers", Region.OW, 100),
                "Timber", "Farmers", set(), "Wool", "Work Clothes", is_early=True),

    A1800Unlock("Framework Knitters", DLC.VANILLA, Region.OW, 1010315, 130060,
                Trigger.POPULATION("Farmers", Region.OW, 100),
                "Timber", "Farmers", "Wool", "Work Clothes", "Work Clothes", is_early=True),

    A1800Unlock("Potato Farm", DLC.VANILLA, Region.OW, 1010265, [140028, 117078],
                Trigger.ANY(Trigger.POPULATION("Farmers", Region.OW, 100),
                            Trigger.POPULATION("Explorers", Region.AR, 500)),
                "Timber", "Farmers", set(), "Potatoes", {("Schnapps", Region.OW), ("Schnapps", Region.AR)}),

    A1800Unlock("Schnapps Distillery", DLC.VANILLA, Region.OW, 1010294, [140028, 117078],
                Trigger.ANY(Trigger.POPULATION("Farmers", Region.OW, 100),
                            Trigger.POPULATION("Explorers", Region.AR, 500)),
                "Timber", "Farmers",
                "Potatoes", "Schnapps", {("Schnapps", Region.OW), ("Schnapps", Region.AR)}),

    A1800Unlock("Fire Station", DLC.VANILLA, Region.OW, 1010463, 1010463,
                Trigger.POPULATION("Farmers", Region.OW, 150), "Timber", set(), set(), "Fire Protection", is_early=True),

    A1800Unlock("Pub", DLC.VANILLA, Region.OW, 1010358, 130042,
                Trigger.POPULATION("Farmers", Region.OW, 150), "Timber", set(), set(), "Pub"),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.OW, 100416, 140031,
                Trigger.POPULATION("Workers", Region.OW, 1), "Timber", "Workers", set(), "Clay", "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.OW, 1010283, 140031,
                Trigger.POPULATION("Workers", Region.OW, 1), "Timber", "Workers", "Clay", "Bricks", "Bricks"),

    A1800Unlock("Pig Farm", DLC.VANILLA, Region.OW, 1010269, 140027,
                Trigger.POPULATION("Workers", Region.OW, 1), "Timber", "Farmers", set(), "Pigs", "Sausages"),

    A1800Unlock("Slaughterhouse", DLC.VANILLA, Region.OW, 1010316, 140027,
                Trigger.POPULATION("Workers", Region.OW, 1),
                {"Timber", "Bricks"}, "Workers", "Pigs", "Sausages", "Sausages"),

    A1800Unlock("Grain Farm", DLC.VANILLA, Region.OW, 1010262, 140033,
                Trigger.POPULATION("Workers", Region.OW, 150), "Timber", "Farmers", set(), "Grain", "Bread"),

    A1800Unlock("Flour Mill", DLC.VANILLA, Region.OW, 1010313, 140033,
                Trigger.POPULATION("Workers", Region.OW, 150),
                {"Timber", "Bricks"}, "Farmers", "Grain", "Flour", "Bread"),

    A1800Unlock("Bakery", DLC.VANILLA, Region.OW, 1010291, 140033,
                Trigger.POPULATION("Workers", Region.OW, 150),
                {"Timber", "Bricks"}, "Workers", "Flour", "Bread", "Bread"),

    A1800Unlock("Church", DLC.VANILLA, Region.OW, 1010359, 130043,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks"}, set(), set(), "Church"),

    A1800Unlock("Sailmakers", DLC.VANILLA, Region.OW, 1010288, 140050,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks"}, "Workers", "Wool", "Sails", "Sails"),

    A1800Unlock("Sailing Shipyard", DLC.VANILLA, Region.OW, 1010520, 130050,
                Trigger.POPULATION("Workers", Region.OW, 150),
                {"Timber", "Bricks"}, "Workers", {"Timber", "Sails"}, "Sea Travel"),

    A1800Unlock("Charcoal Kiln", DLC.VANILLA, Region.OW, 1010298, 140034,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks"}, "Workers", set(), "Coal", "Steel Beams"),

    A1800Unlock("Iron Mine", DLC.VANILLA, Region.OW, 1010305, 140034,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks"}, "Workers", set(), "Iron", "Steel Beams"),

    A1800Unlock("Furnace", DLC.VANILLA, Region.OW, 1010297, 140034,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks"}, "Workers", {"Iron", "Coal"}, "Steel", "Steel Beams"),

    A1800Unlock("Steelworks", DLC.VANILLA, Region.OW, 1010296, 140034,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks"}, "Workers", "Steel", "Steel Beams", "Steel Beams"),

    A1800Unlock("Rendering Works", DLC.VANILLA, Region.OW, 1010312, 140030,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks", "Steel Beams"}, "Workers", "Pigs", "Tallow", "Soap"),

    A1800Unlock("Soap Factory", DLC.VANILLA, Region.OW, 1010281, 140030,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks", "Steel Beams"}, "Workers", "Tallow", "Soap", "Soap"),

    A1800Unlock("Weapon Factory", DLC.VANILLA, Region.OW, 1010299, 140051,
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks", "Steel Beams"}, "Workers", "Steel", "Weapons", "Weapons"),

    A1800Unlock("Hop Farm", DLC.VANILLA, Region.OW, 1010264, [140035, 130141],
                Trigger.ANY(Trigger.POPULATION("Workers", Region.OW, 500),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                "Timber", {"Farmers", "Settling"},
                set(), "Hops", {("Beer", Region.OW), ("Beer", Region.NW)}),

    A1800Unlock("Malthouse", DLC.VANILLA, Region.OW, 1010314, [140035, 130141],
                Trigger.ANY(Trigger.POPULATION("Workers", Region.OW, 500),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                {"Timber", "Bricks", "Steel Beams"}, "Workers",
                "Grain", "Malt", {("Beer", Region.OW), ("Beer", Region.NW)}),

    A1800Unlock("Brewery", DLC.VANILLA, Region.OW, 1010292, [140035, 130141],
                Trigger.ANY(Trigger.POPULATION("Workers", Region.OW, 500),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                {"Timber", "Bricks", "Steel Beams"}, "Workers",
                {"Malt", "Hops"}, "Beer", {("Beer", Region.OW), ("Beer", Region.NW)}),

    A1800Unlock("Police Station", DLC.VANILLA, Region.OW, 1010462, 1010462,
                Trigger.POPULATION("Workers", Region.OW, 500),
                {"Timber", "Bricks"}, set(), set(), "Riot Control"),

    A1800Unlock("School", DLC.VANILLA, Region.OW, 1010360, 130044,
                Trigger.POPULATION("Workers", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), "School"),

    A1800Unlock("Sand Mine", DLC.VANILLA, Region.OW, 1010560, 140037,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks"}, "Workers", set(), "Quartz Sand", "Windows"),

    A1800Unlock("Glassmakers", DLC.VANILLA, Region.OW, 1010319, 140037,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams"}, "Artisans", "Quartz Sand", "Glass", "Windows"),

    A1800Unlock("Window Makers", DLC.VANILLA, Region.OW, 1010285, 140037,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams"}, "Artisans", {"Wood", "Glass"}, "Windows", "Windows"),

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.OW, 1010263, [140036, 117267],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 1),
                            Trigger.POPULATION("Technicians", Region.AR, 300)),
                "Timber", "Farmers", set(), "Beef", {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Red Pepper Farm", DLC.VANILLA, Region.OW, 100654, [140036, 117267],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 1),
                            Trigger.POPULATION("Technicians", Region.AR, 300)),
                "Timber", {"Farmers", "Settling"}, set(), "Red Peppers",
                {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Artisanal Kitchen", DLC.VANILLA, Region.OW, 1010293, [140036, 117267],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 1),
                            Trigger.POPULATION("Technicians", Region.AR, 300)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                {"Beef", "Red Peppers"}, "Goulash", {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Cannery", DLC.VANILLA, Region.OW, 1010295, [140036, 117267],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 1),
                            Trigger.POPULATION("Technicians", Region.AR, 300)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                {"Iron", "Goulash"}, "Canned Food", {("Canned Food", Region.OW), ("Canned Food", Region.AR)}),

    A1800Unlock("Coal Mine", DLC.VANILLA, Region.OW, 1010304, [140032, 130134],
                Trigger.POPULATION("Artisans", Region.OW, 250),
                {"Timber", "Bricks"}, {"Workers", "Settling"},
                set(), "Coal", {("Sewing Machines", Region.OW), ("Sewing Machines", Region.NW)}),

    A1800Unlock("Sewing Machine Factory", DLC.VANILLA, Region.OW, 1010284, [140032, 130134],
                Trigger.POPULATION("Artisans", Region.OW, 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                {"Wood", "Steel"}, "Sewing Machines",
                {("Sewing Machines", Region.OW), ("Sewing Machines", Region.NW)}),

    A1800Unlock("Variety Theatre", DLC.VANILLA, Region.OW, 1010361, 130045,
                Trigger.POPULATION("Artisans", Region.OW, 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Variety Theatre"),

    A1800Unlock("Zoo", DLC.VANILLA, Region.OW, 1010470, 1010470,
                Trigger.POPULATION("Artisans", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Zoo"),

    A1800Unlock("Hunting Cabin", DLC.VANILLA, Region.OW, 1010558, [140046, 130201],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 900),
                            Trigger.POPULATION("Jornaleros", Region.NW, 100)),
                "Timber", {"Farmers", "Settling"},
                set(), "Furs", {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Cotton Plantation", DLC.VANILLA, Region.NW, 1010331, [140046, 130201, 130098],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 900),
                            Trigger.POPULATION("Jornaleros", Region.NW, 100)),
                "Timber", "Jornaleros",
                set(), "Cotton", {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Cotton Mill", DLC.VANILLA, Region.NW, 1010318, [140046, 130201, 130098],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 900),
                            Trigger.POPULATION("Jornaleros", Region.NW, 100)),
                "Timber", "Jornaleros",
                "Cotton", "Cotton Fabric", {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Fur Dealer", DLC.VANILLA, Region.OW, 1010325, [140046, 130201],
                Trigger.ANY(Trigger.POPULATION("Artisans", Region.OW, 900),
                            Trigger.POPULATION("Jornaleros", Region.NW, 100)),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                {"Furs", "Cotton Fabric"}, "Fur Coats", {("Fur Coats", Region.OW), ("Fur Coats", Region.NW)}),

    A1800Unlock("Hospital", DLC.VANILLA, Region.OW, 1010464, 1010464,
                Trigger.POPULATION("Artisans", Region.OW, 900),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Healthcare"),

    A1800Unlock("University", DLC.VANILLA, Region.OW, 1010362, 130046,
                Trigger.POPULATION("Artisans", Region.OW, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "University"),

    A1800Unlock("Museum", DLC.VANILLA, Region.OW, 1010471, 1010471,
                Trigger.POPULATION("Artisans", Region.OW, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Museum"),

    A1800Unlock("Limestone Quarry", DLC.VANILLA, Region.OW, 1010309, 140043,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, {"Workers", "Settling"},
                set(), "Cement", "Reinforced Concrete"),

    A1800Unlock("Concrete Factory", DLC.VANILLA, Region.OW, 1010280, 140043,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Engineers",
                {"Steel", "Cement"}, "Reinforced Concrete", "Reinforced Concrete"),

    A1800Unlock("Rails", DLC.VANILLA, Region.OW | Region.NW, 1010136, [130047, 130124, 269755, 270062],
                Trigger.ANY(Trigger.POPULATION("Engineers", Region.OW, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                {"Timber", "Steel Beams"}, set(), set(), "Railway", "Electricity"),

    A1800Unlock("Oil Refinery", DLC.VANILLA, Region.OW, 101331, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Workers", "Railway", "Oil Field", "Oil Harbour"}, set(), "Oil", "Electricity"),

    A1800Unlock("Oil Well", DLC.VANILLA, Region.OW, 101332, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), "Oil Field"),

    A1800Unlock("Small Oil Harbour", DLC.VANILLA, Region.OW, 100783, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), "Oil Harbour", "Electricity"),

    A1800Unlock("Oil Power Plant", DLC.VANILLA, Region.OW, 100780, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Engineers", "Railway", "Oil Harbour"}, "Oil", "Electricity",
                {("Electricity", Region.OW), ("Electricity", Region.NW)}),

    A1800Unlock("Zinc Mine", DLC.VANILLA, Region.OW, 1010307, [130041, 117740],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), "Zinc", {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Copper Mine", DLC.VANILLA, Region.OW, 1010308, [130041, 117740],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Settling"},
                set(), "Copper", {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Brass Smeltery", DLC.VANILLA, Region.OW, 1010282, [130041, 117740],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Workers",
                {"Zinc", "Copper"}, "Brass", {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Spectacle Factory", DLC.VANILLA, Region.OW, 101250, [130041, 117740],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Glass", "Brass"}, "Spectacles", {("Spectacles", Region.OW), ("Spectacles", Region.EN)}),

    A1800Unlock("Bicycle Factory", DLC.VANILLA, Region.OW, 1010323, 140040,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Caoutchouc"}, "Penny Farthings", "Penny Farthings"),

    A1800Unlock("Motor Assembly Line", DLC.VANILLA, Region.OW, 1010302, 140052,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Brass"}, "Steam Motors", "Steam Motors"),

    A1800Unlock("Steam Shipyard", DLC.VANILLA, Region.OW, 1010521, 130051,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel Beams", "Steam Motors"}, {"Sea Travel", "Oil Transport"}),

    A1800Unlock("Saltpetre Works", DLC.VANILLA, Region.OW, 1010310, 140053,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers", "Sea Travel"}, set(), "Saltpetre", "Advanced Weapons"),

    A1800Unlock("Dynamite Factory", DLC.VANILLA, Region.OW, 1010300, 140053,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Tallow", "Saltpetre"}, "Dynamite", "Advanced Weapons"),

    A1800Unlock("Heavy Weapons Factory", DLC.VANILLA, Region.OW, 1010301, 140053,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Steel", "Dynamite"}, "Advanced Weapons", "Advanced Weapons"),

    A1800Unlock("Goldsmiths", DLC.VANILLA, Region.OW, 1010327, 140042,
                Trigger.POPULATION("Engineers", Region.OW, 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Coal", "Gold Ore"}, "Gold", "Pocket Watches"),

    A1800Unlock("Clockmakers", DLC.VANILLA, Region.OW, 1010324, 140042,
                Trigger.POPULATION("Engineers", Region.OW, 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Glass", "Gold"}, "Pocket Watches", "Pocket Watches"),

    A1800Unlock("Filament Factory", DLC.VANILLA, Region.OW, 1010321, 140044,
                Trigger.POPULATION("Engineers", Region.OW, 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                "Coal", "Filaments", "Light Bulbs"),

    A1800Unlock("Light Bulb Factory", DLC.VANILLA, Region.OW, 1010286, 140044,
                Trigger.POPULATION("Engineers", Region.OW, 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Glass", "Filaments"}, "Light Bulbs", "Light Bulbs"),

    A1800Unlock("Bank", DLC.VANILLA, Region.OW, 1010365, 130049,
                Trigger.POPULATION("Engineers", Region.OW, 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), "Bank"),

    A1800Unlock("Vineyard", DLC.VANILLA, Region.OW, 100655, 130055,
                Trigger.POPULATION("Investors", Region.OW, 1),
                "Timber", {"Farmers", "Settling"}, set(), "Grapes", "Champagne"),

    A1800Unlock("Champagne Cellar", DLC.VANILLA, Region.OW, 100659, 130055,
                Trigger.POPULATION("Investors", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Glass", "Grapes"}, "Champagne", "Champagne"),

    A1800Unlock("World's Fair: Foundations", DLC.VANILLA, Region.OW, 1010489, 1010489,
                Trigger.POPULATION("Investors", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Farmers",
                {"Timber", "Cement"}, {"World's Fair: Foundations"}),

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.OW, 1010320, 130116,
                Trigger.POPULATION("Investors", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                "Wood", "Wood Veneers", "Cigars"),

    A1800Unlock("Members Club", DLC.VANILLA, Region.OW, 1010364, 130048,
                Trigger.POPULATION("Investors", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), "Members Club"),

    A1800Unlock("World's Fair: Superstructure", DLC.VANILLA, Region.OW, 1010490, 1010490,
                Trigger.POPULATION("Investors", Region.OW, 750),
                {"World's Fair: Foundations"}, "Workers",
                {"Bricks", "Steel Beams", "Reinforced Concrete"}, {"World's Fair: Superstructure"}),

    A1800Unlock("Jewellers", DLC.VANILLA, Region.OW, 1010328, 140048,
                Trigger.POPULATION("Investors", Region.OW, 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Pearls", "Gold"}, "Jewellery", "Jewellery"),

    A1800Unlock("World's Fair: Glazing", DLC.VANILLA, Region.OW, 101336, 101336,
                Trigger.POPULATION("Investors", Region.OW, 1750),
                {"World's Fair: Superstructure"}, "Artisans",
                {"Windows", "Steam Motors", "Wood Veneers"}, {"World's Fair: Glazing"}),

    A1800Unlock("Gramophone Factory", DLC.VANILLA, Region.OW, 1010326, 140047,
                Trigger.POPULATION("Investors", Region.OW, 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Wood Veneers", "Brass"}, "Gramophones", "Gramophones"),

    A1800Unlock("World's Fair: Infrastructure", DLC.VANILLA, Region.OW, 1010491, 1010491,
                Trigger.POPULATION("Investors", Region.OW, 3000),
                {"World's Fair: Glazing"}, {"Engineers", "Electricity"},
                {"Filaments", "Light Bulbs", "Caoutchouc"}, {"World's Fair: Infrastructure"}),

    A1800Unlock("Coachmakers", DLC.VANILLA, Region.OW, 1010289, 140049,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Wood Veneers", "Caoutchouc"}, "Chassis", "Steam Carriages"),

    A1800Unlock("Cab Assembly Line", DLC.VANILLA, Region.OW, 1010303, 140049,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Chassis", "Steam Motors"}, "Steam Carriages", "Steam Carriages"),

    A1800Unlock("World's Fair", DLC.VANILLA, Region.OW, 1010492, 1010492,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"World's Fair: Infrastructure"}, {"Investors", "Electricity"},
                set(), {"World's Fair: Exhibitions", "World's Fair"}),

    A1800Unlock("Lumberjack's Hut", DLC.VANILLA, Region.NW, 101260, 130093,
                Trigger.SESSION_ENTER(Session.NW), set(), "Jornaleros", set(), "Wood", "Timber"),

    A1800Unlock("Sawmill", DLC.VANILLA, Region.NW, 101261, 130093,
                Trigger.SESSION_ENTER(Session.NW), set(), "Jornaleros", "Wood", "Timber", "Timber"),

    A1800Unlock("Marketplace", DLC.VANILLA, Region.NW, 101257, 130094,
                Trigger.SESSION_ENTER(Session.NW), "Timber", set(), set(), "Market"),

    A1800Unlock("Fish Oil Factory", DLC.VANILLA, Region.NW, 101262, 130096,
                Trigger.POPULATION("Jornaleros", Region.NW, 50),
                "Timber", "Jornaleros", set(), "Fish Oil", "Fried Plantains"),

    A1800Unlock("Plantain Plantation", DLC.VANILLA, Region.NW, 101263, 130096,
                Trigger.POPULATION("Jornaleros", Region.NW, 50),
                "Timber", "Jornaleros", set(), "Plantains", "Fried Plantains"),

    A1800Unlock("Fried Plantain Kitchen", DLC.VANILLA, Region.NW, 101264, 130096,
                Trigger.POPULATION("Jornaleros", Region.NW, 50),
                "Timber", "Jornaleros", {"Plantains", "Fish Oil"}, "Fried Plantains", "Fried Plantains"),

    A1800Unlock("Sugar Cane Plantation", DLC.VANILLA, Region.NW, 1010329, [140039, 500013, 127050],
                Trigger.POPULATION("Jornaleros", Region.NW, 100),
                "Timber", "Jornaleros", set(), "Sugar Cane",
                {("Rum", Region.NW), ("Rum", Region.OW), ("Rum (Scholars)", Region.OW)}),

    A1800Unlock("Rum Distillery", DLC.VANILLA, Region.NW, 1010340, [140039, 500013, 127050],
                Trigger.POPULATION("Jornaleros", Region.NW, 100),
                "Timber", "Jornaleros", {"Sugar Cane", "Wood"}, "Rum",
                {("Rum", Region.NW), ("Rum", Region.OW), ("Rum (Scholars)", Region.OW)}),

    A1800Unlock("Sailmakers", DLC.VANILLA, Region.NW, 101265, 130098,
                Trigger.POPULATION("Jornaleros", Region.NW, 100),
                {"Timber", "Bricks"}, "Jornaleros", "Cotton Fabric", "Sails", "Sails"),

    A1800Unlock("Sailing Shipyard", DLC.VANILLA, Region.NW, 101277, 130106,
                Trigger.POPULATION("Jornaleros", Region.NW, 100),
                {"Timber", "Bricks"}, "Jornaleros", {"Timber", "Sails"}, "Sea Travel"),

    A1800Unlock("Alpaca Farm", DLC.VANILLA, Region.NW, 101272, 130097,
                Trigger.POPULATION("Jornaleros", Region.NW, 200),
                "Timber", "Jornaleros", set(), "Alpaca Wool", "Ponchos"),

    A1800Unlock("Poncho Darner", DLC.VANILLA, Region.NW, 101266, 130097,
                Trigger.POPULATION("Jornaleros", Region.NW, 200),
                "Timber", "Jornaleros", "Alpaca Wool", "Ponchos", "Ponchos"),

    A1800Unlock("Fire Station", DLC.VANILLA, Region.NW, 101275, 101275,
                Trigger.POPULATION("Jornaleros", Region.NW, 200), "Timber", set(), set(), "Fire Protection"),

    A1800Unlock("Caoutchouc Plantation", DLC.VANILLA, Region.NW, 1010333, 130202,
                Trigger.POPULATION("Jornaleros", Region.NW, 200), "Timber", "Jornaleros", set(), "Caoutchouc"),

    A1800Unlock("Police Station", DLC.VANILLA, Region.NW, 101274, 101274,
                Trigger.POPULATION("Jornaleros", Region.NW, 300), "Timber", set(), set(), "Riot Control"),

    A1800Unlock("Chapel", DLC.VANILLA, Region.NW, 101258, 130099,
                Trigger.POPULATION("Jornaleros", Region.NW, 300), "Timber", set(), set(), "Chapel"),

    A1800Unlock("Pearl Farm", DLC.VANILLA, Region.NW, 1010339, 1010339,
                Trigger.POPULATION("Jornaleros", Region.NW, 300), "Timber", "Jornaleros", set(), "Pearls"),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.NW, 101267, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Obreros", set(), "Clay", "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.NW, 101268, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Obreros", "Clay", "Bricks", "Bricks"),

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.NW, 101269, 130101,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Jornaleros", set(), "Beef", "Tortillas"),

    A1800Unlock("Corn Farm", DLC.VANILLA, Region.NW, 101270, 130101,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Jornaleros", set(), "Corn", "Tortillas"),

    A1800Unlock("Tortilla Maker", DLC.VANILLA, Region.NW, 101271, 130101,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Timber", "Bricks"}, "Obreros", {"Beef", "Corn"}, "Tortillas", "Tortillas"),

    A1800Unlock("Coffee Plantation", DLC.VANILLA, Region.NW, 101251, [130063, 130126, 117074],
                Trigger.POPULATION("Obreros", Region.NW, 300), "Timber", "Jornaleros", set(), "Coffee Beans",
                {("Coffee", Region.NW), ("Coffee", Region.OW), ("Coffee", Region.AR)}),

    A1800Unlock("Coffee Roaster", DLC.VANILLA, Region.NW, 101252, [130063, 130126, 117074],
                Trigger.POPULATION("Obreros", Region.NW, 300),
                {"Timber", "Bricks"}, "Obreros", "Coffee Beans", "Coffee",
                {("Coffee", Region.NW), ("Coffee", Region.OW), ("Coffee", Region.AR)}),

    A1800Unlock("Boxing Arena", DLC.VANILLA, Region.NW, 101259, 130102,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks"}, set(), set(), "Boxing Arena"),

    A1800Unlock("Gold Mine", DLC.VANILLA, Region.NW, 101311, 101311,
                Trigger.POPULATION("Obreros", Region.NW, 300), {"Timber", "Bricks"}, "Obreros", set(), "Gold Ore"),

    A1800Unlock("Felt Producer", DLC.VANILLA, Region.NW, 101415, [130103, 120290],
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks"}, "Jornaleros", "Alpaca Wool", "Felt",
                {("Bombins", Region.NW), ("Bombins", Region.OW)}),

    A1800Unlock("Bombin Weaver", DLC.VANILLA, Region.NW, 101273, [130103, 120290],
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks"}, "Obreros", {"Cotton Fabric", "Felt"}, "Bombins",
                {("Bombins", Region.NW), ("Bombins", Region.OW)}),

    A1800Unlock("Hospital", DLC.VANILLA, Region.NW, 101276, 101276,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks"}, set(), set(), "Healthcare"),

    A1800Unlock("Oil Refinery", DLC.VANILLA, Region.NW, 1010561, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Obreros", "Railway", "Oil Field", "Oil Harbour"}, set(), "Oil", "Electricity"),

    A1800Unlock("Oil Well", DLC.VANILLA, Region.NW, 100524, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), "Oil Field"),

    A1800Unlock("Small Oil Harbour", DLC.VANILLA, Region.NW, 101329, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks"}, set(), set(), "Oil Harbour", "Electricity"),

    A1800Unlock("Tobacco Plantation", DLC.VANILLA, Region.NW, 1010330, 140045,
                Trigger.POPULATION("Obreros", Region.NW, 1000), "Timber", "Jornaleros", set(), "Tobacco",
                {("Cigars", Region.NW), ("Cigars", Region.OW)}),

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.NW, 101296, 140045,
                Trigger.POPULATION("Obreros", Region.NW, 1000),
                {"Timber", "Bricks"}, "Obreros", "Wood", "Wood Veneers", "Cigars"),

    A1800Unlock("Cigar Factory", DLC.VANILLA, Region.NW, 1010342, 140045,
                Trigger.POPULATION("Obreros", Region.NW, 1000),
                {"Timber", "Bricks"}, "Obreros", {"Tobacco", "Wood Veneers"}, "Cigars",
                {("Cigars", Region.NW), ("Cigars", Region.OW)}),

    A1800Unlock("Sugar Refinery", DLC.VANILLA, Region.NW, 1010317, [140041, 130127],
                Trigger.POPULATION("Obreros", Region.NW, 1500),
                "Timber", "Obreros", "Sugar Cane", "Sugar",
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    A1800Unlock("Cocoa Plantation", DLC.VANILLA, Region.NW, 1010332, [140041, 130127],
                Trigger.POPULATION("Obreros", Region.NW, 1500), "Timber", "Jornaleros", set(), "Cocoa",
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    A1800Unlock("Chocolate Factory", DLC.VANILLA, Region.NW, 1010341, [140041, 130127],
                Trigger.POPULATION("Obreros", Region.NW, 1500),
                "Timber", "Obreros", {"Sugar", "Cocoa"}, "Chocolate",
                {("Chocolate", Region.NW), ("Chocolate", Region.OW)}),

    # Building, Upgrade
    A1800Unlock("Paved Street", DLC.VANILLA, Region.OW, 1010035, 1010035,
                Trigger.POPULATION("Workers", Region.OW, 1), "Bricks", previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.OW, 100516, 130053,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.OW, [100510, 100514], 130053,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.OW, 100517, 130054,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.OW, [100511, 100515], 130054,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Trading Post"),

    A1800Unlock("Grand Warehouse", DLC.VANILLA, Region.OW, 269869, 269869,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Warehouse"),

    A1800Unlock("Grand Trading Post", DLC.VANILLA, Region.OW, [269867, 269879], [269867, 269879],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Trading Post"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.OW, 101403, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.OW, 101404, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Medium Oil Harbour"),

    A1800Unlock("Paved Street", DLC.VANILLA, Region.NW, 101309, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Bricks", previous_building="Dirt Road"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.NW, 101324, 130104,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.NW, [101291, 101294], 130104,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.NW, 101405, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.NW, 101406, 130124,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Medium Oil Harbour"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.NW, 101325, 130105,
                Trigger.POPULATION("Obreros", Region.NW, 1500),
                {"Timber", "Bricks", "Steel Beams"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.NW, [101292, 101295], 130105,
                Trigger.POPULATION("Obreros", Region.NW, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Trading Post"),

    # Building, Factory, Residence
    A1800Unlock("Farmer Residence", DLC.VANILLA, Region.OW, 1010343, 1010343,
                Trigger.SESSION_ENTER(Session.OW), "Timber", set(), "Market", "Farmers",
                consumption={"Market", "Fish", "Work Clothes", "Fire Protection"},
                luxury={"Schnapps", "Pub"},
                lifestyle={"Flour", "Sugar", "Jam", "Local Mail", "Regional Mail",
                           "Overseas Mail", "Soap", "Herbs", "Hibiscus Petals"}),

    A1800Unlock("Jornalero Residence", DLC.VANILLA, Region.NW, 101254, 101254,
                Trigger.SESSION_ENTER(Session.NW), "Timber", set(), "Market", "Jornaleros",
                consumption={"Market", "Fried Plantains", "Ponchos", "Fire Protection", "Riot Control"},
                luxury={"Rum", "Chapel"},
                lifestyle={"Work Clothes", "Felt", "Teff", "Local Mail",
                           "Regional Mail", "Overseas Mail", "Soccer Balls", "Beach", "Cinema"}),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Worker Residence", DLC.VANILLA, Region.OW, 1010344, 1010344,
                Trigger.POPULATION("Farmers", Region.OW, 100),
                "Timber", set(), set(), "Workers", "", "Farmer Residence",
                {"Market", "Fish", "Work Clothes", "Sausages", "Bread",
                    "Soap", "School", "Fire Protection", "Riot Control"},
                {"Schnapps", "Pub", "Church", "Beer"},
                {"Rum", "Penny Farthings", "Hot Sauce", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Beef", "Soccer Balls", "Clay Pipes"},
                is_early=True),

    A1800Unlock("Artisan Residence", DLC.VANILLA, Region.OW, 1010345, 1010345,
                Trigger.POPULATION("Workers", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams"}, set(), set(), "Artisans", "", "Worker Residence",
                {"Sausages", "Bread", "Soap", "School", "Canned Food", "Sewing Machines",
                    "Fur Coats", "University", "Fire Protection", "Riot Control", "Healthcare"},
                {"Church", "Beer", "Variety Theatre", "Rum"},
                {"Wool", "Clay", "Paper", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Soccer Balls", "Perfumes", "Scooter"}),

    A1800Unlock("Engineer Residence", DLC.VANILLA, Region.OW, 1010346, 1010346,
                Trigger.POPULATION("Artisans", Region.OW, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Engineers", "", "Artisan Residence",
                {"Canned Food", "Sewing Machines", "Fur Coats", "University", "Spectacles", "Coffee",
                    "Electricity", "Light Bulbs", "Fire Protection", "Riot Control", "Healthcare"},
                {"Variety Theatre", "Rum", "Penny Farthings", "Pocket Watches", "Bank"},
                {"Soap", "Chocolate", "Shampoo", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Mezcal", "Ice Cream", "Medicine"}),

    A1800Unlock("Investor Residence", DLC.VANILLA, Region.OW, 1010347, 1010347,
                Trigger.POPULATION("Engineers", Region.OW, 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(),
                set(), "Investors", "", "Engineer Residence",
                {"Spectacles", "Coffee", "Electricity", "Light Bulbs", "Champagne", "Cigars",
                    "Chocolate", "Steam Carriages", "Fire Protection", "Riot Control", "Healthcare"},
                {"Penny Farthings", "Pocket Watches", "Bank", "Members Club", "Jewellery", "Gramophones"},
                {"Furs", "Bear Fur", "Tapestries", "Local Mail", "Regional Mail",
                    "Overseas Mail", "Perfumes", "Fans", "Film Reel"}),

    A1800Unlock("Obrero Residence", DLC.VANILLA, Region.NW, 101255, 101255,
                Trigger.POPULATION("Jornaleros", Region.NW, 200),
                "Timber", set(), set(), "Obreros", "", "Jornalero Residence",
                {"Market", "Fried Plantains", "Ponchos", "Tortillas", "Coffee", "Bombins",
                    "Sewing Machines", "Fire Protection", "Riot Control", "Healthcare"},
                {"Rum", "Chapel", "Boxing Arena", "Beer", "Cigars"},
                {"Spectacles", "Typewriter", "Illuminated Script", "Local Mail",
                    "Regional Mail", "Overseas Mail", "Beach", "Samba School", "Scooter"}),

    ################################################################################################################
    ### SUNKEN_TREASURES                                                                                         ###
    ################################################################################################################
    # Unlock
    A1800Unlock("Expedition: Cape Trelawney", DLC.SUNKEN_TREASURES, ALL_REGIONS, Session.CT.expedition_unlock_guid, [],
                Trigger.POPULATION("Artisans", Region.OW, 700)),

    ################################################################################################################
    ### BOTANICA                                                                                                 ###
    ################################################################################################################
    # Building
    A1800Unlock("Botanical Garden", DLC.BOTANICA, Region.NW, 114141, 114141,
                Trigger.POPULATION("Obreros", Region.NW, 1500), {"Timber", "Bricks", "Steel Beams", "Windows"}),

    # Building, Factory
    A1800Unlock("Botanical Garden", DLC.BOTANICA, Region.OW, 110935, 110935,
                Trigger.POPULATION("Engineers", Region.OW, 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Botanical Garden"),

    ################################################################################################################
    ### THE_PASSAGE                                                                                              ###
    ################################################################################################################
    # Meta
    A1800Unlock("Trading Post Materials and Sea Travel", DLC.THE_PASSAGE, Region.AR,
                input={"Timber", "Steel Beams", "Sea Travel"}, output="Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Sky Post Materials and Air Travel", DLC.THE_PASSAGE, Region.AR,
                input={"Timber", "Steel Beams", "Air Travel"}, output="Plateau Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    # Unlock
    A1800Unlock("Expedition: The Arctic", DLC.THE_PASSAGE, ALL_REGIONS, Session.AR.expedition_unlock_guid, [],
                Trigger.POPULATION("Engineers", Region.OW, 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.THE_PASSAGE, Region.AR, [112659, 112865], [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Small Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 112726, [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Road", DLC.THE_PASSAGE, Region.AR, 112113, 112113,
                Trigger.SESSION_ENTER(Session.AR), type=UnlockType.BUILDING),

    A1800Unlock("Small Warehouse", DLC.THE_PASSAGE, Region.AR, 112656, 112716,
                Trigger.SESSION_ENTER(Session.AR), "Timber"),

    A1800Unlock("Depot", DLC.THE_PASSAGE, Region.AR, 112670, 112670,
                Trigger.POPULATION("Technicians", Region.AR, 1), "Timber"),

    A1800Unlock("Cannon Tower", DLC.THE_PASSAGE, Region.AR, 112671, 112671,
                Trigger.POPULATION("Technicians", Region.AR, 1), {"Timber", "Steel Beams", "Weapons"}),

    A1800Unlock("Pier", DLC.THE_PASSAGE, Region.AR, 116030, 116030,
                Trigger.POPULATION("Technicians", Region.AR, 1), {"Timber", "Steel Beams"}),

    A1800Unlock("Flame Tower", DLC.THE_PASSAGE, Region.AR, 824, 824,
                Trigger.POPULATION("Technicians", Region.AR, 1), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Arctic Lodge", DLC.THE_PASSAGE, Region.AR, 112678, 112678,
                Trigger.POPULATION("Technicians", Region.AR, 100), {"Timber", "Steel Beams"}),

    # Building, Factory
    A1800Unlock("Gas-Fired Power Plant", DLC.THE_PASSAGE, Region.OW, 117547, 117562,
                Trigger.POPULATION("Investors", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                "Arctic Gas", "Electricity", "Electricity (Gas)"),

    A1800Unlock("Charcoal Kiln", DLC.THE_PASSAGE, Region.AR, 114705, 112715,
                Trigger.SESSION_ENTER(Session.AR), "Timber", "Explorers", set(), "Coal", "Heater"),

    A1800Unlock("Heater", DLC.THE_PASSAGE, Region.AR, 114751, 112715,
                Trigger.SESSION_ENTER(Session.AR), "Timber", set(), "Coal", "Heat", "Heater"),

    A1800Unlock("Lumberjack's Hut", DLC.THE_PASSAGE, Region.AR, 114703, 112717,
                Trigger.SESSION_ENTER(Session.AR), set(), {"Explorers", "Heat"}, set(), "Wood", "Timber"),

    A1800Unlock("Sawmill", DLC.THE_PASSAGE, Region.AR, 114704, 112717,
                Trigger.SESSION_ENTER(Session.AR), set(), {"Explorers", "Heat"}, "Wood", "Timber", "Timber"),

    A1800Unlock("Canteen", DLC.THE_PASSAGE, Region.AR, 114889, 114889,
                Trigger.SESSION_ENTER(Session.AR), "Timber", set(), set(), "Canteen"),

    A1800Unlock("Caribou Hunting Cabin", DLC.THE_PASSAGE, Region.AR, 112667, 112718,
                Trigger.POPULATION("Explorers", Region.AR, 100),
                "Timber", {"Explorers", "Heat"}, set(), "Caribou Meat", "Pemmican"),

    A1800Unlock("Whaling Station", DLC.THE_PASSAGE, Region.AR, 112666, 112718,
                Trigger.POPULATION("Explorers", Region.AR, 100),
                "Timber", {"Explorers", "Heat"}, set(), "Whale Oil", "Pemmican"),

    A1800Unlock("Pemmican Cookhouse", DLC.THE_PASSAGE, Region.AR, 112668, 112718,
                Trigger.POPULATION("Explorers", Region.AR, 100),
                "Timber", {"Explorers", "Heat"}, {"Caribou Meat", "Whale Oil"}, "Pemmican", "Pemmican"),

    A1800Unlock("Ranger Station", DLC.THE_PASSAGE, Region.AR, 112669, 112669,
                Trigger.POPULATION("Explorers", Region.AR, 250),
                {"Timber", "Steel Beams"}, "Heat", set(), {"Fire Protection", "Healthcare"}),

    A1800Unlock("Goose Farm", DLC.THE_PASSAGE, Region.AR, 112676, 112720,
                Trigger.POPULATION("Explorers", Region.AR, 250),
                "Timber", {"Explorers", "Heat"}, set(), "Goose Feathers", "Sleeping Bags"),

    A1800Unlock("Seal Hunting Docks", DLC.THE_PASSAGE, Region.AR, 112674, 112720,
                Trigger.POPULATION("Explorers", Region.AR, 250),
                "Timber", {"Explorers", "Heat"}, set(), "Seal Skin", "Sleeping Bags"),

    A1800Unlock("Sleeping Bag Factory", DLC.THE_PASSAGE, Region.AR, 112675, 112720,
                Trigger.POPULATION("Explorers", Region.AR, 250),
                "Timber", {"Explorers", "Heat"}, {"Goose Feathers", "Seal Skin"}, "Sleeping Bags", "Sleeping Bags"),

    A1800Unlock("Oil Lamp Factory", DLC.THE_PASSAGE, Region.AR, 112679, 112721,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                "Timber", {"Explorers", "Heat"}, {"Brass", "Whale Oil"}, "Oil Lamps", "Oil Lamps"),

    A1800Unlock("Arctic Airship Hangar: Foundations", DLC.THE_PASSAGE, Region.AR, 112685, 112685,
                Trigger.POPULATION("Technicians", Region.AR, 1),
                {"Timber", "Steel Beams"}, {"Explorers", "Heat"},
                {"Timber", "Cement"}, {"Arctic Airship Hangar: Foundations"}),

    A1800Unlock("Post Office", DLC.THE_PASSAGE, Region.AR, 112684, 112684,
                Trigger.POPULATION("Technicians", Region.AR, 100), {"Timber", "Steel Beams"}, set(), set(), "Post Office"),

    A1800Unlock("Arctic Airship Hangar: Structure", DLC.THE_PASSAGE, Region.AR, 112687, 112687,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                {"Arctic Airship Hangar: Foundations"}, {"Technicians", "Heat"},
                {"Steel Beams", "Reinforced Concrete"}, {"Arctic Airship Hangar: Structure"}),

    A1800Unlock("Bear Hunting Cabin", DLC.THE_PASSAGE, Region.AR, 112673, 112719,
                Trigger.POPULATION("Technicians", Region.AR, 300),
                "Timber", {"Explorers", "Heat"}, set(), "Bear Fur", "Parkas"),

    A1800Unlock("Parka Factory", DLC.THE_PASSAGE, Region.AR, 112672, 112719,
                Trigger.POPULATION("Technicians", Region.AR, 300),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, {"Seal Skin", "Bear Fur"}, "Parkas", "Parkas"),

    A1800Unlock("Prime Hunting Cabin", DLC.THE_PASSAGE, Region.AR, 116034, 116034,
                Trigger.POPULATION("Technicians", Region.AR, 300), "Timber", {"Explorers", "Heat"}, set(), "Furs"),

    A1800Unlock("Arctic Airship Hangar: Roof", DLC.THE_PASSAGE, Region.AR, 112688, 112688,
                Trigger.POPULATION("Technicians", Region.AR, 300),
                {"Arctic Airship Hangar: Structure"}, {"Technicians", "Heat"},
                {"Sails", "Windows", "Steam Motors"}, {"Arctic Airship Hangar: Roof"}),

    A1800Unlock("Husky Farm", DLC.THE_PASSAGE, Region.AR, 112682, 112722,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                "Timber", {"Technicians", "Heat"}, set(), "Huskies", "Husky Sleds"),

    A1800Unlock("Sled Frame Factory", DLC.THE_PASSAGE, Region.AR, 112681, 112722,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, {"Seal Skin", "Wood"}, "Sleds", "Husky Sleds"),

    A1800Unlock("Husky Sled Factory", DLC.THE_PASSAGE, Region.AR, 112680, 112722,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"},
                {"Huskies", "Sleds"}, "Husky Sleds", "Husky Sleds"),

    A1800Unlock("Deep Gold Mine", DLC.THE_PASSAGE, Region.AR, 116029, 116029,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat"}, set(), "Gold Ore"),

    A1800Unlock("Arctic Gas Mine", DLC.THE_PASSAGE, Region.AR, 112690, [114192, 117561],
                Trigger.POPULATION("Technicians", Region.AR, 750),
                {"Timber", "Steel Beams"}, {"Technicians", "Heat", "Plateau Settling"},
                set(), "Arctic Gas", "Electricity (Gas)"),

    # No arctic gas input to avoid cyclic dependency - Nate will always give you some if you have none and no Boreas
    A1800Unlock("Arctic Airship Hangar", DLC.THE_PASSAGE, Region.AR, 112689, 112689,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                {"Arctic Airship Hangar: Roof"}, {"Technicians", "Heat"},
                {"Timber", "Sails", "Steam Motors"}, "Air Travel"),

    # Building, Upgrade
    A1800Unlock("Medium Warehouse", DLC.THE_PASSAGE, Region.AR, 112657, 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500), "Timber", previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.THE_PASSAGE, Region.AR, [112660, 112866], 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                {"Timber", "Steel Beams"}, previous_building="Small Trading Post"),

    A1800Unlock("Medium Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 116003, 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                {"Timber", "Steel Beams"}, previous_building="Small Sky Trading Post"),

    A1800Unlock("Large Warehouse", DLC.THE_PASSAGE, Region.AR, 112658, 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100), "Timber", previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.THE_PASSAGE, Region.AR, [112661, 112867], 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                {"Timber", "Steel Beams"}, previous_building="Medium Trading Post"),

    A1800Unlock("Large Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 116004, 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                {"Timber", "Steel Beams", "Windows"}, previous_building="Medium Sky Trading Post"),

    # Building, Factory, Residence
    A1800Unlock("Explorer Shelter", DLC.THE_PASSAGE, Region.AR, 112091, 112091,
                Trigger.SESSION_ENTER(Session.AR), "Timber", "Heat", "Canteen", "Explorers",
                consumption={"Canteen", "Pemmican", "Oil Lamps", "Fire Protection", "Healthcare"},
                luxury={"Sleeping Bags", "Schnapps"},
                lifestyle={"Bread", "Tallow", "Local Mail", "Regional Mail", "Overseas Mail", "Hot Sauce"}),

    # Building, Factory, Residence, Upgrade
    A1800Unlock("Technician Shelter", DLC.THE_PASSAGE, Region.AR, 112652, 112652,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                "Timber", "Heat", set(), "Technicians", "", "Explorer Shelter",
                consumption={"Canteen", "Pemmican", "Oil Lamps", "Post Office",
                             "Canned Food", "Husky Sleds", "Fire Protection", "Healthcare"},
                luxury={"Sleeping Bags", "Schnapps", "Parkas", "Coffee"},
                lifestyle={"Rum", "Dynamite", "Local Mail", "Regional Mail", "Overseas Mail", "Mezcal", "Motor"}),

    ################################################################################################################
    ### SEAT_OF_POWER                                                                                            ###
    ################################################################################################################
    # Building
    A1800Unlock("Palace", DLC.SEAT_OF_POWER, Region.OW, 249947, 249947,
                Trigger.POPULATION("Investors", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}),

    ################################################################################################################
    ### BRIGHT_HARVEST                                                                                           ###
    ################################################################################################################
    # Building
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST, Region.OW, [269957, 269999], [269957, 269999],
                Trigger.POPULATION("Workers", Region.OW, 300),
                {"Timber", "Bricks"}, "Grain"),
    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST, Region.OW, [269837, 269839, 269832], [269755, 269832],
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Steel Beams", "Steam Motors"}, "Fuel"),
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST, Region.NW, [269958, 269999], [269958, 269999],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Timber", "Bricks"}, "Corn"),
    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST, Region.NW, [269848, 269849, 269832], [270062, 269832],
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Steel Beams", "Steam Motors"}, "Fuel"),

    # Building, Factory
    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST, Region.OW, [118571, 269751], 269755,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Workers",
                {"Oil", "Railway", "Oil Harbour"}, "Fuel", "Fuel"),
    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST, Region.NW, [269840, 269751], 270062,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Obreros",
                {"Oil", "Railway", "Oil Harbour"}, "Fuel", "Fuel"),

    # Building, Upgrade
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.OW, 119259, 119259,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Oil Harbour"),
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.NW, 119281, 119281,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
    # Meta
    A1800Unlock("Sea Travel => Free Clipper", DLC.LAND_OF_LIONS, Region.EN,
                input="Sea Travel", output={"Initial Settling", "Wanza Timber"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Trading Post Materials and Sea Travel", DLC.LAND_OF_LIONS, Region.EN,
                input={"Wanza Timber", "Mud Bricks", "Sea Travel"}, output="Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.EN),

    # Research Institute, Engineers for infinite permits
    A1800Unlock("1500 Elders", DLC.LAND_OF_LIONS, Region.EN,
                input={("Elders", Region.EN), ("Engineers", Region.OW), ("Research Institute", Region.OW)},
                output={"Permit: Scholar Residence"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.EN),

    A1800Unlock("Research: Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Coffee Roaster"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Rum Distillery"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Cotton Mill"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Research: Advanced Pier", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research Institute", "Research Points"},
                output={"Permit: Advanced Pier"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    # Unlock
    A1800Unlock("Expedition: Enbesa", DLC.LAND_OF_LIONS, ALL_REGIONS, Session.EN.expedition_unlock_guid, [],
                Trigger.POPULATION("Artisans", Region.OW, 100)),

    # Building
    A1800Unlock("Small Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114626, 114629], [],
                Trigger.SESSION_ENTER(Session.OW), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Small Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114509, 114509,
                Trigger.SESSION_ENTER(Session.EN), "Wanza Timber"),

    A1800Unlock("Desert Road", DLC.LAND_OF_LIONS, Region.EN, 114523, 114523,
                Trigger.SESSION_ENTER(Session.EN), type=UnlockType.BUILDING),

    A1800Unlock("Quay", DLC.LAND_OF_LIONS, Region.EN, 117729, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber"),

    A1800Unlock("Depot", DLC.LAND_OF_LIONS, Region.EN, 117870, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber"),

    A1800Unlock("Harbourmaster's Office", DLC.LAND_OF_LIONS, Region.EN, 117860, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber"),

    A1800Unlock("Repair Crane", DLC.LAND_OF_LIONS, Region.EN, 117864, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Mounted Guns", DLC.LAND_OF_LIONS, Region.EN, 117861, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Trade Union", DLC.LAND_OF_LIONS, Region.EN, 117858, 117858,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber"),

    A1800Unlock("Town Hall", DLC.LAND_OF_LIONS, Region.EN, 117859, 117859,
                Trigger.POPULATION("Elders", Region.EN, 300), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Pier", DLC.LAND_OF_LIONS, Region.EN, 117871, 117921,
                Trigger.POPULATION("Elders", Region.EN, 1000), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Cannon Tower", DLC.LAND_OF_LIONS, Region.EN, 117863, 117921,
                Trigger.POPULATION("Elders", Region.EN, 1000), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Flame Tower", DLC.LAND_OF_LIONS, Region.EN, 823, 823,
                Trigger.POPULATION("Elders", Region.EN, 1000), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    A1800Unlock("Anti-Armour Gun", DLC.LAND_OF_LIONS, Region.EN, 4799, 4799,
                Trigger.POPULATION("Elders", Region.EN, 1000),
                {"Wanza Timber", "Mud Bricks", "Steel Beams", "Advanced Weapons"}),

    # Building, Factory
    A1800Unlock("Research Institute: Foundations", DLC.LAND_OF_LIONS, Region.OW, 118938, 118938,
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Workers",
                {"Bricks", "Cement"}, {"Research Institute: Foundations"}),

    A1800Unlock("Research Institute: Superstructure", DLC.LAND_OF_LIONS, Region.OW, 118939, 118939,
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Research Institute: Foundations"}, "Engineers",
                {"Steel Beams", "Windows", "Reinforced Concrete"}, {"Research Institute: Superstructure"}),

    A1800Unlock("Research Institute", DLC.LAND_OF_LIONS, Region.OW, [118940, 119392], [118940, 119392],
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Research Institute: Superstructure"}, {"Engineers", "Electricity"}, set(), "Research Institute"),

    A1800Unlock("Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW, 124738, 127612,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Coffee Roaster"},
                {"Engineers", "Electricity"}, "Malt", "Coffee", "Coffee (alt)"),

    A1800Unlock("Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW, 124737, 127613,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Reinforced Concrete", "Permit: Advanced Rum Distillery"},
                {"Engineers", "Electricity"}, {"Potatoes", "Coal"}, "Rum", "Rum (alt)"),

    A1800Unlock("Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW, 124739, 127614,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Cotton Mill"},
                {"Engineers", "Electricity"}, {"Wood", "Wool"}, "Cotton Fabric", "Cotton Fabric (alt)"),

    A1800Unlock("Bootmakers", DLC.LAND_OF_LIONS, Region.OW, 118733, 118740,
                Trigger.POPULATION("Scholars", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                "Sanga Cow", "Leather Boots", "Leather Boots"),

    A1800Unlock("Tailor's Shop", DLC.LAND_OF_LIONS, Region.OW, 118734, 118743,
                Trigger.POPULATION("Scholars", Region.OW, 300),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artisans",
                {"Cotton Fabric", "Linen"}, "Tailored Suits", "Tailored Suits"),

    A1800Unlock("Telephone Manufacturer", DLC.LAND_OF_LIONS, Region.OW, 118735, 118744,
                Trigger.POPULATION("Scholars", Region.OW, 4000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Filaments", "Wood Veneers"}, "Telephones", "Telephones"),

    A1800Unlock("Radio Tower", DLC.LAND_OF_LIONS, Region.OW, 118736, 118736,
                Trigger.POPULATION("Scholars", Region.OW, 7000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, set(), set(), "Radio Tower"),

    A1800Unlock("Canal", DLC.LAND_OF_LIONS, Region.EN, [112842, 117786], 117783,
                Trigger.SESSION_ENTER(Session.EN), output="Canal System", unlock_chain="Irrigation"),

    A1800Unlock("Water Pump", DLC.LAND_OF_LIONS, Region.EN, 114544, 117783,
                Trigger.SESSION_ENTER(Session.EN), "Wanza Timber", "Canal System", set(), "Irrigation", "Irrigation"),

    A1800Unlock("Marketplace", DLC.LAND_OF_LIONS, Region.EN, 114518, 114518,
                Trigger.SESSION_ENTER(Session.EN), "Wanza Timber", set(), set(), "Market"),

    A1800Unlock("Wanza Woodcutter", DLC.LAND_OF_LIONS, Region.EN, 122963, [122963, 114356],
                Trigger.SESSION_ENTER(Session.EN), set(), "Shepherds", set(), "Wanza Timber"),

    A1800Unlock("Goat Farm", DLC.LAND_OF_LIONS, Region.EN, 114456, [114456, 114371],
                Trigger.POPULATION("Shepherds", Region.EN, 50), "Wanza Timber", "Shepherds", set(), "Goat Milk"),

    A1800Unlock("Linseed Farm", DLC.LAND_OF_LIONS, Region.EN, 114448, 114527,
                Trigger.POPULATION("Shepherds", Region.EN, 150),
                "Wanza Timber", {"Shepherds", "Irrigation"}, set(), "Linseed", "Finery"),

    A1800Unlock("Linen Mill", DLC.LAND_OF_LIONS, Region.EN, 114441, 114527,
                Trigger.POPULATION("Shepherds", Region.EN, 150),
                "Wanza Timber", {"Shepherds", "Irrigation"}, "Linseed", "Linen", "Finery"),

    A1800Unlock("Embroiderer", DLC.LAND_OF_LIONS, Region.EN, 114466, 114527,
                Trigger.POPULATION("Shepherds", Region.EN, 150),
                "Wanza Timber", {"Shepherds", "Irrigation"}, "Linen", "Finery", "Finery"),

    A1800Unlock("Musicians' Court", DLC.LAND_OF_LIONS, Region.EN, 114519, 114519,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber", set(), set(), {"Musicians' Court"}),

    A1800Unlock("Fire Station", DLC.LAND_OF_LIONS, Region.EN, 119892, 119892,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber", "Irrigation", set(), "Fire Protection"),

    A1800Unlock("Sanga Farm", DLC.LAND_OF_LIONS, Region.EN, 114439, 114524,
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", "Shepherds", set(), "Sanga Cow", "Dried Meat"),

    A1800Unlock("Salt Works", DLC.LAND_OF_LIONS, Region.EN, 114440, 114524,
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", "Shepherds", set(), "Salt", "Dried Meat"),

    A1800Unlock("Dry-House", DLC.LAND_OF_LIONS, Region.EN, 114444, 114524,
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", "Shepherds", {"Sanga Cow", "Salt"}, "Dried Meat", "Dried Meat"),

    A1800Unlock("Hibiscus Farm", DLC.LAND_OF_LIONS, Region.EN, 114447, [114525, 120286],
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", {"Shepherds", "Irrigation", "Settling"}, set(), "Hibiscus Petals",
                {("Hibiscus Tea", Region.EN), ("Hibiscus Tea", Region.OW)}),

    A1800Unlock("Tea Spicer", DLC.LAND_OF_LIONS, Region.EN, 114468, [114525, 120286],
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", "Shepherds", "Hibiscus Petals", "Hibiscus Tea",
                {("Hibiscus Tea", Region.EN), ("Hibiscus Tea", Region.OW)}),

    A1800Unlock("Clay Collector", DLC.LAND_OF_LIONS, Region.EN, 117743, 114528,
                Trigger.POPULATION("Elders", Region.EN, 1),
                "Wanza Timber", "Shepherds", set(), "Clay", "Mud Bricks"),

    A1800Unlock("Teff Farm", DLC.LAND_OF_LIONS, Region.EN, 114450, 114528,
                Trigger.POPULATION("Elders", Region.EN, 1),
                "Wanza Timber", {"Shepherds", "Irrigation"}, set(), "Teff", "Mud Bricks"),

    A1800Unlock("Brick Dry-House", DLC.LAND_OF_LIONS, Region.EN, 114467, 114528,
                Trigger.POPULATION("Elders", Region.EN, 1),
                "Wanza Timber", "Elders", {"Clay", "Teff"}, "Mud Bricks", "Mud Bricks"),

    A1800Unlock("Indigo Farm", DLC.LAND_OF_LIONS, Region.EN, 114451, 118730,
                Trigger.POPULATION("Elders", Region.EN, 1),
                "Wanza Timber", {"Shepherds", "Irrigation", "Settling"}, set(), "Indigo Dye", "Ceramics"),

    A1800Unlock("Ceramics Workshop", DLC.LAND_OF_LIONS, Region.EN, 118725, 118730,
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, "Elders", {"Clay", "Indigo Dye"}, "Ceramics", "Ceramics"),

    A1800Unlock("Tapestry Looms", DLC.LAND_OF_LIONS, Region.EN, 114469, [114530, 120288],
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, "Elders",
                {"Linen", "Indigo Dye"}, "Tapestries", {("Tapestries", Region.EN), ("Tapestries", Region.OW)}),

    A1800Unlock("Police Station", DLC.LAND_OF_LIONS, Region.EN, 114508, 114508,
                Trigger.POPULATION("Elders", Region.EN, 1), "Wanza Timber", set(), set(), "Riot Control"),

    A1800Unlock("Spice Farm", DLC.LAND_OF_LIONS, Region.EN, 114452, [114531, 120287],
                Trigger.POPULATION("Elders", Region.EN, 300),
                "Wanza Timber", {"Shepherds", "Irrigation", "Settling"}, set(), "Spices",
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Teff Mill", DLC.LAND_OF_LIONS, Region.EN, 114459, [114531, 120287],
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Wanza Timber", "Mud Bricks"}, "Elders", {"Teff", "Spices"}, "Spiced Flour",
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Lobster Fishery", DLC.LAND_OF_LIONS, Region.EN, 118729, [114531, 120287],
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Wanza Timber", "Mud Bricks"}, {"Shepherds", "Settling"}, set(), "Lobster",
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Wat Kitchen", DLC.LAND_OF_LIONS, Region.EN, 114471, [114531, 120287],
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Wanza Timber", "Mud Bricks"}, "Elders",
                {"Spiced Flour", "Lobster"}, "Seafood Stew",
                {("Seafood Stew", Region.EN), ("Seafood Stew", Region.OW)}),

    A1800Unlock("Pipe Maker", DLC.LAND_OF_LIONS, Region.EN, 114472, [114532, 120289],
                Trigger.POPULATION("Elders", Region.EN, 300),
                {"Wanza Timber", "Mud Bricks"}, "Elders", {"Clay", "Tobacco"}, "Clay Pipes",
                {("Clay Pipes", Region.EN), ("Clay Pipes", Region.OW)}),

    A1800Unlock("Hospital", DLC.LAND_OF_LIONS, Region.EN, 117668, 117668,
                Trigger.POPULATION("Elders", Region.EN, 600), {"Wanza Timber", "Mud Bricks"}, set(), set(), "Healthcare"),

    A1800Unlock("Paper Mill", DLC.LAND_OF_LIONS, Region.EN, 117744, 117719,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, "Elders", "Wood", "Paper", "Illuminated Script"),

    A1800Unlock("Luminer", DLC.LAND_OF_LIONS, Region.EN, 114470, 117719,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, "Elders",
                {"Paper", "Indigo Dye"}, "Illuminated Script", "Illuminated Script"),

    A1800Unlock("Apiary", DLC.LAND_OF_LIONS, Region.EN, 114453, 117720,
                Trigger.POPULATION("Elders", Region.EN, 1000),
                "Wanza Timber", {"Shepherds", "Irrigation", "Settling"}, set(), "Beeswax", "Lanterns"),

    A1800Unlock("Chandler", DLC.LAND_OF_LIONS, Region.EN, 114461, 117720,
                Trigger.POPULATION("Elders", Region.EN, 1000),
                {"Wanza Timber", "Mud Bricks"}, "Elders", {"Beeswax", "Cotton"}, "Ornate Candles", "Lanterns"),

    A1800Unlock("Lanternsmith", DLC.LAND_OF_LIONS, Region.EN, 114464, 117720,
                Trigger.POPULATION("Elders", Region.EN, 1000),
                {"Wanza Timber", "Mud Bricks"}, "Elders", {"Ornate Candles", "Glass"}, "Lanterns", "Lanterns"),

    A1800Unlock("Monastery", DLC.LAND_OF_LIONS, Region.EN, 114520, 114520,
                Trigger.POPULATION("Elders", Region.EN, 1000),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), "Monastery"),

    # Building, Upgrade
    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.OW, 125028, 125028,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.NW, 125191, 125191,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Paved Street", DLC.LAND_OF_LIONS, Region.EN, 119029, 119029,
                Trigger.POPULATION("Elders", Region.EN, 1), "Mud Bricks", previous_building="Desert Road"),

    A1800Unlock("Medium Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114537, 114633,
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Medium Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114627, 114630], 114633,
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Small Trading Post"),

    A1800Unlock("Large Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114635, 114634,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Medium Warehouse"),

    A1800Unlock("Large Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114628, 114631], 114634,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Medium Trading Post"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.EN, 125193, 125193,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Wanza Timber", "Mud Bricks", "Permit: Advanced Pier"}, previous_building="Pier"),

    # Building, Factory, Residence
    # University + Canned Food guarantuee enough scholars to make infinite permits
    A1800Unlock("Scholar Residence", DLC.LAND_OF_LIONS, Region.OW, 114445, 114445,
                Trigger.POPULATION("Elders", Region.EN, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Permit: Scholar Residence"}, set(),
                {"University", "Canned Food"}, {"Scholars", "Research Points"},
                consumption={"University", "Canned Food", "Tailored Suits", "Electricity", "Seafood Stew",
                             "Telephones", "Radio Tower", "Fire Protection", "Riot Control", "Healthcare"},
                luxury={"Leather Boots", "Rum", "Bombins", "Hibiscus Tea", "Tapestries", "Clay Pipes", "Gramophones"},
                lifestyle={"Local Mail", "Regional Mail", "Overseas Mail", "Saltpeter",
                           "New World Reports", "Arctic Reports", "Film Reel", "Fans", "Scooter"}),

    A1800Unlock("Shepherd Residence", DLC.LAND_OF_LIONS, Region.EN, 114436, 114436,
                Trigger.SESSION_ENTER(Session.EN), "Wanza Timber", set(), "Market", "Shepherds",
                consumption={"Market", "Goat Milk", "Finery", "Dried Meat", "Fire Protection"},
                luxury={"Musicians' Court", "Hibiscus Tea"},
                lifestyle={"Wanza Timber", "Grain", "Ponchos", "Canned Food", "Hot Sauce", "Jam"}),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Elder Residence", DLC.LAND_OF_LIONS, Region.EN, 114437, 114437,
                Trigger.POPULATION("Shepherds", Region.EN, 300),
                "Wanza Timber", set(), set(), "Elders", "", "Shepherd Residence",
                {"Market", "Goat Milk", "Finery", "Dried Meat", "Ceramics", "Seafood Stew",
                    "Illuminated Script", "Lanterns", "Fire Protection", "Riot Control", "Healthcare"},
                {"Musicians' Court", "Hibiscus Tea", "Tapestries", "Clay Pipes", "Spectacles", "Monastery"},
                {"Cotton Fabric", "Sewing Machines", "Goose Feathers", "Soap", "Herbs", "Orchid"}),

    ### Needs The Passage ###
    # Building, Upgrade
    A1800Unlock("Advanced Pier", DLC.THE_PASSAGE | DLC.LAND_OF_LIONS, Region.AR, 125192, 125192,
                Trigger.COUNTER("Research Institute", "Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    ### Needs Bright Harvest ###
    # Meta
    A1800Unlock("Oil Transport OW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, ALL_REGIONS,
                input={("Oil", Region.OW), "Oil Transport"}, output=("Oil", Region.EN),
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, ALL_REGIONS,
                input={("Oil", Region.NW), "Oil Transport"}, output=("Oil", Region.EN),
                type=UnlockType.META | UnlockType.FACTORY),

    # Building
    A1800Unlock("Silo", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, [119025, 269999], [119025, 269999],
                Trigger.POPULATION("Elders", Region.EN, 1), {"Wanza Timber", "Mud Bricks"}, "Teff"),

    A1800Unlock("Oil Store", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119034, 270173,
                Trigger.POPULATION("Elders", Region.EN, 600), {"Wanza Timber", "Mud Bricks"}, unlock_chain="Fuel"),

    A1800Unlock("Tractor Barn", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, [119026, 119027, 269832],
                [270173, 269832],
                Trigger.POPULATION("Elders", Region.EN, 600), {"Steel Beams", "Steam Motors"}, "Fuel"),

    # Building, Factory
    A1800Unlock("Rails", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119035, 270173,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Steel Beams"}, set(), set(), "Railway", "Fuel"),

    A1800Unlock("Fuel Station", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, [119028, 269751], 270173,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Elders",
                {"Oil", "Railway", "Oil Harbour"}, "Fuel", "Fuel"),

    A1800Unlock("Small Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119031, 270173,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), "Oil Harbour", "Fuel"),

    # Building, Factory, Upgrade
    A1800Unlock("Medium Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119032, 119032,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), "Oil Harbour", previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119033, 119033,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), "Oil Harbour", previous_building="Medium Oil Harbour"),

    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 270172, 270172,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, set(), set(), "Oil Harbour", previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### DOCKLANDS                                                                                                ###
    ################################################################################################################
    # Building, Factory
    A1800Unlock("Docklands Main Wharf", DLC.DOCKLANDS, Region.OW, 601470, 601470,
                Trigger.POPULATION("Artisans", Region.OW, 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, output=set[str | tuple[str, Region]]({"Docklands"}) | {
                    # Tattershire Farms
                    "Potatoes", "Pigs", "Grain", "Wood", "Beeswax", "Corn", "Red Peppers", "Sanga Cow", "Beef",
                    "Caribou Meat", "Hops", "Malt", "Goose Feather", "Spices"
                } | {
                    # FEEDL
                    "Fish", "Schnapps", "Sausages", "Bread", "Goulash", "Beer", "Seafood Stew", "Canned Food", "Rum",
                    "Champagne"
                } | {
                    # Chanteuse
                    "Work Clothes", "Soap", "Fur Coats", "Tailored Suits", "Glasses", "Leather Boots", "Bombins",
                    "Jewellery"
                } | {
                    # Qinsa Mining
                    "Coal", "Iron", "Clay", "Quartz Sand", "Cement", "Zinc", "Copper", "Gold Ore", "Steel", "Brass",
                    "Pearls", "Gold"
                } | {
                    # Old Levant & Co.
                    "Tortillas", "Plantains", "Fried Plantains", "Chocolate", "Hibiscus Tea", "Tobacco", "Coffee",
                    "Clay Pipes", "Cigars"
                } | {
                    # KITEA
                    "Glass", "Wool", "Timber", "Linen", "Felt", "Furs", "Tapestries", "Cotton Fabric", "Wood Veneers",
                    "Sewing Machines"
                } | {
                    # The Promise Trust
                    "Saltpetre", "Dynamite", "Tallow", "Filaments", "Caoutchouc", "Light Bulbs"
                } | {
                    # Ganymedia
                    "Penny Farthings", "Pocket Watches", "Gramophones", "Telephones", "Steam Carriages"
                }),


    ################################################################################################################
    ### TOURIST_SEASON                                                                                           ###
    ################################################################################################################
    # Building, Factory
    A1800Unlock("Bus Stop", DLC.TOURIST_SEASON, Region.OW, 601326, 601326,
                Trigger.COUNTER("Tourist Mooring", "Tourist Mooring", Region.OW, 1),
                "Steel Beams", set(), set(), "Public Transport"),

    A1800Unlock("Restaurant", DLC.TOURIST_SEASON, Region.OW, 132780, 132780,
                Trigger.POPULATION("Tourists", Region.OW, 250),
                {"Timber", "Bricks"}, set(), set(), {"Restaurant (Blank)"}),

    A1800Unlock("Restaurant: Archduke's Schnitzel", DLC.TOURIST_SEASON, Region.OW,
                [132747, RECIPE_GUIDS["Recipe: Archduke's Schnitzel"][0]], [132747],
                Trigger.UNLOCK("Restaurant", Region.OW),
                set(), {"Tourists", "Restaurant (Blank)"}, {"Pigs", "Potatoes", "Tallow"}, "Restaurant"),

    A1800Unlock("Restaurant: Stroggof Goulash", DLC.TOURIST_SEASON, Region.OW,
                [132750, RECIPE_GUIDS["Recipe: Stroggof Goulash"][0]], [132750],
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", "Restaurant (Blank)", Region.OW, 1, 135069),
                               Trigger.COUNTER_GOOD_IN_REGION("Corn", ALL_REGIONS, 1, Region.OW)),
                set(), {"Tourists", "Restaurant (Blank)"}, {"Beef", "Red Peppers", "Corn"}, "Restaurant"),

    A1800Unlock("Restaurant: Fish and Frites", DLC.TOURIST_SEASON, Region.OW,
                [133339, RECIPE_GUIDS["Recipe: Fish and Frites"][0]], [133339],
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", "Restaurant (Blank)", Region.OW, 1, 135069),
                               Trigger.COUNTER("Orchard: Citrus", "Citrus", Region.NW, 1)),
                set(), {"Tourists", "Restaurant (Blank)"}, {"Fish", "Potatoes", "Citrus"}, "Restaurant"),

    A1800Unlock("Orchard: Jam", DLC.TOURIST_SEASON, Region.OW, [133496, 133498, 132933], [133496, 134706, 132933],
                Trigger.POPULATION("Tourists", Region.OW, 300),
                {"Timber", "Bricks"}, "Farmers", set(), "Jam"),

    A1800Unlock("Cafe", DLC.TOURIST_SEASON, Region.OW, 132782, 132782,
                Trigger.POPULATION("Tourists", Region.OW, 550),
                {"Timber", "Bricks"}, set(), set(), {"Cafe (Blank)"}),

    A1800Unlock("Cafe: Donut Fourre", DLC.TOURIST_SEASON, Region.OW,
                [132753, RECIPE_GUIDS["Recipe: Donut Fourre"][0]], [132753],
                Trigger.UNLOCK("Cafe", Region.OW),
                set(), {"Tourists", "Cafe (Blank)"}, {"Flour", "Tallow", "Jam"}, "Cafe"),

    A1800Unlock("Cafe: Eclair", DLC.TOURIST_SEASON, Region.OW,
                [133347, RECIPE_GUIDS["Recipe: Eclair"][0]], [133347],
                Trigger.LINEAR(
                    Trigger.COUNTER("Cafe", "Cafe (Blank)", Region.OW, 1, 133510),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: supply Tourists with any Cafe (5 min)",
                        134387,
                        {("Tourists", Region.OW), ("Cafe", Region.OW)}
                    )
                ),
                set(), {"Tourists", "Cafe (Blank)"}, {"Flour", "Sugar", "Chocolate"}, "Cafe"),

    A1800Unlock("Cafe: Palmier Biscuit", DLC.TOURIST_SEASON, Region.OW,
                [133348, RECIPE_GUIDS["Recipe: Palmier Biscuit"][0]], [133348],
                Trigger.LINEAR(
                    Trigger.COUNTER("Cafe", "Cafe (Blank)", Region.OW, 1, 133510),
                    Trigger.ANY(
                        Trigger.COUNTER("Zoo", "Zoo", Region.OW, 1, 101816),
                        Trigger.COUNTER("Zoo", "Zoo", Region.OW, 1, 124109),
                        ap_location_name="Have 1 Elephant Enclosure (Zoo, Eastern Elephant or Elephant)"
                    )
                ),
                set(), {"Tourists", "Cafe (Blank)"}, {"Flour", "Tallow", "Cinnamon"}, "Cafe", is_excluded=True),

    A1800Unlock("Orchard: Coconut Oil", DLC.TOURIST_SEASON, Region.NW,
                [133004, 133005, 133010], [133004, 134710, 133010],
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Coconut Oil"),

    A1800Unlock("Orchard: Cinnamon", DLC.TOURIST_SEASON, Region.NW, [133030, 133028, 133010], [133030, 134708, 133010],
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Cinnamon"),

    A1800Unlock("Chemical Plant: Shampoo", DLC.TOURIST_SEASON, Region.OW,
                [132786, 132788, 132771], [134716, 132771, 137608],
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Soap", "Coconut Oil", "Cinnamon"}, "Shampoo", "Shampoo"),

    A1800Unlock("The Iron Tower: Foundations", DLC.TOURIST_SEASON, Region.OW, 132765, 132765,
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Workers",
                {"Timber", "Cement"}, {"The Iron Tower: Foundations"}),

    A1800Unlock("Orchard: Citrus", DLC.TOURIST_SEASON, Region.NW, [133031, 133029, 133010], [133031, 134707, 133010],
                Trigger.POPULATION("Tourists", Region.OW, 1250),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Citrus"),

    A1800Unlock("Chemical Plant: Lemonade", DLC.TOURIST_SEASON, Region.OW,
                [132777, 132778, 132771], [134712, 132771, 137607],
                Trigger.POPULATION("Tourists", Region.OW, 1250),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Saltpetre", "Sugar", "Citrus"}, "Lemonade", "Lemonade"),

    A1800Unlock("Bar", DLC.TOURIST_SEASON, Region.OW, 132781, 132781,
                Trigger.POPULATION("Tourists", Region.OW, 1500),
                {"Timber", "Bricks"}, set(), set(), {"Bar (Blank)"}),

    A1800Unlock("Bar: Daiquiri Tropic", DLC.TOURIST_SEASON, Region.OW,
                [132752, RECIPE_GUIDS["Recipe: Daiquiri Tropic"][0]], [132752],
                Trigger.UNLOCK("Bar", Region.OW),
                set(), {"Tourists", "Bar (Blank)"}, {"Sugar Cane", "Rum", "Plantains"}, "Bar"),

    A1800Unlock("Bar: Black Muscovy", DLC.TOURIST_SEASON, Region.OW,
                [133342, RECIPE_GUIDS["Recipe: Black Muscovy"][0]], [133342],
                Trigger.LINEAR(Trigger.COUNTER("Bar", "Bar (Blank)", Region.OW, 1, 133472),
                               Trigger.COUNTER("Members Club", "Members Club", Region.OW, 1)),
                set(), {"Tourists", "Bar (Blank)"}, {"Coffee", "Rum", "Schnapps"}, "Bar"),

    A1800Unlock("Bar: Montmartre '75'", DLC.TOURIST_SEASON, Region.OW,
                [133343, RECIPE_GUIDS["Recipe: Montmartre '75'"][0]], [133343],
                Trigger.LINEAR(Trigger.COUNTER("Bar", "Bar (Blank)", Region.OW, 1, 133472),
                               Trigger.EVENT_ACTIVE("World's Fair: Exhibitions", Region.OW)),
                set(), {"Tourists", "Bar (Blank)"}, {"Sugar", "Champagne", "Citrus"}, "Bar"),

    A1800Unlock("The Iron Tower: Superstructure", DLC.TOURIST_SEASON, Region.OW, 132766, 132766,
                Trigger.POPULATION("Tourists", Region.OW, 1500),
                {"The Iron Tower: Foundations"}, "Artisans",
                {"Steel Beams", "Reinforced Concrete"}, {"The Iron Tower: Superstructure"}),

    A1800Unlock("Orchard: Camphor Wax", DLC.TOURIST_SEASON, Region.NW,
                [134614, 134615, 133010], [134614, 134709, 133010],
                Trigger.POPULATION("Tourists", Region.OW, 2000),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Camphor Wax"),

    A1800Unlock("Chemical Plant: Souvenirs", DLC.TOURIST_SEASON, Region.OW,
                [133533, 133534, 132771], [134717, 132771, 137609],
                Trigger.POPULATION("Tourists", Region.OW, 2000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Glass", "Cotton", "Camphor Wax"}, "Souvenirs", "Souvenirs"),

    A1800Unlock("The Iron Tower", DLC.TOURIST_SEASON, Region.OW, 132770, 132770,
                Trigger.POPULATION("Tourists", Region.OW, 4000),
                {"The Iron Tower: Superstructure"}, set(), set(), {"The Iron Tower (Blank)"}),

    A1800Unlock("The Iron Tower: Brioche Royale", DLC.TOURIST_SEASON, Region.OW,
                [133928, RECIPE_GUIDS["Recipe: Brioche Royale"][0]], [133928],
                Trigger.COUNTER("The Iron Tower", "The Iron Tower (Blank)", Region.OW, 1, 134450),
                set(), {"Tourists", "Electricity", "The Iron Tower (Blank)"},
                {"Sausages", "Bread", "Beef", "Gold"}, "The Iron Tower"),

    A1800Unlock("The Iron Tower: Trifle Tower", DLC.TOURIST_SEASON, Region.OW,
                [133930, RECIPE_GUIDS["Recipe: Trifle Tower"][0]], [133930],
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", "The Iron Tower (Blank)", Region.OW, 1, 134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Supply Tourists with The Iron Tower (5 min)",
                        134314,
                        {("Tourists", Region.OW), ("The Iron Tower", Region.OW)}
                    )
                ),
                set(), {"Tourists", "Electricity", "The Iron Tower (Blank)"},
                {"Rum", "Bread", "Grapes", "Sugar"}, "The Iron Tower"),

    A1800Unlock("The Iron Tower: Lady Marmelade", DLC.TOURIST_SEASON, Region.OW,
                [133931, RECIPE_GUIDS["Recipe: Lady Marmelade"][0]], [133931],
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", "The Iron Tower (Blank)", Region.OW, 1, 134450),
                    Trigger.ALL(
                        Trigger.COUNTER("Variety Theatre", "Variety Theatre", Region.OW, 3),
                        Trigger.COUNTER("Chemical Plant: Lemonade", "Lemonade", Region.OW, 1)
                    )
                ),
                set(), {"Tourists", "Electricity", "The Iron Tower (Blank)"},
                {"Rum", "Champagne", "Citrus", "Jam"}, "The Iron Tower"),

    # Building, Factory, Upgrade
    A1800Unlock("Tourist Mooring", DLC.TOURIST_SEASON, Region.OW, 133890, 133890,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Tourist Mooring",
                previous_building="Public Mooring"),

    # Building, Factory, Residence
    A1800Unlock("Hotel", DLC.TOURIST_SEASON, Region.OW, 601445, 601445,
                Trigger.COUNTER("Tourist Mooring", "Tourist Mooring", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(),
                {"Tourist Mooring", "Public Transport"}, "Tourists",
                consumption={"Tourist Mooring", "Bread", "Variety Theatre", "Restaurant", "Jam",
                             "Cafe", "Shampoo", "Bar", "The Iron Tower", "Fire Protection", "Healthcare"},
                luxury={"Fur Coats", "Zoo", "Jewellery", "Lemonade", "Docklands", "Museum",
                        "Botanical Garden", "Palace", "World's Fair", "Souvenirs", "Skyline Tower"},
                lifestyle={"Gramophones", "Bombins", "Leather Boots", "Mezcal", "Ice Cream", "Perfumes"}),

    ### Needs The Passage ###
    # Building, Factory
    A1800Unlock("Restaurant: Venison en Croute", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133340, RECIPE_GUIDS["Recipe: Venison en Croute"][0]], [133340],
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", "Restaurant (Blank)", Region.OW, 1, 135069),
                               Trigger.COUNTER("Arctic Airship Hangar", "Air Travel", Region.AR, 1, 114166,
                                               ap_location_name="(Build 1 OW: Restaurant) THEN (Build 1 Boreas)")),
                set(), {"Tourists", "Restaurant (Blank)"}, {"Flour", "Potatoes", "Caribou Meat"}, "Restaurant"),

    A1800Unlock("Cafe: Venison Tartare", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133349, RECIPE_GUIDS["Recipe: Venison Tartare"][0]], [133349],
                Trigger.LINEAR(Trigger.COUNTER("Cafe", "Cafe (Blank)", Region.OW, 1, 133510),
                               Trigger.COUNTER("Post Office", "Post Office", Region.AR, 1)),
                set(), {"Tourists", "Cafe (Blank)"}, {"Grapes", "Caribou Meat", "Citrus"}, "Cafe"),

    A1800Unlock("Bar: Glogg", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133345, RECIPE_GUIDS["Recipe: Glogg"][0]], [133345],
                Trigger.LINEAR(
                    Trigger.COUNTER("Bar", "Bar (Blank)", Region.OW, 1, 133472),
                    Trigger.COUNTER_EXPEDITION_SOLVED(
                        "Complete 1 expedition in the Arctic",
                        1,
                        134300,
                        {("Expedition: The Arctic", ALL_REGIONS), ("Sea Travel", ALL_REGIONS), ("Artisans", Region.OW)})
                ),
                set(), {"Tourists", "Bar (Blank)"}, {"Whale Oil", "Grapes", "Cinnamon"}, "Bar"),

    A1800Unlock("The Iron Tower: Age of Exploration", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133932, RECIPE_GUIDS["Recipe: Age of Exploration"][0]], [133932],
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", "The Iron Tower (Blank)", Region.OW, 1, 134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Complete the set Polar Circle in a Zoo (Arctic Fox, Great Auk, Narwhal, Polar Bear, Ringed Seal, Walrus)",
                        134983,
                        {("Zoo", Region.OW)}
                    )
                ),
                set(), {"Tourists", "Electricity", "The Iron Tower (Blank)"},
                {"Arctic Gas", "Potatoes", "Red Peppers", "Beef"}, "The Iron Tower", is_excluded=True),

    ### Needs Land of Lions ###
    # Building, Factory
    A1800Unlock("Restaurant: Lobster Cheminee", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133341, RECIPE_GUIDS["Recipe: Lobster Cheminee"][0]], [133341],
                Trigger.LINEAR(
                    Trigger.COUNTER("Restaurant", "Restaurant (Blank)", Region.OW, 1, 135069),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Supply Scholars with Clay Pipes (5 min)",
                        133994,
                        {("Scholars", Region.OW), ("Clay Pipes", Region.OW)}
                    )
                ),
                set(), {"Tourists", "Restaurant (Blank)"}, {"Lobster", "Citrus", "Tobacco"}, "Restaurant"),

    A1800Unlock("Cafe: Banana Surprise", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133350, RECIPE_GUIDS["Recipe: Banana Surprise"][0]], [133350],
                Trigger.LINEAR(Trigger.COUNTER("Cafe", "Cafe (Blank)", Region.OW, 1, 133510),
                               Trigger.COUNTER_GOOD_IN_REGION("Plantains", ALL_REGIONS, 1, Region.EN)),
                set(), {"Tourists", "Cafe (Blank)"}, {"Goat Milk", "Plantains", "Cinnamon"}, "Cafe"),

    A1800Unlock("Bar: Enbesa Sunrise", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133346, RECIPE_GUIDS["Recipe: Enbesa Sunrise"][0]], [133346],
                Trigger.LINEAR(Trigger.COUNTER("Bar", "Bar (Blank)", Region.OW, 1, 133472),
                               Trigger.POPULATION_HAPPINESS("Elders", Session.EN, 30, "Elder Residence")),
                set(), {"Tourists", "Bar (Blank)"}, {"Hibiscus Petals", "Rum", "Spices"}, "Bar"),

    A1800Unlock("The Iron Tower: Homard Lit de Terroir", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133933, RECIPE_GUIDS["Recipe: Homard Lit de Terroir"][0]], [133933],
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", "The Iron Tower (Blank)", Region.OW, 1, 134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Socket a Lobsterman in a Harbourmaster's Office in Enbesa",
                        134984,
                        {("Artisans", Region.OW), ("Elders", Region.EN), ("Harbourmaster's Office", Region.EN)}
                    )
                ),
                set(), {"Tourists", "Electricity", "The Iron Tower (Blank)"},
                {"Lobster", "Sanga Cow", "Potatoes", "Spices"}, "The Iron Tower", is_excluded=True),

    ################################################################################################################
    ### THE_HIGH_LIFE                                                                                            ###
    ################################################################################################################

    # TODO: Bus need Skyline Tower

    ################################################################################################################
    ### EMPIRE_OF_THE_SKIES                                                                                      ###
    ################################################################################################################

    # TODO: Meta Upgrades for Alpaca and Cattle Farms with Electricity

    ################################################################################################################
    ### NEW_WORLD_RISING                                                                                         ###
    ################################################################################################################

    # TODO: New restaurant, cafe, bar
]


class _Unlocks:
    _initialized: bool = False

    def init(self, enabled_dlcs: DLC) -> None:
        self._apply_options(enabled_dlcs)

        for a1800_unlock in self._a1800_unlocks:
            a1800_unlock.post_init()
            self._add_guids_to_trigger(a1800_unlock.trigger)

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

    def _add_guids_to_trigger(self, trigger: Trigger) -> None:
        if trigger.trigger_type in [TriggerType.ALL, TriggerType.LINEAR, TriggerType.ANY]:
            for subtrigger in trigger.triggers:
                self._add_guids_to_trigger(subtrigger)
        elif (trigger.trigger_type == TriggerType.UNLOCK or trigger.trigger_type == TriggerType.COUNTER) \
                and trigger.guid == 0:
            references = [unlock for unlock in self._a1800_unlocks
                          if unlock.name == trigger.unlock_name and trigger.region in unlock.region]
            assert references, f"Trigger references unknown unlock {trigger.unlock_name}"
            assert len(references) == 1, \
                f"Trigger references multiple unlocks {[reference.name for reference in references]}"
            assert references[0].unlock_guids, \
                f"Trigger references unlock {references[0].name}, which has no guids"
            trigger.guid = references[0].unlock_guids[0]
        elif (trigger.trigger_type == TriggerType.COUNTER_GOOD_IN_REGION) and trigger.guid == 0:
            references = list(PRODUCTS.find_products(trigger.product_name, trigger.product_region))
            assert references, f"Trigger references unknown product {trigger.product_name}"
            assert len(references) == 1, \
                f"Trigger references multiple products {[reference.name for reference in references]}"
            trigger.guid = references[0].guid
        elif (trigger.trigger_type == TriggerType.EVENT_ACTIVE) and trigger.guid == 0:
            references = list(PRODUCTS.find_products(trigger.product_name, trigger.region))
            assert references, f"Trigger references unknown product {trigger.product_name}"
            assert len(references) == 1, \
                f"Trigger references multiple products {[reference.name for reference in references]}"
            trigger.guid = references[0].guid
        elif (trigger.trigger_type in [TriggerType.POPULATION, TriggerType.POPULATION_HAPPINESS]) and trigger.guid == 0:
            references = list(PRODUCTS.find_products(trigger.population_name, trigger.region))
            assert references, f"Trigger references unknown population {trigger.population_name}"
            assert len(references) == 1, \
                f"Trigger references multiple populations {[reference.name for reference in references]}"
            trigger.guid = references[0].guid

    def _clean_dlc_trigger(self, enabled_dlcs: DLC, trigger: Trigger) -> Trigger:
        if trigger.trigger_type in [TriggerType.ALL, TriggerType.LINEAR]:
            trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.TRUE]

            if len(trigger.triggers) == 0:
                return Trigger.TRUE()
            elif len(trigger.triggers) == 1:
                return trigger.triggers[0]
            elif any([subtrigger.trigger_type == TriggerType.FALSE for subtrigger in trigger.triggers]):
                return Trigger.FALSE()
            else:
                return trigger
        elif trigger.trigger_type == TriggerType.ANY:
            trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.FALSE]

            if len(trigger.triggers) == 0:
                return Trigger.FALSE()
            elif len(trigger.triggers) == 1:
                return trigger.triggers[0]
            elif any([subtrigger.trigger_type == TriggerType.TRUE for subtrigger in trigger.triggers]):
                return Trigger.TRUE()
            else:
                return trigger
        elif trigger.trigger_type in [TriggerType.POPULATION, TriggerType.POPULATION_HAPPINESS]:
            return Trigger.FALSE() if not next(PRODUCTS.find_populations(trigger.population_name, trigger.region), None) else trigger
        elif trigger.trigger_type == TriggerType.UNLOCK:
            return Trigger.FALSE() if not len([unlock for unlock in self._a1800_unlocks if unlock.name == trigger.unlock_name
                                               and trigger.region in unlock.region]) else trigger
        elif trigger.trigger_type == TriggerType.COUNTER:
            return Trigger.FALSE() if not next(PRODUCTS.find_products(trigger.product_name, trigger.region), None) or \
                not len([unlock for unlock in self._a1800_unlocks if unlock.name == trigger.unlock_name
                         and trigger.region in unlock.region]) else trigger
        elif trigger.trigger_type == TriggerType.COUNTER_GOOD_IN_REGION:
            return Trigger.FALSE() if not next(
                PRODUCTS.find_products(trigger.product_name, trigger.product_region), None) else trigger
        elif trigger.trigger_type == TriggerType.EVENT_ACTIVE:
            return Trigger.FALSE() if not next(
                PRODUCTS.find_products(trigger.product_name, trigger.region), None) else trigger
        elif trigger.trigger_type in [TriggerType.COUNTER_EXPEDITION_SOLVED, TriggerType.QUEST_COMPLETE]:
            return Trigger.FALSE() if any(
                [not next(PRODUCTS.find_products(name, region), None) and
                 (len([unlock for unlock in self._a1800_unlocks if unlock.name == name and region in unlock.region]) == 0)
                    for name, region in trigger.requirements]
            ) else trigger
        else:
            return trigger

    def _clean_dlc_references(self, enabled_dlcs: DLC) -> None:
        for unlock in self._a1800_unlocks:
            unlock.trigger = self._clean_dlc_trigger(enabled_dlcs, unlock.trigger)

            missing_outputs: set[tuple[str, Region]] = set()
            for output in unlock.output:
                if not next(PRODUCTS.find_products(output[0], output[1]), None):
                    missing_outputs.add(output)
            if missing_outputs:
                unlock.output -= missing_outputs

            missing_chains: set[tuple[str, Region]] = set()
            for chain in unlock.unlock_chain:
                if not next(CHAINS.find_chains(chain[0], unlock.name, unlock.region, chain[1]), None):
                    missing_chains.add(chain)
            if missing_chains:
                unlock.unlock_chain -= missing_chains

            if unlock.name == "Hotel":  # Turning off DLC can remove tourist luxury needs
                missing_luxuries: set[str] = set()
                for luxury in unlock.luxury:
                    if not next(PRODUCTS.find_products(luxury, unlock.region), None):
                        missing_luxuries.add(luxury)
                if missing_luxuries:
                    unlock.luxury -= missing_luxuries

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
                    unlock.output.add(("Local Mail", Region.AR))
                    break

        self._clean_dlc_references(enabled_dlcs)

    def _verify_data(self) -> None:
        # Assure all references exist
        for unlock in self._a1800_unlocks:
            assert unlock.region, f"Unlock {unlock.name} has no region"

            if unlock.trigger.trigger_type == TriggerType.POPULATION:
                assert next(PRODUCTS.find_populations(unlock.trigger.population_name, unlock.trigger.region), None), \
                    f"Unlock {unlock} trigger references non-existent population {unlock.trigger.population_name}, " \
                    f"{unlock.trigger.region}"

            for cost in unlock.cost:
                assert next(PRODUCTS.find_products(cost, unlock.region), None), \
                    f"Unlock {unlock} references non-existent cost {cost}"

            for maintenance in unlock.maintenance:
                assert next(PRODUCTS.find_products(maintenance, unlock.region), None), \
                    f"Unlock {unlock} references non-existent maintenance {maintenance}"

            for name, region in unlock.input:
                assert next(PRODUCTS.find_products(name, region), None), \
                    f"Unlock {unlock} references non-existent input {name}"

            for name, region in unlock.output:
                assert next(PRODUCTS.find_products(name, region), None), \
                    f"Unlock {unlock} references non-existent output {name}"

            for chain, region in unlock.unlock_chain:
                assert next(CHAINS.find_chains(chain, unlock.name, unlock.region, region), None), \
                    f"Unlock {unlock} references non-existent chain {chain}"

            if unlock.previous_building:
                assert next(self.find_unlocks(unlock.previous_building, unlock.region), None), \
                    f"Unlock {unlock} references non-existent previous building {unlock.previous_building}"

            for consumption in unlock.consumption:
                assert next(PRODUCTS.find_products(consumption, unlock.region), None), \
                    f"Unlock {unlock} references non-existent consumption {consumption}"

            for luxury in unlock.luxury:
                assert next(PRODUCTS.find_products(luxury, unlock.region), None), \
                    f"Unlock {unlock} references non-existent luxury {luxury}"

            for lifestyle in unlock.lifestyle:
                assert next(PRODUCTS.find_products(lifestyle, unlock.region), None), \
                    f"Unlock {unlock} references non-existent lifestyle {lifestyle}"

        # Assure all chain references exist
        for chain in CHAINS.get_chains():
            assert chain.region, f"Chain {chain.name} has no region"

            for name, region in chain.elements:
                assert next(self.find_unlocks(name, region), None), f"Chain {chain.name} references non-existent "\
                    f"unlock {name}, {region}"

        # Assure all trigger references exist
        for unlock in self.get_unlocks():
            if unlock.trigger.trigger_type == TriggerType.POPULATION:
                population = next(PRODUCTS.find_populations(
                    unlock.trigger.population_name, unlock.trigger.region), None)
                assert population, f"Population {unlock.trigger.population_name} referenced in {unlock} was filtered "\
                    "during init and no longer is available!"


UNLOCKS = _Unlocks()
