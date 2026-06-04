from collections.abc import Sequence
from typing import ClassVar, Iterator, Optional

from ._Chains import CHAINS
from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, TriggerType, UnlockType
from ._Guid import RECIPE_GUIDS
from ._ParsedOptions import ParsedOptions
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
    dlc: set[DLC]
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
        dlc: DLC | set[DLC],
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
        is_excluded: bool = False
    ) -> None:
        self.name = name
        self.dlc = {dlc} if isinstance(dlc, DLC) else dlc
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
                chain_guid = next(CHAINS.find_chains(chain, self.name, self.region, region)).guid
                if not chain_guid in self.unlock_guids:
                    self.unlock_guids.append(chain_guid)

        if UnlockType.FACTORY in self.type:
            for name, region in self.output:
                output_guid = next(PRODUCTS.find_products(name, region)).guid
                if output_guid and not output_guid in self.unlock_guids:
                    self.unlock_guids.append(output_guid)

    def __str__(self) -> str:
        return f"(Unlock: {self.name}, {self.region})"


_a1800_unlocks: list[A1800Unlock] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    # Meta
    A1800Unlock("Starting Goods", DLC.VANILLA, Region.OW,  # Resolves circular dependency at game start
                output="Timber", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Trading Post Materials and Seafaring", DLC.VANILLA, Region.OW | Region.NW,
                input={"Timber", "Steel Beams", "Seafaring"}, output="Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Oil Transport OW => NW", DLC.VANILLA, Region.NW,
                input={("Oil", Region.OW), "Oil Transport"}, output="Oil", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => OW", DLC.VANILLA, Region.OW,
                input={("Oil", Region.NW), "Oil Transport"}, output="Oil", type=UnlockType.META | UnlockType.FACTORY),

    # Unlock
    A1800Unlock("Expedition: New World", DLC.VANILLA, ALL_REGIONS, Session.NW.expedition_unlock_guid, [],
                Trigger.POPULATION("Artisans", Region.OW, 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.VANILLA, Region.OW, [1010517, 1010540], [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.OW, 1010371, 130040,
                Trigger.SESSION_ENTER(Session.OW), "Timber"),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.OW, 1010516, 1010516,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}),

    A1800Unlock("Mounted Guns", DLC.VANILLA, Region.OW, 1010522, 1010522,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.OW, 1010567, 130121,
                Trigger.POPULATION("Workers", Region.OW, 150), type=UnlockType.BUILDING),

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

    A1800Unlock("Small Warehouse", DLC.VANILLA, Region.NW, 101323,
                130095, Trigger.SESSION_ENTER(Session.NW), "Timber"),

    A1800Unlock("Trade Union", DLC.VANILLA, Region.NW, 101284, 101284,
                Trigger.POPULATION("Jornaleros", Region.NW, 50), {"Timber", "Bricks"}),

    A1800Unlock("Quay", DLC.VANILLA, Region.NW, 101339, 130106,
                Trigger.POPULATION("Jornaleros", Region.NW, 100), type=UnlockType.BUILDING),

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
    A1800Unlock("Dirt Road", DLC.VANILLA, Region.OW, 1000178, 1000178,
                Trigger.SESSION_ENTER(Session.OW), output="Road Network", type=UnlockType.BUILDING | UnlockType.FACTORY),

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

    A1800Unlock("Paved Street", DLC.VANILLA, Region.OW, 1010035, 1010035,
                Trigger.POPULATION("Workers", Region.OW, 1), "Bricks", output="Road Network"),

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
                {"Timber", "Bricks"}, "Workers", set(), "Sailing Ships"),

    A1800Unlock("Depot", DLC.VANILLA, Region.OW, 1010519, 130121,
                Trigger.POPULATION("Workers", Region.OW, 150), {"Timber", "Bricks"}, output={"Medium Storage", "Large Storage", "Grand Storage"}),

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
                {"Timber", "Steel Beams"}, set(), set(), "Railway", {("Electricity", Region.OW), ("Electricity", Region.NW)}),

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
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete",
                    "Medium Storage"}, {"Engineers", "Electricity"}, set(), {"Steam Ships"}),

    A1800Unlock("Saltpetre Works", DLC.VANILLA, Region.OW, 1010310, 140053,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams"}, {"Workers", "Settling"}, set(), "Saltpetre", "Advanced Weapons"),

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
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Large Storage"}, "Farmers",
                {"Timber", "Cement"}, "World's Fair: Foundations"),

    A1800Unlock("Marquetry Workshop", DLC.VANILLA, Region.OW, 1010320, 130116,
                Trigger.POPULATION("Investors", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                "Wood", "Wood Veneers", "Cigars"),

    A1800Unlock("Members Club", DLC.VANILLA, Region.OW, 1010364, 130048,
                Trigger.POPULATION("Investors", Region.OW, 750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"}, set(), set(), "Members Club"),

    A1800Unlock("World's Fair: Superstructure", DLC.VANILLA, Region.OW, 1010490, 1010490,
                Trigger.POPULATION("Investors", Region.OW, 750),
                "World's Fair: Foundations", "Workers",
                {"Bricks", "Steel Beams", "Reinforced Concrete"}, "World's Fair: Superstructure"),

    A1800Unlock("Jewellers", DLC.VANILLA, Region.OW, 1010328, 140048,
                Trigger.POPULATION("Investors", Region.OW, 1750),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Pearls", "Gold"}, "Jewellery", "Jewellery"),

    A1800Unlock("World's Fair: Glazing", DLC.VANILLA, Region.OW, 101336, 101336,
                Trigger.POPULATION("Investors", Region.OW, 1750),
                "World's Fair: Superstructure", "Artisans",
                {"Windows", "Steam Motors", "Wood Veneers"}, "World's Fair: Glazing"),

    A1800Unlock("Gramophone Factory", DLC.VANILLA, Region.OW, 1010326, 140047,
                Trigger.POPULATION("Investors", Region.OW, 3000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Engineers", "Electricity"},
                {"Wood Veneers", "Brass"}, "Gramophones", "Gramophones"),

    A1800Unlock("World's Fair: Infrastructure", DLC.VANILLA, Region.OW, 1010491, 1010491,
                Trigger.POPULATION("Investors", Region.OW, 3000),
                "World's Fair: Glazing", {"Engineers", "Electricity"},
                {"Filaments", "Light Bulbs", "Caoutchouc"}, "World's Fair: Infrastructure"),

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
                "World's Fair: Infrastructure", {"Investors", "Electricity"},
                set(), {"World's Fair: Exhibitions", "World's Fair"}),

    A1800Unlock("Dirt Road", DLC.VANILLA, Region.NW, 101308, 101308,
                Trigger.SESSION_ENTER(Session.NW), output="Road Network", type=UnlockType.BUILDING | UnlockType.FACTORY, ap_region=Region.OW),

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
                {"Timber", "Bricks"}, "Jornaleros", set(), "Sailing Ships"),

    A1800Unlock("Depot", DLC.VANILLA, Region.NW, 101278, 130106,
                Trigger.POPULATION("Jornaleros", Region.NW, 100),
                {"Timber", "Bricks"}, output={"Medium Storage", "Large Storage", "Grand Storage"}),

    A1800Unlock("Alpaca Farm", DLC.VANILLA, Region.NW, 101272, 130097,
                Trigger.POPULATION("Jornaleros", Region.NW, 200),
                "Timber", "Jornaleros", set(), {"Alpaca Wool", "Alpaca Farm"}, "Ponchos"),

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

    A1800Unlock("Paved Street", DLC.VANILLA, Region.NW, 101309, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Bricks",
                # output="Road Network", ap_region=Region.OW # Don't allow settling with Paveed Street - later with option
                ),

    A1800Unlock("Clay Pit", DLC.VANILLA, Region.NW, 101267, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Obreros", set(), "Clay", "Bricks"),

    A1800Unlock("Brick Factory", DLC.VANILLA, Region.NW, 101268, 130100,
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", "Obreros", "Clay", "Bricks", "Bricks"),

    A1800Unlock("Cattle Farm", DLC.VANILLA, Region.NW, 101269, 130101,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                "Timber", "Jornaleros", set(), {"Beef", "Cattle Farm"}, "Tortillas"),

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
    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.OW, 100516, 130053,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Large Warehouse", DLC.VANILLA, Region.OW, 100517, 130054,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, previous_building="Medium Warehouse"),

    A1800Unlock("Grand Warehouse", DLC.VANILLA, Region.OW, 269869, 269869,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Large Warehouse"),

    A1800Unlock("Medium Oil Harbour", DLC.VANILLA, Region.OW, 101403, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Small Oil Harbour"),

    A1800Unlock("Large Oil Harbour", DLC.VANILLA, Region.OW, 101404, 130047,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                previous_building="Medium Oil Harbour"),

    A1800Unlock("Medium Warehouse", DLC.VANILLA, Region.NW, 101324, 130104,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}, previous_building="Small Warehouse"),

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

    # Building, Factory, Upgrade
    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.OW, [100510, 100514], 130053,
                Trigger.POPULATION("Workers", Region.OW, 1), {"Timber", "Bricks"}, output="Medium Storage", previous_building="Small Trading Post"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.OW, [100511, 100515], 130054,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, output="Large Storage", previous_building="Medium Trading Post"),

    A1800Unlock("Grand Trading Post", DLC.VANILLA, Region.OW, [269867, 269879], [269867, 269879],
                Trigger.POPULATION("Engineers", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                output="Grand Storage", previous_building="Large Trading Post"),

    A1800Unlock("Medium Trading Post", DLC.VANILLA, Region.NW, [101291, 101294], 130104,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}, output="Medium Storage", previous_building="Small Trading Post"),

    A1800Unlock("Large Trading Post", DLC.VANILLA, Region.NW, [101292, 101295], 130105,
                Trigger.POPULATION("Obreros", Region.NW, 1500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, output="Large Storage", previous_building="Medium Trading Post"),

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
                    "Overseas Mail", "Soccer Balls", "Perfumes", "Scooters"}),

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
                    "Overseas Mail", "Perfumes", "Fans", "Film Reels"}),

    A1800Unlock("Obrero Residence", DLC.VANILLA, Region.NW, 101255, 101255,
                Trigger.POPULATION("Jornaleros", Region.NW, 200),
                "Timber", set(), set(), "Obreros", "", "Jornalero Residence",
                {"Market", "Fried Plantains", "Ponchos", "Tortillas", "Coffee", "Bombins",
                    "Sewing Machines", "Fire Protection", "Riot Control", "Healthcare"},
                {"Rum", "Chapel", "Boxing Arena", "Beer", "Cigars"},
                {"Spectacles", "Typewriters", "Illuminated Script", "Local Mail",
                    "Regional Mail", "Overseas Mail", "Beach", "Samba School", "Scooters"}),

    # Factory
    A1800Unlock("Schooner", DLC.VANILLA, ALL_REGIONS, 100438, 100438,
                Trigger.UNLOCK("Sailing Shipyard", Region.OW),
                input={"Sailing Ships", "Timber", "Sails"}, output={"Seafaring", "Expeditions: Level 1"}, ap_region=Region.OW),

    A1800Unlock("Gunboat", DLC.VANILLA, ALL_REGIONS, 100437, 100437,
                Trigger.UNLOCK("Sailing Shipyard", Region.OW),
                input={"Sailing Ships", "Timber", "Sails", "Weapons"}, output={"Seafaring", "Expeditions: Level 1"}, ap_region=Region.OW),

    A1800Unlock("Frigate", DLC.VANILLA, ALL_REGIONS, 100439, 100439,
                Trigger.POPULATION("Artisans", Region.OW, 1),
                input={"Sailing Ships", "Timber", "Sails", "Weapons"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2"}, ap_region=Region.OW),

    A1800Unlock("Clipper", DLC.VANILLA, ALL_REGIONS, 100441, 100441,
                Trigger.POPULATION("Artisans", Region.OW, 750),
                input={"Sailing Ships", "Timber", "Sails"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2"}, ap_region=Region.OW),

    A1800Unlock("Ship-of-the-line", DLC.VANILLA, ALL_REGIONS, 100440, 100440,
                Trigger.POPULATION("Artisans", Region.OW, 750),
                input={"Sailing Ships", "Timber", "Sails", "Weapons"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2", "Expeditions: Level 3"}, ap_region=Region.OW),

    A1800Unlock("Oil Tanker", DLC.VANILLA, ALL_REGIONS, 100853, 100853,
                Trigger.UNLOCK("Oil Power Plant", Region.OW),
                input={"Steam Ships", "Steel Beams", "Steam Motors"}, output={"Oil Transport"}, ap_region=Region.OW),

    A1800Unlock("Cargo Ship", DLC.VANILLA, ALL_REGIONS, 1010062, 1010062,
                Trigger.UNLOCK("Steam Shipyard", Region.OW),
                input={"Steam Ships", "Steel Beams", "Steam Motors"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2", "Expeditions: Level 3"}, ap_region=Region.OW),

    A1800Unlock("Battle Cruiser", DLC.VANILLA, ALL_REGIONS, 100442, 100442,
                Trigger.UNLOCK("Steam Shipyard", Region.OW),
                input={"Steam Ships", "Steel Beams", "Steam Motors", "Advanced Weapons"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2", "Expeditions: Level 3"}, ap_region=Region.OW),

    A1800Unlock("Monitor", DLC.VANILLA, ALL_REGIONS, 100443, 100443,
                Trigger.POPULATION("Investors", Region.OW, 1),
                input={"Steam Ships", "Steel Beams", "Steam Motors", "Advanced Weapons"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2"}, ap_region=Region.OW),

    A1800Unlock("Flamethrower Monitor", DLC.VANILLA, ALL_REGIONS, 968, 968,
                Trigger.POPULATION("Investors", Region.OW, 1),
                input={"Steam Ships", "Steel Beams", "Steam Motors", "Advanced Weapons"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2"}, ap_region=Region.OW),

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
    A1800Unlock("Trading Post Materials and Seafaring", DLC.THE_PASSAGE, Region.AR,
                input={"Timber", "Steel Beams", "Seafaring"}, output="Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Sky Post Materials and Aviation", DLC.THE_PASSAGE, Region.AR,
                input={"Timber", "Steel Beams", "Aviation"}, output="Plateau Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Search in the far northern Arctic", DLC.THE_PASSAGE, Region.AR,
                input="Aviation", output="Lost Expedition Scrap",
                type=UnlockType.META | UnlockType.FACTORY),

    # Unlock
    A1800Unlock("Expedition: The Arctic", DLC.THE_PASSAGE, ALL_REGIONS, Session.AR.expedition_unlock_guid, [],
                Trigger.POPULATION("Engineers", Region.OW, 1)),

    # Building
    A1800Unlock("Small Trading Post", DLC.THE_PASSAGE, Region.AR, [112659, 112865], [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Small Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 112726, [],
                Trigger.SESSION_ENTER(Session.OW), {"Timber", "Steel Beams"}),

    A1800Unlock("Small Warehouse", DLC.THE_PASSAGE, Region.AR, 112656, 112716,
                Trigger.SESSION_ENTER(Session.AR), "Timber"),

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

    A1800Unlock("Road", DLC.THE_PASSAGE, Region.AR, 112113, 112113,
                Trigger.SESSION_ENTER(Session.AR), output="Road Network", type=UnlockType.BUILDING | UnlockType.FACTORY, ap_region=Region.OW),

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
                {"Timber", "Cement"}, "Arctic Airship Hangar: Foundations"),

    A1800Unlock("Depot", DLC.THE_PASSAGE, Region.AR, 112670, 112670,
                Trigger.POPULATION("Technicians", Region.AR, 1), "Timber", output={"Medium Storage", "Large Storage"}),

    A1800Unlock("Post Office", DLC.THE_PASSAGE, Region.AR, 112684, 112684,
                Trigger.POPULATION("Technicians", Region.AR, 100), {"Timber", "Steel Beams"}, set(), set(), "Post Office"),

    A1800Unlock("Arctic Airship Hangar: Structure", DLC.THE_PASSAGE, Region.AR, 112687, 112687,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                "Arctic Airship Hangar: Foundations", {"Technicians", "Heat"},
                {"Steel Beams", "Reinforced Concrete"}, "Arctic Airship Hangar: Structure"),

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
                "Arctic Airship Hangar: Structure", {"Technicians", "Heat"},
                {"Sails", "Windows", "Steam Motors"}, "Arctic Airship Hangar: Roof"),

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

    A1800Unlock("Arctic Airship Hangar", DLC.THE_PASSAGE, Region.AR, 112689, 112689,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                "Arctic Airship Hangar: Roof", {"Technicians", "Heat"},
                set(), "Arctic Airships"),

    # Building, Upgrade
    A1800Unlock("Medium Warehouse", DLC.THE_PASSAGE, Region.AR, 112657, 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500), "Timber", previous_building="Small Warehouse"),

    A1800Unlock("Large Warehouse", DLC.THE_PASSAGE, Region.AR, 112658, 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100), "Timber", previous_building="Medium Warehouse"),

    # Building, Factory, Upgrade
    A1800Unlock("Medium Trading Post", DLC.THE_PASSAGE, Region.AR, [112660, 112866], 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                {"Timber", "Steel Beams"}, output="Medium Storage", previous_building="Small Trading Post"),

    A1800Unlock("Medium Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 116003, 112723,
                Trigger.POPULATION("Explorers", Region.AR, 500),
                {"Timber", "Steel Beams"}, output="Medium Plateau Storage", previous_building="Small Sky Trading Post"),

    A1800Unlock("Large Trading Post", DLC.THE_PASSAGE, Region.AR, [112661, 112867], 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                {"Timber", "Steel Beams"}, output="Large Storage", previous_building="Medium Trading Post"),

    A1800Unlock("Large Sky Trading Post", DLC.THE_PASSAGE, Region.AR, 116004, 112724,
                Trigger.POPULATION("Technicians", Region.AR, 100),
                {"Timber", "Steel Beams", "Windows"}, output="Large Plateau Storage", previous_building="Medium Sky Trading Post"),

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

    # Factory
    # No arctic gas input to avoid cyclic dependency - Nate will always give you some if you have none and no Boreas
    A1800Unlock("Boreas", DLC.THE_PASSAGE, ALL_REGIONS, 114166, 114166,
                Trigger.POPULATION("Technicians", Region.AR, 750),
                input={"Arctic Airships", "Timber", "Sails", "Steam Motors"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Blue Flamethrower Monitor", DLC.THE_PASSAGE, ALL_REGIONS, 1537, 1537,
                Trigger.ALL(Trigger.POPULATION("Technicians", Region.AR, 750),
                            Trigger.POPULATION("Investors", Region.OW, 1)),
                input={"Steam Ships", "Steel Beams", "Steam Motors", "Advanced Weapons", "Arctic Gas"}, output={"Seafaring", "Expeditions: Level 1", "Expeditions: Level 2"}, ap_region=Region.OW),

    ################################################################################################################
    ### SEAT_OF_POWER                                                                                            ###
    ################################################################################################################
    # Building, Factory
    A1800Unlock("Palace", DLC.SEAT_OF_POWER, Region.OW, 249947, 249947,
                Trigger.POPULATION("Investors", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Large Storage"}, output="Palace"),

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
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"},
                previous_building="Large Oil Harbour"),
    A1800Unlock("Grand Oil Harbour", DLC.BRIGHT_HARVEST, Region.NW, 119281, 119281,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"},
                previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
    # Meta
    A1800Unlock("Seafaring => Free Clipper", DLC.LAND_OF_LIONS, Region.EN,
                input="Seafaring", output={"Initial Settling", "Wanza Timber"},
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.OW),

    A1800Unlock("Trading Post Materials and Seafaring", DLC.LAND_OF_LIONS, Region.EN,
                input={"Wanza Timber", "Mud Bricks", "Seafaring"}, output="Settling",
                type=UnlockType.META | UnlockType.FACTORY, ap_region=Region.EN),

    # Research Institute, Engineers for infinite permits
    A1800Unlock("1500 Elders", DLC.LAND_OF_LIONS, Region.EN,
                input={("Elders", Region.EN), ("Engineers", Region.OW), ("Research", Region.OW)},
                output="Permit: Scholar Residence",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Research: Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research", "Research Points"},
                output="Permit: Advanced Coffee Roaster",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Research: Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research", "Research Points"},
                output="Permit: Advanced Rum Distillery",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Research: Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research", "Research Points"},
                output="Permit: Advanced Cotton Mill",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Research: Advanced Pier", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research", "Research Points"},
                output="Permit: Advanced Pier",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Research: Great Eastern", DLC.LAND_OF_LIONS, Region.OW,
                input={"Engineers", "Research", "Research Points"},
                output="Permit: Great Eastern",
                type=UnlockType.META | UnlockType.FACTORY),

    # Unlock
    A1800Unlock("Expedition: Enbesa", DLC.LAND_OF_LIONS, ALL_REGIONS, Session.EN.expedition_unlock_guid, [],
                Trigger.POPULATION("Artisans", Region.OW, 100)),

    # Building
    A1800Unlock("Small Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114626, 114629], [],
                Trigger.SESSION_ENTER(Session.OW), {"Wanza Timber", "Mud Bricks"}),

    A1800Unlock("Small Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114509, 114509,
                Trigger.SESSION_ENTER(Session.EN), "Wanza Timber"),

    A1800Unlock("Quay", DLC.LAND_OF_LIONS, Region.EN, 117729, 117918,
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
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"}, "Workers",
                {"Bricks", "Cement"}, "Research Institute: Foundations"),

    A1800Unlock("Research Institute: Superstructure", DLC.LAND_OF_LIONS, Region.OW, 118939, 118939,
                Trigger.POPULATION("Elders", Region.EN, 300),
                "Research Institute: Foundations", "Engineers",
                {"Steel Beams", "Windows", "Reinforced Concrete"}, "Research Institute: Superstructure"),

    A1800Unlock("Research Institute", DLC.LAND_OF_LIONS, Region.OW, [118940, 119392], [118940, 119392],
                Trigger.POPULATION("Elders", Region.EN, 300),
                "Research Institute: Superstructure", {"Engineers", "Electricity"}, set(), "Research"),

    A1800Unlock("Advanced Coffee Roaster", DLC.LAND_OF_LIONS, Region.OW, 124738, 127612,
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Coffee Roaster"},
                {"Engineers", "Electricity"}, "Malt", "Coffee", "Coffee (alt)"),

    A1800Unlock("Advanced Rum Distillery", DLC.LAND_OF_LIONS, Region.OW, 124737, 127613,
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Reinforced Concrete", "Permit: Advanced Rum Distillery"},
                {"Engineers", "Electricity"}, {"Potatoes", "Coal"}, "Rum", "Rum (alt)"),

    A1800Unlock("Advanced Cotton Mill", DLC.LAND_OF_LIONS, Region.OW, 124739, 127614,
                Trigger.COUNTER("Research Institute", Region.OW, 1),
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

    A1800Unlock("Desert Road", DLC.LAND_OF_LIONS, Region.EN, 114523, 114523,
                Trigger.SESSION_ENTER(Session.EN), output="Road Network", type=UnlockType.BUILDING | UnlockType.FACTORY, ap_region=Region.OW),

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

    A1800Unlock("Depot", DLC.LAND_OF_LIONS, Region.EN, 117870, 117918,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber", output={"Medium Storage", "Large Storage"}),

    A1800Unlock("Musicians' Court", DLC.LAND_OF_LIONS, Region.EN, 114519, 114519,
                Trigger.POPULATION("Shepherds", Region.EN, 150), "Wanza Timber", set(), set(), "Musicians' Court"),

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

    A1800Unlock("Paved Street", DLC.LAND_OF_LIONS, Region.EN, 119029, 119029,
                Trigger.POPULATION("Elders", Region.EN, 1), "Mud Bricks", output="Road Network", ap_region=Region.OW),

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
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.NW, 125191, 125191,
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    A1800Unlock("Medium Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114537, 114633,
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Small Warehouse"),

    A1800Unlock("Large Warehouse", DLC.LAND_OF_LIONS, Region.EN, 114635, 114634,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, previous_building="Medium Warehouse"),

    A1800Unlock("Advanced Pier", DLC.LAND_OF_LIONS, Region.EN, 125193, 125193,
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Wanza Timber", "Mud Bricks", "Permit: Advanced Pier"}, previous_building="Pier"),

    # Building, Factory, Upgrade
    A1800Unlock("Medium Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114627, 114630], 114633,
                Trigger.POPULATION("Elders", Region.EN, 1),
                {"Wanza Timber", "Mud Bricks"}, output="Medium Storage", previous_building="Small Trading Post"),

    A1800Unlock("Large Trading Post", DLC.LAND_OF_LIONS, Region.EN, [114628, 114631], 114634,
                Trigger.POPULATION("Elders", Region.EN, 600),
                {"Wanza Timber", "Mud Bricks"}, output="Large Storage", previous_building="Medium Trading Post"),

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
                           "New World Reports", "Arctic Reports", "Film Reels", "Fans", "Scooters"}),

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
                Trigger.COUNTER("Research Institute", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Permit: Advanced Pier"},
                previous_building="Pier"),

    ### Needs Bright Harvest ###
    # Meta
    A1800Unlock("Oil Transport OW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN,
                input={("Oil", Region.OW), "Oil Transport"}, output="Oil",  type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Oil Transport NW => EN", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN,
                input={("Oil", Region.NW), "Oil Transport"}, output="Oil", type=UnlockType.META | UnlockType.FACTORY),

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
                {"Wanza Timber", "Mud Bricks", "Medium Storage"}, set(), set(), "Oil Harbour", previous_building="Large Oil Harbour"),

    ################################################################################################################
    ### DOCKLANDS                                                                                                ###
    ################################################################################################################
    # Building, Factory
    A1800Unlock("Docklands Main Wharf", DLC.DOCKLANDS, Region.OW, 601470, 601470,
                Trigger.POPULATION("Artisans", Region.OW, 250),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, output=set[str | tuple[str, Region]]({
                    "Docklands", "Medium Storage", "Large Storage", "Grand Storage"
                }) | {
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
                Trigger.COUNTER("Tourist Mooring", Region.OW, 1), "Steel Beams", set(), set(), "Public Transport"),

    A1800Unlock("Restaurant", DLC.TOURIST_SEASON, Region.OW, 132780, 132780,
                Trigger.POPULATION("Tourists", Region.OW, 250),
                {"Timber", "Bricks"}, set(), set(), "Restaurant (Blank)"),

    A1800Unlock("Restaurant: Archduke's Schnitzel", DLC.TOURIST_SEASON, Region.OW,
                [132747, RECIPE_GUIDS["Recipe: Archduke's Schnitzel"][0]], 132747,
                Trigger.UNLOCK("Restaurant", Region.OW),
                "Restaurant (Blank)", "Tourists", {"Pigs", "Potatoes", "Tallow"}, "Restaurant"),

    A1800Unlock("Restaurant: Stroggof Goulash", DLC.TOURIST_SEASON, Region.OW,
                [132750, RECIPE_GUIDS["Recipe: Stroggof Goulash"][0]], 132750,
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", Region.OW, 1, guid=135069),
                               Trigger.COUNTER_GOOD_IN_REGION("Corn", ALL_REGIONS, 1, Region.OW)),
                "Restaurant (Blank)", "Tourists", {"Beef", "Red Peppers", "Corn"}, "Restaurant"),

    A1800Unlock("Restaurant: Fish and Frites", DLC.TOURIST_SEASON, Region.OW,
                [133339, RECIPE_GUIDS["Recipe: Fish and Frites"][0]], 133339,
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", Region.OW, 1, guid=135069),
                               Trigger.COUNTER("Orchard: Citrus", Region.NW, 1)),
                "Restaurant (Blank)", "Tourists", {"Fish", "Potatoes", "Citrus"}, "Restaurant"),

    A1800Unlock("Orchard: Jam", DLC.TOURIST_SEASON, Region.OW, [133496, 133498, 132933], [133496, 134706, 132933],
                Trigger.POPULATION("Tourists", Region.OW, 300),
                {"Timber", "Bricks"}, "Farmers", set(), "Jam"),

    A1800Unlock("Cafe", DLC.TOURIST_SEASON, Region.OW, 132782, 132782,
                Trigger.POPULATION("Tourists", Region.OW, 550),
                {"Timber", "Bricks"}, set(), set(), "Cafe (Blank)"),

    A1800Unlock("Cafe: Donut Fourre", DLC.TOURIST_SEASON, Region.OW,
                [132753, RECIPE_GUIDS["Recipe: Donut Fourre"][0]], 132753,
                Trigger.UNLOCK("Cafe", Region.OW),
                "Cafe (Blank)", "Tourists", {"Flour", "Tallow", "Jam"}, "Cafe"),

    A1800Unlock("Cafe: Eclair", DLC.TOURIST_SEASON, Region.OW,
                [133347, RECIPE_GUIDS["Recipe: Eclair"][0]], 133347,
                Trigger.LINEAR(
                    Trigger.COUNTER("Cafe", Region.OW, 1, guid=133510),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Supply Tourists with any Cafe (5 min)",
                        134387,
                        {("Tourists", Region.OW), ("Cafe", Region.OW)}
                    )
                ),
                "Cafe (Blank)", "Tourists", {"Flour", "Sugar", "Chocolate"}, "Cafe"),

    A1800Unlock("Cafe: Palmier Biscuit", DLC.TOURIST_SEASON, Region.OW,
                [133348, RECIPE_GUIDS["Recipe: Palmier Biscuit"][0]], 133348,
                Trigger.LINEAR(
                    Trigger.COUNTER("Cafe", Region.OW, 1, guid=133510),
                    Trigger.ANY(
                        Trigger.COUNTER("Zoo", Region.OW, 1, guid=101816, requirements={
                                        ("Expeditions: Level 2", ALL_REGIONS)}),
                        Trigger.COUNTER("Zoo", Region.OW, 1, guid=124109, requirements={
                                        ("Expeditions: Level 3", ALL_REGIONS)}),
                        ap_location_name="Have 1 Elephant Enclosure (Zoo, Eastern Elephant or Elephant)"
                    )
                ),
                "Cafe (Blank)", "Tourists", {"Flour", "Tallow", "Cinnamon"}, "Cafe", is_excluded=True),

    A1800Unlock("Orchard: Coconut Oil", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, Region.NW,
                [133004, 133005, 133010], [133004, 134710, 137179, 137608, 5818, 133010],
                Trigger.ANY(
                    Trigger.POPULATION("Tourists", Region.OW, 850),
                    Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 10),
                    Trigger.POPULATION("Artistas", Region.NW, 2700)),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Coconut Oil", {"Shampoo", "Perfumes"}),

    A1800Unlock("Orchard: Cinnamon", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE}, Region.NW,
                [133030, 133028, 133010], [133030, 134708, 136065, 137608, 133010],
                Trigger.ANY(
                    Trigger.POPULATION("Tourists", Region.OW, 850),
                    Trigger.ANY(
                        Trigger.COUNTER("Engineer Skyscraper: Level 2", Region.OW, 1),
                        Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 1))),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Cinnamon", {"Shampoo", "Chewing Gum"}),

    A1800Unlock("Chemical Plant: Shampoo", DLC.TOURIST_SEASON, Region.OW,
                [132786, 132788, 132771], [134716, 132771, 137608],
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Soap", "Coconut Oil", "Cinnamon"}, "Shampoo", "Shampoo"),

    A1800Unlock("The Iron Tower: Foundations", DLC.TOURIST_SEASON, Region.OW, 132765, 132765,
                Trigger.POPULATION("Tourists", Region.OW, 850),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Workers",
                {"Timber", "Cement"}, "The Iron Tower: Foundations"),

    A1800Unlock("Orchard: Citrus", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, Region.NW,
                [133031, 133029, 133010], [133031, 134707, 136066, 6611, 137607, 133010],
                Trigger.ANY(
                    Trigger.POPULATION("Tourists", Region.OW, 1250),
                    Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                    Trigger.POPULATION("Artistas", Region.NW, 1)),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Citrus", {"Lemonade", "Biscuits", "Mezcal"}),

    A1800Unlock("Chemical Plant: Lemonade", DLC.TOURIST_SEASON, Region.OW,
                [132777, 132778, 132771], [134712, 132771, 137607],
                Trigger.POPULATION("Tourists", Region.OW, 1250),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Saltpetre", "Sugar", "Citrus"}, "Lemonade", "Lemonade"),

    A1800Unlock("Bar", DLC.TOURIST_SEASON, Region.OW, 132781, 132781,
                Trigger.POPULATION("Tourists", Region.OW, 1500),
                {"Timber", "Bricks"}, set(), set(), "Bar (Blank)"),

    A1800Unlock("Bar: Daiquiri Tropic", DLC.TOURIST_SEASON, Region.OW,
                [132752, RECIPE_GUIDS["Recipe: Daiquiri Tropic"][0]], 132752,
                Trigger.UNLOCK("Bar", Region.OW),
                "Bar (Blank)", "Tourists", {"Sugar Cane", "Rum", "Plantains"}, "Bar"),

    A1800Unlock("Bar: Black Muscovy", DLC.TOURIST_SEASON, Region.OW,
                [133342, RECIPE_GUIDS["Recipe: Black Muscovy"][0]], 133342,
                Trigger.LINEAR(Trigger.COUNTER("Bar", Region.OW, 1, guid=133472),
                               Trigger.COUNTER("Members Club", Region.OW, 1)),
                "Bar (Blank)", "Tourists", {"Coffee", "Rum", "Schnapps"}, "Bar"),

    A1800Unlock("Bar: Montmartre '75'", DLC.TOURIST_SEASON, Region.OW,
                [133343, RECIPE_GUIDS["Recipe: Montmartre '75'"][0]], 133343,
                Trigger.LINEAR(Trigger.COUNTER("Bar", Region.OW, 1, guid=133472),
                               Trigger.EVENT_ACTIVE("World's Fair: Exhibitions", Region.OW)),
                "Bar (Blank)", "Tourists", {"Sugar", "Champagne", "Citrus"}, "Bar"),

    A1800Unlock("The Iron Tower: Superstructure", DLC.TOURIST_SEASON, Region.OW, 132766, 132766,
                Trigger.POPULATION("Tourists", Region.OW, 1500),
                "The Iron Tower: Foundations", "Artisans",
                {"Steel Beams", "Reinforced Concrete"}, "The Iron Tower: Superstructure"),

    A1800Unlock("Orchard: Camphor Wax", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, Region.NW,
                [134614, 134615, 133010], [134614, 134709, 137840, 137609, 5812, 133010],
                Trigger.ANY(
                    Trigger.POPULATION("Tourists", Region.OW, 2000),
                    Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                    Trigger.POPULATION("Artistas", Region.NW, 4000)),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Camphor Wax", {"Souvenirs", "Celluloid", "Fans"}),

    A1800Unlock("Chemical Plant: Souvenirs", DLC.TOURIST_SEASON, Region.OW,
                [133533, 133534, 132771], [134717, 132771, 137609],
                Trigger.POPULATION("Tourists", Region.OW, 2000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Engineers",
                {"Glass", "Cotton", "Camphor Wax"}, "Souvenirs", "Souvenirs"),

    A1800Unlock("The Iron Tower", DLC.TOURIST_SEASON, Region.OW, 132770, 132770,
                Trigger.POPULATION("Tourists", Region.OW, 4000),
                "The Iron Tower: Superstructure", set(), set(), "The Iron Tower (Blank)"),

    A1800Unlock("The Iron Tower: Brioche Royale", DLC.TOURIST_SEASON, Region.OW,
                [133928, RECIPE_GUIDS["Recipe: Brioche Royale"][0]], 133928,
                Trigger.COUNTER("The Iron Tower", Region.OW, 1, guid=134450),
                "The Iron Tower (Blank)", {"Tourists", "Electricity"},
                {"Sausages", "Bread", "Beef", "Gold"}, "The Iron Tower"),

    A1800Unlock("The Iron Tower: Trifle Tower", DLC.TOURIST_SEASON, Region.OW,
                [133930, RECIPE_GUIDS["Recipe: Trifle Tower"][0]], 133930,
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", Region.OW, 1, guid=134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Supply Tourists with The Iron Tower (5 min)",
                        134314,
                        {("Tourists", Region.OW), ("The Iron Tower", Region.OW)}
                    )
                ),
                "The Iron Tower (Blank)", {"Tourists", "Electricity"},
                {"Rum", "Bread", "Grapes", "Sugar"}, "The Iron Tower"),

    A1800Unlock("The Iron Tower: Lady Marmelade", DLC.TOURIST_SEASON, Region.OW,
                [133931, RECIPE_GUIDS["Recipe: Lady Marmelade"][0]], 133931,
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", Region.OW, 1, guid=134450),
                    Trigger.ALL(
                        Trigger.COUNTER("Variety Theatre", Region.OW, 3),
                        Trigger.COUNTER("Chemical Plant: Lemonade", Region.OW, 1)
                    )
                ),
                "The Iron Tower (Blank)", {"Tourists", "Electricity"},
                {"Rum", "Champagne", "Citrus", "Jam"}, "The Iron Tower"),

    # Building, Factory, Upgrade
    A1800Unlock("Tourist Mooring", DLC.TOURIST_SEASON, Region.OW, 133890, 133890,
                Trigger.POPULATION("Engineers", Region.OW, 500),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, set(), set(), "Tourist Mooring",
                previous_building="Public Mooring"),

    # Building, Factory, Residence
    A1800Unlock("Hotel", DLC.TOURIST_SEASON, Region.OW, 601445, 601445,
                Trigger.COUNTER("Tourist Mooring", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Medium Storage"}, set(),
                {"Tourist Mooring", "Public Transport"}, "Tourists",
                consumption={"Tourist Mooring", "Bread", "Variety Theatre", "Restaurant", "Jam",
                             "Cafe", "Shampoo", "Bar", "The Iron Tower", "Fire Protection", "Healthcare"},
                luxury={"Fur Coats", "Zoo", "Jewellery", "Lemonade", "Docklands", "Museum",
                        "Botanical Garden", "Palace", "World's Fair", "Souvenirs", "Skyline Tower"},
                lifestyle={"Gramophones", "Bombins", "Leather Boots", "Mezcal", "Ice Cream", "Perfumes"}),

    ### Needs The Passage ###
    # Building, Factory
    A1800Unlock("Restaurant: Venison en Croute", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133340, RECIPE_GUIDS["Recipe: Venison en Croute"][0]], 133340,
                Trigger.LINEAR(Trigger.COUNTER("Restaurant", Region.OW, 1, guid=135069),
                               Trigger.COUNTER("Boreas", Region.AR, 1)),
                "Restaurant (Blank)", "Tourists", {"Flour", "Potatoes", "Caribou Meat"}, "Restaurant"),

    A1800Unlock("Cafe: Venison Tartare", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133349, RECIPE_GUIDS["Recipe: Venison Tartare"][0]], [133349, 4839],
                Trigger.LINEAR(Trigger.COUNTER("Cafe", Region.OW, 1, guid=133510),
                               Trigger.COUNTER("Post Office", Region.AR, 1)),
                "Cafe (Blank)", "Tourists", {"Grapes", "Caribou Meat", "Citrus"}, "Cafe"),

    A1800Unlock("Bar: Glogg", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133345, RECIPE_GUIDS["Recipe: Glogg"][0]], 133345,
                Trigger.LINEAR(
                    Trigger.COUNTER("Bar", Region.OW, 1, guid=133472),
                    Trigger.COUNTER_EXPEDITION_SOLVED(
                        "Complete 1 expedition in the Arctic",
                        1,
                        134300,
                        {("Artisans", Region.OW), ("Seafaring", ALL_REGIONS), ("Expeditions: Level 2", ALL_REGIONS)})
                ),  # Require expedition level 2 to reduce RNG factor by allowing for the lowest 2 tiers to be doable
                "Bar (Blank)", "Tourists", {"Whale Oil", "Grapes", "Cinnamon"}, "Bar"),

    A1800Unlock("The Iron Tower: Age of Exploration", DLC.THE_PASSAGE | DLC.TOURIST_SEASON, Region.OW,
                [133932, RECIPE_GUIDS["Recipe: Age of Exploration"][0]], 133932,
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", Region.OW, 1, guid=134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Complete the set 'Polar Circle' in an OW: Zoo (Arctic Fox, Great Auk, Narwhal, Polar Bear, Ringed Seal, Walrus)",
                        134983,
                        {("Zoo", Region.OW), ("Expeditions: Level 3", Region.OW)}
                    )
                ),
                "The Iron Tower (Blank)", {"Tourists", "Electricity"},
                {"Arctic Gas", "Potatoes", "Red Peppers", "Beef"}, "The Iron Tower", is_excluded=True),

    ### Needs Land of Lions ###
    # Building, Factory
    A1800Unlock("Restaurant: Lobster Cheminee", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133341, RECIPE_GUIDS["Recipe: Lobster Cheminee"][0]], 133341,
                Trigger.LINEAR(
                    Trigger.COUNTER("Restaurant", Region.OW, 1, guid=135069),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Supply Scholars with Clay Pipes (5 min)",
                        133994,
                        {("Scholars", Region.OW), ("Clay Pipes", Region.OW)}
                    )
                ),
                "Restaurant (Blank)", "Tourists", {"Lobster", "Citrus", "Tobacco"}, "Restaurant"),

    A1800Unlock("Cafe: Banana Surprise", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133350, RECIPE_GUIDS["Recipe: Banana Surprise"][0]], 133350,
                Trigger.LINEAR(Trigger.COUNTER("Cafe", Region.OW, 1, guid=133510),
                               Trigger.COUNTER_GOOD_IN_REGION("Plantains", ALL_REGIONS, 1, Region.EN)),
                "Cafe (Blank)", "Tourists", {"Goat Milk", "Plantains", "Cinnamon"}, "Cafe"),

    A1800Unlock("Bar: Enbesa Sunrise", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133346, RECIPE_GUIDS["Recipe: Enbesa Sunrise"][0]], 133346,
                Trigger.LINEAR(Trigger.COUNTER("Bar", Region.OW, 1, guid=133472),
                               Trigger.POPULATION_HAPPINESS("Elders", Session.EN, 30, "Elder Residence")),
                "Bar (Blank)", "Tourists", {"Hibiscus Petals", "Rum", "Spices"}, "Bar"),

    A1800Unlock("The Iron Tower: Homard Lit de Terroir", DLC.LAND_OF_LIONS | DLC.TOURIST_SEASON, Region.OW,
                [133933, RECIPE_GUIDS["Recipe: Homard Lit de Terroir"][0]], 133933,
                Trigger.LINEAR(
                    Trigger.COUNTER("The Iron Tower", Region.OW, 1, guid=134450),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Socket a 'Lobsterman' in a Harbourmaster's Office in Enbesa",
                        134984,
                        {("Artisans", Region.OW), ("Elders", Region.EN), ("Harbourmaster's Office", Region.EN)}
                    )
                ),
                "The Iron Tower (Blank)", {"Tourists", "Electricity"},
                {"Lobster", "Sanga Cow", "Potatoes", "Spices"}, "The Iron Tower", is_excluded=True),

    ################################################################################################################
    ### THE_HIGH_LIFE                                                                                            ###
    ################################################################################################################
    # Building, Factory
    A1800Unlock("Assembly Line: Elevators", DLC.THE_HIGH_LIFE, Region.OW,
                [134622, 134621, 134619], 136054,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Electricity"},
                {"Steel", "Wood Veneers", "Steam Motors"}, "Elevators", "Elevators"),

    A1800Unlock("Department Store", DLC.THE_HIGH_LIFE, Region.OW, 135100, 136063,
                Trigger.ANY(Trigger.COUNTER("Engineer Skyscraper: Level 1", Region.OW, 1),
                            Trigger.COUNTER("Investor Skyscraper: Level 1", Region.OW, 1)),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"}, set(),
                set(), "Department Store (Blank)"),

    A1800Unlock("Department Store: Toasters", DLC.THE_HIGH_LIFE, Region.OW,
                [135103, RECIPE_GUIDS["Recipe: Toasters"][0]], 136063,
                Trigger.UNLOCK("Department Store", Region.OW),
                "Department Store (Blank)", {"Artisans", "Electricity"}, {"Filaments", "Steel", "Zinc"}, {"Department Store", "Toasters"}),

    A1800Unlock("Department Store: Vacuum Cleaners", DLC.THE_HIGH_LIFE, Region.OW,
                [135188, RECIPE_GUIDS["Recipe: Vacuum Cleaners"][0]], [135188, 137606],
                Trigger.LINEAR(Trigger.COUNTER("Department Store", Region.OW, 1, guid=135729),
                               Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 5)),
                "Department Store (Blank)", {"Artisans", "Electricity"}, {"Wool", "Celluloid", "Steel"}, {"Department Store", "Vacuum Cleaners"}),

    A1800Unlock("Department Store: Crockery", DLC.THE_HIGH_LIFE, Region.OW,
                [135187, RECIPE_GUIDS["Recipe: Crockery"][0]], [135187, 137603],
                Trigger.LINEAR(Trigger.COUNTER("Department Store", Region.OW, 1, guid=135729),
                               Trigger.OBJECT_POSITION("Members Club", Region.OW, 10, "Pub")),
                "Department Store (Blank)", {"Artisans", "Electricity"}, {"Clay", "Quartz Sand", "Lacquer"}, {"Department Store", "Crockery"}),

    # Orchard: Cinnamon -> Tourist Season

    A1800Unlock("Chemical Plant: Chewing Gum", DLC.THE_HIGH_LIFE, Region.NW,
                [135185, 135223, 135221], 136065,
                Trigger.ANY(Trigger.COUNTER("Engineer Skyscraper: Level 2", Region.OW, 1),
                            Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 1)),
                {"Timber", "Bricks"}, "Obreros",
                {"Caoutchouc", "Sugar", "Cinnamon"}, "Chewing Gum", "Chewing Gum"),

    # Orchard: Citrus -> Tourist Season

    A1800Unlock("Assembly Line: Biscuits", DLC.THE_HIGH_LIFE, Region.OW,
                [135361, 135398, 134619], 136054,
                Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Electricity"},
                {"Tallow", "Flour", "Citrus"}, "Biscuits", "Biscuits"),

    # Orchard: Camphor Wax -> Tourist Season

    A1800Unlock("Chemical Plant: Ethanol", {DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, Region.NW,
                [135134, 135147, 135221], [137841, 5811],
                Trigger.ANY(Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                            Trigger.POPULATION("Artistas", Region.NW, 2700)),
                {"Timber", "Bricks"}, "Obreros",
                {"Wood", "Corn"}, "Ethanol", {"Ethanol", "Perfumes"}),

    A1800Unlock("Chemical Plant: Celluloid", {DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, Region.NW,
                [135224, 135222, 135221], [137840, 5812],
                Trigger.ANY(Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                            Trigger.POPULATION("Artistas", Region.NW, 4000)),
                {"Timber", "Bricks"}, "Obreros",
                {"Cotton", "Camphor Wax", "Ethanol"}, "Celluloid", {"Celluloid", "Fans"}),

    A1800Unlock("Orchard: Cherry Wood", DLC.THE_HIGH_LIFE, Region.OW, [135088, 135090, 132933], 136067,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 1),
                {"Timber", "Bricks"}, "Farmers", set(), "Cherry Wood", "Cognac"),

    A1800Unlock("Artisan's Workshop: Cognac", DLC.THE_HIGH_LIFE, Region.OW,
                [135418, 135419, 135295], [136067],
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Grapes", "Cherry Wood", "Sugar"}, "Cognac", "Cognac"),

    A1800Unlock("Orchard: Resin", DLC.THE_HIGH_LIFE, Region.OW, [135085, 135089, 132933], 137839,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 15),
                {"Timber", "Bricks"}, "Farmers", set(), "Resin", "Lacquer"),

    A1800Unlock("Artisan's Workshop: Lacquer", DLC.THE_HIGH_LIFE, Region.OW,
                [135133, 135146, 135295], 137839,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Quartz Sand", "Resin", "Ethanol"}, "Lacquer", "Lacquer"),

    A1800Unlock("Furniture Store", DLC.THE_HIGH_LIFE, Region.OW, 135099, 136070,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"}, set(),
                set(), "Furniture Store (Blank)"),

    A1800Unlock("Furniture Store: Banker's Lamps", DLC.THE_HIGH_LIFE, Region.OW,
                [135105, RECIPE_GUIDS["Recipe: Banker's Lamps"][0]], 136070,
                Trigger.UNLOCK("Furniture Store", Region.OW),
                "Furniture Store (Blank)", {"Artisans", "Electricity"}, {"Light Bulbs", "Brass", "Glass"}, {"Furniture Store", "Banker's Lamps"}),

    A1800Unlock("Furniture Store: Vanity Screens", DLC.THE_HIGH_LIFE, Region.OW,
                [135121, RECIPE_GUIDS["Recipe: Vanity Screens"][0]], [135121, 137603],
                Trigger.LINEAR(
                    Trigger.COUNTER("Furniture Store", Region.OW, 1, guid=135730),
                    Trigger.ITEM_SET_ACTIVE(
                        "Zoo", Region.OW,
                        "Complete the set 'Eastern Jungle' in an OW: Zoo (Eastern Elephant, Chital, Eastern Water Buffalo, Crocodile, Peacock, Tiger)",
                        191120, {("Expeditions: Level 2", Region.OW)}),
                ),
                "Furniture Store (Blank)", {"Artisans", "Electricity"},
                {"Cotton Fabric", "Cherry Wood", "Lacquer"}, {"Furniture Store", "Vanity Screens"}, is_excluded=True),

    A1800Unlock("Furniture Store: Writing Desks", DLC.THE_HIGH_LIFE, Region.OW,
                [135120, RECIPE_GUIDS["Recipe: Writing Desks"][0]], [135120, 137603],
                Trigger.LINEAR(
                    Trigger.COUNTER("Furniture Store", Region.OW, 1, guid=135730),
                    Trigger.FACTORY_PRODUCTIVITY("Furniture Store: Banker's Lamps", Region.OW, 100),
                ),
                "Furniture Store (Blank)", {"Artisans", "Electricity"}, {"Wood Veneers", "Lacquer", "Brass"}, {"Furniture Store", "Writing Desks"}),

    A1800Unlock("Assembly Line: Typewriters", DLC.THE_HIGH_LIFE, Region.OW,
                [135148, 135149, 134619], 136072,
                Trigger.ANY(Trigger.COUNTER("Engineer Skyscraper: Level 3", Region.OW, 1),
                            Trigger.COUNTER("Investor Skyscraper: Level 4", Region.OW, 1)),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Workers", "Electricity"},
                {"Steel", "Brass", "Lacquer"}, "Typewriters", "Typewriters"),

    A1800Unlock("Artisan's Workshop: Billiard Tables", DLC.THE_HIGH_LIFE, Region.OW,
                [135407, 135416, 135295], 136073,
                Trigger.COUNTER("Investor Skyscraper: Level 4", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Cherry Wood", "Felt", "Celluloid"}, "Billiard Tables", "Billiard Tables"),

    A1800Unlock("Artisan's Workshop: Violins", DLC.THE_HIGH_LIFE, Region.OW,
                [135397, 135417, 135295], 137194,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Steel", "Cherry Wood", "Lacquer"}, "Violins", "Violins"),

    # Orchard: Coconut Oil -> Tourist Season

    A1800Unlock("Drug Store", DLC.THE_HIGH_LIFE, Region.OW, 134629, 137179,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 10),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Medium Storage"}, set(),
                set(), "Drug Store (Blank)"),

    A1800Unlock("Drug Store: Toothpaste", DLC.THE_HIGH_LIFE, Region.OW,
                [134631, RECIPE_GUIDS["Recipe: Toothpaste"][0]], 137179,
                Trigger.UNLOCK("Drug Store", Region.OW),
                "Drug Store (Blank)", {"Artisans", "Electricity"}, {"Coal", "Soap", "Sugar"}, {"Drug Store", "Toothpaste"}),

    A1800Unlock("Drug Store: Detergent", DLC.THE_HIGH_LIFE, Region.OW,
                [135191, RECIPE_GUIDS["Recipe: Detergent"][0]], 135191,
                Trigger.LINEAR(
                    Trigger.COUNTER("Drug Store", Region.OW, 1, guid=135731),
                    Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 40)
                ),
                "Drug Store (Blank)", {"Artisans", "Electricity"}, {"Citrus", "Ethanol", "Saltpetre"}, {"Drug Store", "Detergent"}),

    A1800Unlock("Drug Store: Lipstick", DLC.THE_HIGH_LIFE, Region.OW,
                [135192, RECIPE_GUIDS["Recipe: Lipstick"][0]], [135192, 137603],
                Trigger.LINEAR(
                    Trigger.COUNTER("Drug Store", Region.OW, 1, guid=135731),
                    Trigger.OBJECT_POSITION("Investor Skyscraper: Level 5", Region.OW, 8, "Variety Theatre")
                ),
                "Drug Store (Blank)", {"Artisans", "Electricity"}, {"Coconut Oil", "Fish Oil", "Lacquer"}, {"Drug Store", "Lipstick"}),

    A1800Unlock("Artisan's Workshop: Toys", DLC.THE_HIGH_LIFE, Region.OW,
                [135669, 135670, 135295], 137195,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, "Artisans",
                {"Felt", "Celluloid", "Lacquer"}, "Toys", "Toys"),

    A1800Unlock("Skyline Tower: Foundations", DLC.THE_HIGH_LIFE, Region.OW, 403, 403,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 25),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators", "Grand Storage"}, "Workers",
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"},
                "Skyline Tower: Foundations"),

    A1800Unlock("Skyline Tower: Superstructure", DLC.THE_HIGH_LIFE, Region.OW, 404, 404,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 40),
                "Skyline Tower: Foundations", "Workers",
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"},
                "Skyline Tower: Superstructure"),

    A1800Unlock("Skyline Tower: Glazing", DLC.THE_HIGH_LIFE, Region.OW, 135709, 135709,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 55),
                "Skyline Tower: Superstructure", "Workers",
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"},
                "Skyline Tower: Glazing"),

    # Building, Factory, Residence
    A1800Unlock("Skyline Tower", DLC.THE_HIGH_LIFE, Region.OW, 406, 406,
                Trigger.COUNTER("Investor Skyscraper: Level 5", Region.OW, 75),
                "Skyline Tower: Glazing", set(), set(), {"Skyline Tower"},
                consumption={"Spectacles", "Coffee", "Electricity", "Light Bulbs", "Champagne", "Cigars", "Chocolate",
                             "Steam Carriages", "Fire Protection", "Riot Control", "Healthcare"},
                luxury={"Penny Farthings", "Pocket Watches", "Bank", "Members Club", "Jewellery", "Gramophones"},
                lifestyle={"Toasters", "Vacuum Cleaners", "Crockery", "Refrigerators", "Briefcases", "Banker's Lamps",
                           "Vanity Screens", "Writing Desks", "Four-Poster Beds", "Lounge Seating", "Toothpaste",
                           "Detergent", "Lipstick", "Face Cream", "Pomade"}),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Engineer Skyscraper: Level 1", DLC.THE_HIGH_LIFE, Region.OW, 601888, 601888,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Engineers", "", "Engineer Residence", {"Department Store"}),

    A1800Unlock("Engineer Skyscraper: Level 2", DLC.THE_HIGH_LIFE, Region.OW, 601889, 601889,
                Trigger.ANY(Trigger.COUNTER("Engineer Skyscraper: Level 1", Region.OW, 1),
                            Trigger.COUNTER("Investor Skyscraper: Level 1", Region.OW, 1)),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Engineers", "", "Engineer Skyscraper: Level 1", {"Chewing Gum", "Furniture Store"}),

    A1800Unlock("Engineer Skyscraper: Level 3", DLC.THE_HIGH_LIFE, Region.OW, 601890, 601890,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Engineers", "", "Engineer Skyscraper: Level 2", {"Typewriters", "Drug Store", "Violins"}),

    A1800Unlock("Investor Skyscraper: Level 1", DLC.THE_HIGH_LIFE, Region.OW, 601882, 601882,
                Trigger.POPULATION("Investors", Region.OW, 5000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Investors", "", "Investor Residence", {"Department Store"}),

    A1800Unlock("Investor Skyscraper: Level 2", DLC.THE_HIGH_LIFE, Region.OW, 601883, 601883,
                Trigger.ANY(Trigger.COUNTER("Engineer Skyscraper: Level 1", Region.OW, 1),
                            Trigger.COUNTER("Investor Skyscraper: Level 1", Region.OW, 1)),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Investors", "", "Investor Skyscraper: Level 1", {"Chewing Gum", "Biscuits"}),

    A1800Unlock("Investor Skyscraper: Level 3", DLC.THE_HIGH_LIFE, Region.OW, 601884, 601884,
                Trigger.COUNTER("Investor Skyscraper: Level 2", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Investors", "", "Investor Skyscraper: Level 2", {"Cognac", "Furniture Store"}),

    A1800Unlock("Investor Skyscraper: Level 4", DLC.THE_HIGH_LIFE, Region.OW, 601886, 601886,
                Trigger.COUNTER("Investor Skyscraper: Level 3", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Investors", "", "Investor Skyscraper: Level 3", {"Typewriters", "Billiard Tables"}),

    A1800Unlock("Investor Skyscraper: Level 5", DLC.THE_HIGH_LIFE, Region.OW, 601891, 601891,
                Trigger.COUNTER("Investor Skyscraper: Level 4", Region.OW, 15),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete", "Elevators"}, set(),
                set(), "Investors", "", "Investor Skyscraper: Level 4", {"Violins", "Drug Store", "Toys"}),

    ### Needs The Passage ###
    # Building, Factory
    A1800Unlock("Department Store: Refrigerators", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW,
                [135189, RECIPE_GUIDS["Recipe: Refrigerators"][0]], 135189,
                Trigger.LINEAR(
                    Trigger.COUNTER("Department Store", Region.OW, 1, guid=135729),
                    Trigger.QUEST_COMPLETE(
                        "Hidden quest: Socket 'The \"Magnificone\" Ice Cream Maker' in an OW: Town Hall (see Arctic Nate)",
                        135736,
                        {("Expedition: The Arctic", ALL_REGIONS), ("Expeditions: Level 2", ALL_REGIONS),
                         ("Aviation", ALL_REGIONS), ("Lost Expedition Scrap", ALL_REGIONS), ("Grapes", ALL_REGIONS),
                         ("Plantains", ALL_REGIONS), ("Chocolate", ALL_REGIONS), ("Investors", Region.OW),
                         ("Town Hall", Region.OW)}
                    )
                ),
                "Department Store (Blank)", {"Artisans", "Electricity"}, {"Arctic Gas", "Steel", "Caoutchouc"}, {"Department Store", "Refrigerators"}),

    A1800Unlock("Furniture Store: Four-Poster Beds", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW,
                [135122, RECIPE_GUIDS["Recipe: Four-Poster Beds"][0]], 135122,
                Trigger.LINEAR(
                    Trigger.COUNTER("Furniture Store", Region.OW, 1, guid=135730),
                    Trigger.ALL(
                        Trigger.COUNTER_GOOD_IN_REGION("Bear Fur", ALL_REGIONS, 1, Region.OW),
                        Trigger.COUNTER_GOOD_IN_REGION("Goose Feathers", ALL_REGIONS, 1, Region.OW))
                ),
                "Furniture Store (Blank)", {"Artisans", "Electricity"},
                {"Cherry Wood", "Bear Fur", "Goose Feathers"}, {"Furniture Store", "Four-Poster Beds"}),

    A1800Unlock("Drug Store: Face Cream", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW,
                [135193, RECIPE_GUIDS["Recipe: Face Cream"][0]], [135193, 137603],
                Trigger.LINEAR(
                    Trigger.COUNTER("Drug Store", Region.OW, 1, guid=135731),
                    Trigger.ITEM_SET_ACTIVE(
                        "Museum", Region.OW,
                        "Complete the set 'Icebound' in an OW: Museum (Collection Of Lost Expedition Relics, Frozen Woolly Mammoth, Wolf Pup Mummy)",
                        193776, {("Expeditions: Level 3", Region.OW)}),
                ),
                "Drug Store (Blank)", {"Artisans", "Electricity"},
                {"Whale Oil", "Coconut Oil", "Citrus"}, {"Drug Store", "Face Cream"}, is_excluded=True),

    ### Needs Land of Lions ###
    # Building, Factory
    A1800Unlock("Department Store: Briefcases", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW,
                [135190, RECIPE_GUIDS["Recipe: Briefcases"][0]], [135190, 137606],
                Trigger.LINEAR(Trigger.COUNTER("Department Store", Region.OW, 1, guid=135729),
                               Trigger.OBJECT_POSITION("Scholar Residence", Region.OW, 8, "Department Store")),
                "Department Store (Blank)", {"Artisans", "Electricity"}, {"Sanga Cow", "Brass", "Celluloid"}, {"Department Store", "Briefcases"}),

    A1800Unlock("Furniture Store: Lounge Seating", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW,
                [135123, RECIPE_GUIDS["Recipe: Lounge Seating"][0]], 135123,
                Trigger.LINEAR(
                    Trigger.COUNTER("Furniture Store", Region.OW, 1, guid=135730),
                    Trigger.COUNTER("Radio Tower", Region.OW, 2)
                ),
                "Furniture Store (Blank)", {"Artisans", "Electricity"},
                {"Wool", "Sanga Cow", "Wanza Timber"}, {"Furniture Store", "Lounge Seating"}),

    A1800Unlock("Drug Store: Pomade", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW,
                [135194, RECIPE_GUIDS["Recipe: Face Cream"][0]], 135194,
                Trigger.LINEAR(
                    Trigger.COUNTER("Drug Store", Region.OW, 1, guid=135731),
                    Trigger.OBJECT_POSITION("Apiary", Region.EN, 8, "Hibiscus Farm")
                ),
                "Drug Store (Blank)", {"Artisans", "Electricity"},
                {"Beeswax", "Camphor Wax", "Hibiscus Petals"}, {"Drug Store", "Pomade"}),

    ################################################################################################################
    ### SEEDS_OF_CHANGE                                                                                          ###
    ################################################################################################################
    # Building
    A1800Unlock("Hacienda Paving", DLC.SEEDS_OF_CHANGE, Region.NW, 24770, 25055,
                Trigger.POPULATION("Obreros", Region.NW, 1), type=UnlockType.BUILDING),

    A1800Unlock("Hacienda Pathway", DLC.SEEDS_OF_CHANGE, Region.NW, 25224, 25055,
                Trigger.POPULATION("Obreros", Region.NW, 1), type=UnlockType.BUILDING),

    # Building, Factory
    A1800Unlock("Fertiliser Silo", DLC.SEEDS_OF_CHANGE, Region.OW, 25240, 25054,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Timber", "Bricks"}, set(), "Fertiliser"),

    A1800Unlock("Hacienda", DLC.SEEDS_OF_CHANGE, Region.NW, 24768, [25055, 25546],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Timber", "Bricks"}, set(), set(), "Hacienda"),

    A1800Unlock("Hacienda Storeroom", DLC.SEEDS_OF_CHANGE, Region.NW, 24775, 25055,
                Trigger.POPULATION("Obreros", Region.NW, 1), {"Timber", "Bricks"}, "Hacienda", output={"Medium Storage", "Large Storage"}),

    A1800Unlock("Hacienda Sugar Cane Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [24798, 24796, 24794], [24796, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Sugar Cane"),

    A1800Unlock("Hacienda Corn Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25003, 25010, 24794], [25010, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Corn"),

    A1800Unlock("Hacienda Caoutchouc Plantation", DLC.SEEDS_OF_CHANGE, Region.NW, [25006, 25013, 24794], [25013, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Caoutchouc"),

    A1800Unlock("Hacienda Potato Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25019, 25023, 24794], [25023, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Potatoes"),

    A1800Unlock("Hacienda Spice Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25020, 25024, 24794], [25024, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Spices"),

    A1800Unlock("Hacienda Grain Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25128, 25349, 24794], [25349, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", {"Jornaleros", "Hacienda"}, output="Grain"),

    A1800Unlock("Hacienda Rum Distillery", DLC.SEEDS_OF_CHANGE, Region.NW, [24801, 24803, 24800], [24803, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                "Timber", {"Jornaleros", "Hacienda"}, {"Wood", "Sugar Cane"}, "Rum"),

    A1800Unlock("Hacienda Atole Maker", DLC.SEEDS_OF_CHANGE, Region.NW, [25126, 25130, 24800], [25130, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                "Timber", {"Jornaleros", "Hacienda"}, {"Corn", "Sugar Cane"}, "Atole"),

    A1800Unlock("Hacienda Schnapps Distillery", DLC.SEEDS_OF_CHANGE, Region.NW, [25350, 25351, 24800], [25351, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                "Timber", {"Jornaleros", "Hacienda"}, "Potatoes", "Schnapps"),

    A1800Unlock("Hacienda Hot Sauce Factory", DLC.SEEDS_OF_CHANGE, Region.NW, [25508, 25507, 24800], [25507, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 1),
                "Timber", {"Jornaleros", "Hacienda"}, "Spices", "Hot Sauce"),

    A1800Unlock("Hacienda Fertiliser Works", DLC.SEEDS_OF_CHANGE, Region.NW, 24805, 25054,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Steel Beams", "Steam Motors"}, {"Jornaleros", "Hacienda"}, "Dung", "Fertiliser"),

    A1800Unlock("Fertiliser Silo", DLC.SEEDS_OF_CHANGE, Region.NW, 25241, 25054,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Timber", "Bricks"}, set(), "Fertiliser"),

    A1800Unlock("Hacienda Coffee Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25005, 25012, 24794], [25005, 25012, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 300), "Timber", {"Jornaleros", "Hacienda"}, output="Coffee Beans"),

    A1800Unlock("Hacienda Cocoa Farm", DLC.SEEDS_OF_CHANGE, Region.NW, [25009, 25015, 24794], [25009, 25015, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 600), "Timber", {"Jornaleros", "Hacienda"}, output="Cocoa"),

    A1800Unlock("Hacienda Beer Brewery", DLC.SEEDS_OF_CHANGE, Region.NW, [25064, 25062, 24800], [25064, 25062, 25055],
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Timber", {"Jornaleros", "Hacienda"}, {"Grain", "Corn"}, "Beer"),

    # Building, Factory, Residence
    A1800Unlock("Hacienda Jornalero Quarters", DLC.SEEDS_OF_CHANGE, Region.NW, 24792, [25055, 24792],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", set(), {"Hacienda", "Jornaleros"}, "Jornaleros",
                consumption={"Hacienda", "Fried Plantains", "Ponchos",
                             "Schnapps", "Hot Sauce", "Fire Protection", "Riot Control"},
                luxury={"Rum", "Chapel"},
                lifestyle={"Work Clothes", "Felt", "Teff", "Local Mail",
                           "Regional Mail", "Overseas Mail", "Soccer Balls", "Beach", "Cinema"}),

    A1800Unlock("Hacienda Obrera Quarters", DLC.SEEDS_OF_CHANGE, Region.NW, 24793, [25055, 24793],
                Trigger.POPULATION("Obreros", Region.NW, 1), "Timber", set(), {"Hacienda", "Obreros"}, "Obreros",
                consumption={"Hacienda", "Fried Plantains", "Ponchos", "Tortillas", "Hot Sauce", "Atole", "Coffee", "Bombins",
                             "Sewing Machines", "Fire Protection", "Riot Control", "Healthcare"},
                luxury={"Rum", "Chapel", "Boxing Arena", "Beer", "Cigars"},
                lifestyle={"Spectacles", "Typewriters", "Illuminated Script", "Local Mail",
                           "Regional Mail", "Overseas Mail", "Beach", "Samba School", "Scooters"}),

    ### Needs Land of Lions ###
    # Building, Factory
    A1800Unlock("Fertiliser Silo", DLC.LAND_OF_LIONS | DLC.SEEDS_OF_CHANGE, Region.EN, 25242, 25054,
                Trigger.POPULATION("Obreros", Region.NW, 1),
                {"Wanza Timber", "Mud Bricks"}, set(), "Fertiliser"),

    ################################################################################################################
    ### EMPIRE_OF_THE_SKIES                                                                                      ###
    ################################################################################################################
    # Meta
    A1800Unlock("Postal Service OW => OW", DLC.EMPIRE_OF_THE_SKIES, Region.OW,
                input={("Aviation", Region.OW), ("Local Mail", Region.OW), ("Airship Platform", Region.OW),
                       ("Airmail Sorting Office", Region.OW)},
                output="Regional Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service OW => NW", DLC.EMPIRE_OF_THE_SKIES, Region.NW,
                input={("Aviation", Region.OW | Region.NW), ("Local Mail", Region.OW),
                       ("Airship Platform", Region.OW), ("Airship Platform", Region.NW),
                       ("Airmail Sorting Office", Region.OW), ("Airmail Sorting Office", Region.NW)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service NW => NW", DLC.EMPIRE_OF_THE_SKIES, Region.NW,
                input={("Aviation", Region.NW), ("Local Mail", Region.NW), ("Airship Platform", Region.NW),
                       ("Airmail Sorting Office", Region.NW)},
                output="Regional Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service NW => OW", DLC.EMPIRE_OF_THE_SKIES, Region.OW,
                input={("Aviation", Region.OW | Region.NW), ("Local Mail", Region.NW),
                       ("Airship Platform", Region.OW), ("Airship Platform", Region.NW),
                       ("Airmail Sorting Office", Region.OW), ("Airmail Sorting Office", Region.NW)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    # Building
    A1800Unlock("Flak Emplacement", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 736, 736,
                Trigger.POPULATION("Workers", Region.OW, 300), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Item Transfer Depot", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 964, 1989,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks", "Steel Beams"}),

    A1800Unlock("Flak Emplacement", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 742, 742,
                Trigger.POPULATION("Jornaleros", Region.NW, 200), {"Timber", "Bricks", "Weapons"}),

    A1800Unlock("Item Transfer Depot", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 2274, 1988,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks"}),

    A1800Unlock("Commuter Station", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 967, 1988,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks"}),

    # Building, Factory
    A1800Unlock("Post Box", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 538, 4320,
                Trigger.POPULATION("Artisans", Region.OW, 500),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Workers", set(), "Local Mail"),

    A1800Unlock("Post Office", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 3741, 4320,
                Trigger.POPULATION("Artisans", Region.OW, 500),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Workers", set(), "Local Mail"),

    A1800Unlock("Rigid Airship Hangar: Foundations", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 648, 676,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Workers",
                {"Timber", "Bricks"}, "Rigid Airship Hangar: Foundations"),

    A1800Unlock("Rigid Airship Hangar: Structure", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 649, 676,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Foundations", "Workers",
                {"Bricks", "Aluminium Profiles"}, "Rigid Airship Hangar: Structure"),

    A1800Unlock("Rigid Airship Hangar: Roof", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 651, 676,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Structure", "Workers",
                {"Aluminium Profiles", "Windows"}, "Rigid Airship Hangar: Roof"),

    A1800Unlock("Rigid Airship Hangar", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 636, 676,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Roof", "Workers",
                set(), {"Airships", "Arctic Airships"}),

    A1800Unlock("Airship Platform", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 962, 1989,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks", "Aluminium Profiles"}, output="Airship Platform"),

    A1800Unlock("Bomb Factory", DLC.EMPIRE_OF_THE_SKIES, Region.OW, [924, 940, 923], 2040,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Aluminium Profiles"}, "Workers",
                {"Saltpetre", "Dynamite", "Steel"}, "Bombs"),

    A1800Unlock("Sea Mine Factory", DLC.EMPIRE_OF_THE_SKIES, Region.OW, [934, 953, 923], 2040,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Aluminium Profiles"}, "Workers",
                {"Copper", "Dynamite", "Steel"}, "Sea Mines"),

    A1800Unlock("Pamphlet Printer", DLC.EMPIRE_OF_THE_SKIES, Region.OW, [935, 954, 923], 2040,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Aluminium Profiles"}, "Workers",
                {"Wood", "Cotton"}, "Pamphlets"),

    A1800Unlock("Care Package Factory", DLC.EMPIRE_OF_THE_SKIES, Region.OW, [936, 955, 923], 2040,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Aluminium Profiles"}, "Workers",
                {"Canned Food", "Chocolate", "Schnapps"}, "Care Packages"),

    A1800Unlock("Water Drop Factory", DLC.EMPIRE_OF_THE_SKIES, Region.OW, [937, 956, 923], 2040,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Steel Beams", "Aluminium Profiles"}, "Workers",
                set(), "Water Drop"),

    A1800Unlock("Airmail Sorting Office", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 966, 4321,
                Trigger.POPULATION("Obreros", Region.NW, 1000),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, output="Airmail Sorting Office"),

    A1800Unlock("Post Box", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 3661, 4324,
                Trigger.POPULATION("Obreros", Region.NW, 250),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Obreros", set(), "Local Mail"),

    A1800Unlock("Post Office", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 3761, 4324,
                Trigger.POPULATION("Obreros", Region.NW, 250),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Obreros", set(), "Local Mail"),

    A1800Unlock("Charcoal Kiln", {DLC.EMPIRE_OF_THE_SKIES, DLC.NEW_WORLD_RISING}, Region.NW, 1345, [1352, 7221],
                Trigger.ANY(Trigger.POPULATION("Obreros", Region.NW, 250),
                            Trigger.POPULATION("Artistas", Region.NW, 1)),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Coal", {"Aluminium Profiles", "Sewing Machines"}),

    A1800Unlock("Bauxite Mine", {DLC.EMPIRE_OF_THE_SKIES, DLC.NEW_WORLD_RISING}, Region.NW, 1308, [1352, 7221],
                Trigger.ANY(Trigger.POPULATION("Obreros", Region.NW, 250),
                            Trigger.POPULATION("Artistas", Region.NW, 1)),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Bauxite", {"Aluminium Profiles", "Sewing Machines"}),

    A1800Unlock("Aluminium Smelter", {DLC.EMPIRE_OF_THE_SKIES, DLC.NEW_WORLD_RISING}, Region.NW, 835, [1352, 7221],
                Trigger.ANY(Trigger.POPULATION("Obreros", Region.NW, 250),
                            Trigger.POPULATION("Artistas", Region.NW, 1)),
                "Timber", "Obreros", {"Coal", "Bauxite"},
                "Aluminium Profiles", {"Aluminium Profiles", "Sewing Machines"}),

    A1800Unlock("Industrial Oil Press", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 1418, 1355,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks"}, "Jornaleros",
                {"Fish Oil", "Saltpetre"}, "Industrial Lubricant", "Helium"),

    A1800Unlock("Helium Extractor", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 1353, 1355,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Obreros",
                {"Industrial Lubricant", "Clay"}, "Helium", "Helium"),

    A1800Unlock("Rigid Airship Hangar: Foundations", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 692, 696,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Timber", "Bricks"}, "Rigid Airship Hangar: Foundations"),

    A1800Unlock("Rigid Airship Hangar: Structure", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 693, 696,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Foundations", "Jornaleros",
                {"Bricks", "Aluminium Profiles"}, "Rigid Airship Hangar: Structure"),

    A1800Unlock("Rigid Airship Hangar: Roof", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 695, 696,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Structure", "Obreros",
                {"Aluminium Profiles", "Sails"}, "Rigid Airship Hangar: Roof"),

    A1800Unlock("Rigid Airship Hangar", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 635, 696,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                "Rigid Airship Hangar: Roof", "Obreros",
                set(), {"Airships", "Arctic Airships"}),

    A1800Unlock("Airship Platform", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 963, 1988,
                Trigger.POPULATION("Obreros", Region.NW, 600), {"Timber", "Bricks", "Aluminium Profiles"}, output="Airship Platform"),

    A1800Unlock("Bomb Factory", DLC.EMPIRE_OF_THE_SKIES, Region.NW, [906, 868, 905], 2041,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Saltpetre", "Dynamite", "Steel"}, "Bombs"),

    A1800Unlock("Sea Mine Factory", DLC.EMPIRE_OF_THE_SKIES, Region.NW, [907, 918, 905], 2041,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Copper", "Dynamite", "Steel"}, "Sea Mines"),

    A1800Unlock("Pamphlet Printer", DLC.EMPIRE_OF_THE_SKIES, Region.NW, [908, 919, 905], 2041,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Wood", "Cotton"}, "Pamphlets"),

    A1800Unlock("Care Package Factory", DLC.EMPIRE_OF_THE_SKIES, Region.NW, [916, 921, 905], 2041,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Canned Food", "Chocolate", "Schnapps"}, "Care Packages"),

    A1800Unlock("Water Drop Factory", DLC.EMPIRE_OF_THE_SKIES, Region.NW, [915, 922, 905], 2041,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                set(), "Water Drop"),

    A1800Unlock("Airmail Sorting Office", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 2276, 4321,
                Trigger.POPULATION("Obreros", Region.NW, 1000), {"Timber", "Bricks"}, output="Airmail Sorting Office"),

    # Factory
    A1800Unlock("Flak Monitor", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 720, 720,
                Trigger.POPULATION("Engineers", Region.OW, 1),
                input={"Steam Ships", "Steel Beams", "Steam Motors", "Advanced Weapons"}, output={"Seafaring", "Expeditions: Level 2"}, ap_region=Region.OW),

    A1800Unlock("Colibri", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1654, 2011,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                input={"Airships", "Aluminium Profiles", "Sails", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Colibri (Armed)", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1054, 2011,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                input={"Airships", "Aluminium Profiles", "Sails", "Helium", "Weapons"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Atotolin", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1058, 2011,
                Trigger.POPULATION("Obreros", Region.NW, 600),
                input={"Airships", "Aluminium Profiles", "Sails", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Alicanto", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1655, 2012,
                Trigger.ALL(Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Alicanto (Armed)", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1056, 2012,
                Trigger.ALL(Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Helium", "Weapons"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Dtundtuncan", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1059, 2012,
                Trigger.ALL(Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Quetzalcoatl", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1060, 2012,
                Trigger.ALL(Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    ### Needs The Passage ###
    # Meta
    A1800Unlock("Postal Service OW => AR", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR,
                input={("Aviation", Region.OW | Region.AR), ("Local Mail", Region.OW),
                       ("Airship Platform", Region.OW), ("Airship Platform", Region.AR),
                       ("Airmail Sorting Office", Region.OW), ("Airmail Sorting Office", Region.AR)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service NW => AR", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR,
                input={("Aviation", Region.NW | Region.AR), ("Local Mail", Region.NW),
                       ("Airship Platform", Region.NW), ("Airship Platform", Region.AR),
                       ("Airmail Sorting Office", Region.NW), ("Airmail Sorting Office", Region.AR)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service AR => AR", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR,
                input={("Aviation", Region.AR), ("Local Mail", Region.AR), ("Airship Platform", Region.AR),
                       ("Airmail Sorting Office", Region.AR)},
                output="Regional Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service AR => OW", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.OW,
                input={("Aviation", Region.OW | Region.AR), ("Local Mail", Region.AR),
                       ("Airship Platform", Region.OW), ("Airship Platform", Region.AR),
                       ("Airmail Sorting Office", Region.OW), ("Airmail Sorting Office", Region.AR)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Postal Service AR => NW", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.NW,
                input={("Aviation", Region.NW | Region.AR), ("Local Mail", Region.AR),
                       ("Airship Platform", Region.NW), ("Airship Platform", Region.AR),
                       ("Airmail Sorting Office", Region.NW), ("Airmail Sorting Office", Region.AR)},
                output="Overseas Mail", type=UnlockType.META | UnlockType.FACTORY),

    # Building
    A1800Unlock("Flak Emplacement", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 822, 822,
                Trigger.POPULATION("Technicians", Region.AR, 1), {"Timber", "Bricks", "Weapons"}),

    # Building, Factory
    A1800Unlock("Airship Platform", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 4258, 4532,
                Trigger.POPULATION("Technicians", Region.AR, 100), {"Timber", "Bricks"}, output="Airship Platform"),

    A1800Unlock("Airmail Sorting Office", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, [4259, 4513], 4532,
                Trigger.POPULATION("Technicians", Region.AR, 100), {"Timber", "Bricks"}, output="Airmail Sorting Office"),

    # Factory
    A1800Unlock("Mapinguari", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1755, 3369,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                input={"Airships", "Timber", "Sails", "Steam Motors", "Helium"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Harpy", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1733, 3369,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                input={"Airships", "Aluminium Profiles", "Sails", "Arctic Gas"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Harpy (Armed)", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1731, 3369,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                input={"Airships", "Aluminium Profiles", "Sails", "Arctic Gas", "Weapons"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Hermes", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1735, 3369,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 600)),
                input={"Airships", "Aluminium Profiles", "Sails", "Arctic Gas"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Manticore", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1734, 3370,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Arctic Gas"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Manticore (Armed)", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1732, 3370,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Arctic Gas", "Weapons"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Pegasus", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1736, 3370,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Arctic Gas"}, output={"Aviation"}, ap_region=Region.OW),

    A1800Unlock("Zephyr", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1737, 3370,
                Trigger.ALL(Trigger.COUNTER("Arctic Airship Hangar", Region.AR, 1),
                            Trigger.POPULATION("Obreros", Region.NW, 1500),
                            Trigger.POPULATION("Engineers", Region.OW, 500)),
                input={"Airships", "Aluminium Profiles", "Steam Motors", "Arctic Gas"}, output={"Aviation"}, ap_region=Region.OW),

    ### Needs Land of Lions ###
    # Building
    A1800Unlock("Flak Emplacement", DLC.LAND_OF_LIONS | DLC.EMPIRE_OF_THE_SKIES, Region.EN, 743, 743,
                Trigger.POPULATION("Shepherds", Region.EN, 50), {"Wanza Timber", "Mud Bricks", "Weapons"}),

    ################################################################################################################
    ### NEW_WORLD_RISING                                                                                         ###
    ################################################################################################################
    A1800Unlock("Electrified Nandu Farm", DLC.NEW_WORLD_RISING, Region.NW,
                input={"Nandu Farm", "Electricity"}, output="Nandu Feathers",
                type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Electrified Cattle Farm", DLC.NEW_WORLD_RISING, Region.NW,
                input={"Cattle Farm", "Electricity"}, output="Milk", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Electrified Alpaca Farm", DLC.NEW_WORLD_RISING, Region.NW,
                input={"Alpaca Farm", "Electricity"}, output="Saltpetre", type=UnlockType.META | UnlockType.FACTORY),

    A1800Unlock("Dam: Foundations", DLC.NEW_WORLD_RISING, Region.NW,
                input={"Jornaleros", "Timber", "Bricks"}, output="Dam: Foundations",
                type=UnlockType.META | UnlockType.FACTORY),

    # Building, Factory
    A1800Unlock("Fire Department", DLC.NEW_WORLD_RISING, Region.OW, 6354, 7333,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Timber", set(), "Fire Extinguishers", "Fire Protection", "", "Fire Station"),

    A1800Unlock("Police Headquarters", DLC.NEW_WORLD_RISING, Region.OW, 6353, 7336,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks"}, set(), "Police Equipment", "Riot Control", "", "Police Station"),

    A1800Unlock("City Hospital", DLC.NEW_WORLD_RISING, Region.OW, 6355, 7337,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                {"Timber", "Bricks", "Steel Beams"}, set(), "Medicine", "Healthcare", "", "Hospital"),

    # Charcoal Kiln -> Empire of the Skies

    # Bauxite Mine -> Empire of the Skies

    # Aluminium Smelter -> Empire of the Skies

    A1800Unlock("Sewing Machine Factory", DLC.NEW_WORLD_RISING, Region.NW, 6083, 7221,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                {"Timber", "Bricks"}, "Artistas",
                {"Wood", "Aluminium Profiles"}, "Sewing Machines", "Sewing Machines (Aluminium)"),

    A1800Unlock("Nandu Farm", DLC.NEW_WORLD_RISING, Region.NW, [5457, 8026], 5800,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                "Timber", "Jornaleros", set(), {"Nandu Leather", "Nandu Farm"}, "Ballsports"),

    A1800Unlock("Ball Manufactory", DLC.NEW_WORLD_RISING, Region.NW, 5879, 5807,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                "Timber", "Jornaleros", {"Nandu Leather", "Caoutchouc"}, "Soccer Balls", "Ballsports"),

    # Orchard: Citrus -> Tourist Season or The High Life

    A1800Unlock("Herb Garden", DLC.NEW_WORLD_RISING, Region.NW, [5463, 5464], 6611,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                "Timber", "Jornaleros", set(), "Herbs", "Mezcal"),

    A1800Unlock("Mezcal Bar", DLC.NEW_WORLD_RISING, Region.NW, 6594, 6611,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artistas",
                {"Citrus", "Sugar", "Herbs"}, "Mezcal", "Mezcal"),

    A1800Unlock("Calamari Fishery", DLC.NEW_WORLD_RISING, Region.NW, 7919, 5802,
                Trigger.POPULATION("Artistas", Region.NW, 900),
                "Timber", "Jornaleros", set(), "Calamari", "Jalea"),

    A1800Unlock("Jalea Kitchen", DLC.NEW_WORLD_RISING, Region.NW, 5458, 5802,
                Trigger.POPULATION("Artistas", Region.NW, 900),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artistas",
                {"Calamari", "Herbs", "Corn"}, "Jalea", "Jalea"),

    A1800Unlock("Power Station", DLC.NEW_WORLD_RISING, Region.NW, 5164, [5164, 7305],
                Trigger.POPULATION("Artistas", Region.NW, 900),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"},
                {"Obreros", "Railway", "Oil Harbour"}, "Oil", "Electricity",
                "Electricity (Artistas)"),

    A1800Unlock("Ice Cream Factory", DLC.NEW_WORLD_RISING, Region.NW, 5459, 5801,
                Trigger.POPULATION("Artistas", Region.NW, 1800),
                {"Timber", "Bricks"}, "Artistas", {"Milk", "Chocolate", "Citrus"}, "Ice Cream", "Ice Cream"),

    A1800Unlock("Beach", DLC.NEW_WORLD_RISING, Region.NW, [6264, 7085, 7178, 7179, 7180, 7181, 7879, 7880, 7895], 5801,
                Trigger.POPULATION("Artistas", Region.NW, 1800), "Timber", output="Beach"),

    # Orchard: Coconut Oil -> Tourist Season or The High Life

    # Chemical Plant: Ethanol -> The High Life

    A1800Unlock("Orchid Farm", DLC.NEW_WORLD_RISING, Region.NW, [5814, 5815], 5818,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Timber", "Jornaleros", set(), "Orchid", "Perfumes"),

    A1800Unlock("Perfume Mixer", DLC.NEW_WORLD_RISING, Region.NW, 5657, 5818,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artistas",
                {"Orchid", "Ethanol", "Coconut Oil"}, "Perfumes", "Perfumes"),

    A1800Unlock("Mineral Mine", DLC.NEW_WORLD_RISING, Region.NW, 1390, 5931,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Obreros", set(), "Minerals", "Samba School"),

    A1800Unlock("Laboratory: Pigments", DLC.NEW_WORLD_RISING, Region.NW, [5462, 7000], 5931,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Artistas",
                {"Minerals", "Saltpetre"}, "Pigments", "Samba School"),

    A1800Unlock("Costume Shop", DLC.NEW_WORLD_RISING, Region.NW, 5933, 5931,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks", "Steel Beams", "Windows"}, "Artistas",
                {"Cotton Fabric", "Pigments", "Nandu Feathers"}, "Costumes", "Samba School"),

    A1800Unlock("Samba School", DLC.NEW_WORLD_RISING, Region.NW, 5840, 5931,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks"}, "Artistas", "Costumes", "Samba School", "Samba School"),

    A1800Unlock("Iron Mine", DLC.NEW_WORLD_RISING, Region.NW, 1388, 7348,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks"}, "Jornaleros", set(), "Iron", "Fire Department"),

    A1800Unlock("Furnace", DLC.NEW_WORLD_RISING, Region.NW, 6080, 7348,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks"}, "Obreros", {"Coal", "Iron"}, "Steel", "Fire Department"),

    A1800Unlock("Laboratory: Fire Extinguishers", DLC.NEW_WORLD_RISING, Region.NW, [6629, 6633], 7333,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Artistas",
                {"Steel", "Caoutchouc"}, "Fire Extinguishers", "Fire Department"),

    A1800Unlock("Fire Department", DLC.NEW_WORLD_RISING, Region.NW, 6259, 7333,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Timber", set(), "Fire Extinguishers", "Fire Protection", "Fire Department", "Fire Station"),

    # Orchard: Camphor Wax -> Tourist Season or The High Life

    # Chemical Plant: Celluloid -> The High Life

    A1800Unlock("Cable Factory", DLC.NEW_WORLD_RISING, Region.NW, 6279, 5812,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks"}, "Obreros", {"Copper", "Caoutchouc"}, "Electric Cables", "Fans"),

    A1800Unlock("Motor Assembly Plant", DLC.NEW_WORLD_RISING, Region.NW, 5659, 5812,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Obreros", "Electricity"},
                {"Electric Cables", "Celluloid", "Steel"}, "Motor", "Fans"),

    A1800Unlock("Fan Factory", DLC.NEW_WORLD_RISING, Region.NW, 5862, 5812,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Artistas", "Electricity"},
                {"Motor", "Aluminium Profiles"}, "Fans", "Fans"),

    A1800Unlock("Chemical Plant: Film Reels", DLC.NEW_WORLD_RISING, Region.NW, [5828, 5932, 135221], [135221, 5812],
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks"}, "Obreros", {"Saltpetre", "Celluloid"}, "Film Reels", "Cinema"),

    A1800Unlock("Cinema", DLC.NEW_WORLD_RISING, Region.NW, 6018, 5812,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks"}, "Artistas", "Film Reels", "Cinema", "Cinema"),

    A1800Unlock("Arsenal: Police Equipment", DLC.NEW_WORLD_RISING, Region.NW, [6630, 6632, 905], [2041, 7336],
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Jornaleros",
                {"Wood", "Steel", "Cotton Fabric"}, "Police Equipment", "Police Headquarters"),

    A1800Unlock("Police Headquarters", DLC.NEW_WORLD_RISING, Region.NW, 6258, 7336,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                {"Timber", "Bricks"}, set(),
                "Police Equipment", "Riot Control", "Police Headquarters", "Police Station"),

    A1800Unlock("Dam: Structure", DLC.NEW_WORLD_RISING, Region.NW, 6004, 6004,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                "Dam: Foundations", "Obreros", {"Bricks", "Steel Beams"}, "Dam: Structure"),

    A1800Unlock("Dam: Engineering", DLC.NEW_WORLD_RISING, Region.NW, 6005, 6005,
                Trigger.POPULATION("Artistas", Region.NW, 4000),
                "Dam: Structure", "Obreros", {"Windows", "Reinforced Concrete"}, "Dam: Engineering"),

    A1800Unlock("Dam", DLC.NEW_WORLD_RISING, Region.NW, 6006, 6006,
                Trigger.POPULATION("Artistas", Region.NW, 4000), "Dam: Engineering", "Obreros", set(), "Electricity"),

    A1800Unlock("Scooter Factory", DLC.NEW_WORLD_RISING, Region.NW, 5658, 5824,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                {"Timber", "Bricks", "Steel Beams", "Windows", "Reinforced Concrete"}, {"Artistas", "Electricity"},
                {"Motor", "Pigments", "Caoutchouc"}, "Scooters", "Scooters"),

    A1800Unlock("Laboratory: Medicine", DLC.NEW_WORLD_RISING, Region.NW, [6631, 6634], 7337,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                {"Timber", "Bricks", "Aluminium Profiles"}, "Artistas",
                {"Herbs", "Orchid", "Ethanol"}, "Medicine", "City Hospital"),

    A1800Unlock("City Hospital", DLC.NEW_WORLD_RISING, Region.NW, 6260, 7337,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                {"Timber", "Bricks"}, set(),
                "Medicine", "Healthcare", "City Hospital", "Hospital"),

    A1800Unlock("Grand Stadium: Foundations", DLC.NEW_WORLD_RISING, Region.NW, 6117, 6117,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                {"Timber", "Reinforced Concrete", "Grand Storage"}, "Jornaleros",
                {"Timber", "Reinforced Concrete"}, "Grand Stadium: Foundations"),

    A1800Unlock("Grand Stadium: Superstructure", DLC.NEW_WORLD_RISING, Region.NW, 6118, 6118,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                "Grand Stadium: Foundations", "Obreros",
                {"Bricks", "Steel Beams", "Reinforced Concrete"}, "Grand Stadium: Superstructure"),

    A1800Unlock("Grand Stadium", DLC.NEW_WORLD_RISING, Region.NW, 6121, 6121,
                Trigger.POPULATION("Artistas", Region.NW, 6000),
                "Grand Stadium: Superstructure", {"Artistas", "Electricity"}, set(), "Grand Stadium: Football Championships"),

    # Building, Factory, Upgrade, Residence
    A1800Unlock("Artista Residence", DLC.NEW_WORLD_RISING, Region.NW, 5405, 5405,
                Trigger.POPULATION("Obreros", Region.NW, 1000),
                {"Timber", "Bricks"}, set(), set(), "Artistas", "", "Obrero Residence",
                {"Tortillas", "Sewing Machines", "Coffee", "Bombins", "Soccer Balls", "Mezcal", "Jalea",
                    "Beach", "Perfumes", "Scooters", "Fire Protection", "Riot Control", "Healthcare"},
                {"Beer", "Boxing Arena", "Cigars", "Ice Cream", "Samba School", "Cinema"},
                {"Light Bulbs", "Champagne", "Billiard Tables", "Lanterns", "Local Mail",
                    "Regional Mail", "Overseas Mail", "Jewellery", "Souvenirs"}),

    ### Needs Tourist Season ###
    # Building, Factory
    A1800Unlock("Restaurant: Empanadas", DLC.TOURIST_SEASON | DLC.NEW_WORLD_RISING, Region.OW, [6136, 6139], 6187,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Restaurant (Blank)", "Tourists", {"Beef", "Herbs", "Flour"}, "Restaurant"),

    A1800Unlock("Cafe: Cone O'Copia", DLC.TOURIST_SEASON | DLC.NEW_WORLD_RISING, Region.OW, [6138, 6145], 6187,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Cafe (Blank)", "Tourists", {"Milk", "Orchid", "Jam"}, "Cafe"),

    A1800Unlock("Bar: Absinthe", DLC.TOURIST_SEASON | DLC.NEW_WORLD_RISING, Region.OW, [6137, 6144], 6187,
                Trigger.POPULATION("Artistas", Region.NW, 2700),
                "Bar (Blank)", "Tourists", {"Herbs", "Sugar", "Schnapps"}, "Bar"),

    ### Needs Seeds of Change ###
    # Building, Factory, Residence
    A1800Unlock("Hacienda Artista Quarters", DLC.SEEDS_OF_CHANGE | DLC.NEW_WORLD_RISING, Region.NW, 6086, 6086,
                Trigger.POPULATION("Artistas", Region.NW, 1),
                {"Timber", "Bricks"}, set(), "Artistas", "Artistas",
                consumption={"Tortillas", "Sewing Machines", "Coffee", "Bombins", "Soccer Balls", "Mezcal", "Jalea",
                             "Beach", "Perfumes", "Scooters", "Spectacles", "Electricity", "Fire Protection",
                             "Riot Control", "Healthcare"},
                luxury={"Beer", "Boxing Arena", "Cigars", "Ice Cream", "Samba School", "Cinema"},
                lifestyle={"Light Bulbs", "Champagne", "Billiard Tables", "Lanterns", "Local Mail",
                           "Regional Mail", "Overseas Mail", "Jewellery", "Souvenirs"}),
]


class _Unlocks:
    _initialized: bool = False

    def init(self, parsed_options: ParsedOptions) -> None:
        self._apply_options(parsed_options)

        for a1800_unlock in self._a1800_unlocks:
            a1800_unlock.trigger = self._flatten_trigger(a1800_unlock.trigger)
            a1800_unlock.post_init()
            self._add_guids_to_trigger(a1800_unlock.trigger)
            self._regenerate_trigger_ap_location_name(a1800_unlock.trigger)

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
        elif (trigger.trigger_type in [TriggerType.UNLOCK, TriggerType.COUNTER, TriggerType.ITEM_SET_ACTIVE, TriggerType.FACTORY_PRODUCTIVITY]) \
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
            assert references[0].guid, \
                f"Trigger references product without guid {references[0].name}"
            trigger.guid = references[0].guid
        elif (trigger.trigger_type == TriggerType.EVENT_ACTIVE) and trigger.guid == 0:
            references = list(PRODUCTS.find_products(trigger.product_name, trigger.region))
            assert references, f"Trigger references unknown product {trigger.product_name}"
            assert len(references) == 1, \
                f"Trigger references multiple products {[reference.name for reference in references]}"
            assert references[0].guid, \
                f"Trigger references product without guid {references[0].name}"
            trigger.guid = references[0].guid
        elif (trigger.trigger_type in [TriggerType.POPULATION, TriggerType.POPULATION_HAPPINESS]) and trigger.guid == 0:
            references = list(PRODUCTS.find_products(trigger.population_name, trigger.region))
            assert references, f"Trigger references unknown population {trigger.population_name}"
            assert len(references) == 1, \
                f"Trigger references multiple populations {[reference.name for reference in references]}"
            assert references[0].guid, \
                f"Trigger references population without guid {references[0].name}"
            trigger.guid = references[0].guid
        elif (trigger.trigger_type == TriggerType.OBJECT_POSITION) and trigger.guid == 0:
            references = [unlock for unlock in self._a1800_unlocks
                          if unlock.name == trigger.unlock_name and trigger.region in unlock.region]
            assert references, f"Trigger references unknown unlock {trigger.unlock_name}"
            assert len(references) == 1, \
                f"Trigger references multiple unlocks {[reference.name for reference in references]}"
            assert references[0].unlock_guids, \
                f"Trigger references unlock {references[0].name}, which has no guids"
            trigger.guid = references[0].unlock_guids[0]
            target_references = [unlock for unlock in self._a1800_unlocks
                                 if unlock.name == trigger.target_name and trigger.region in unlock.region]
            assert target_references, f"Trigger references unknown target {trigger.target_name}"
            assert len(target_references) == 1, \
                f"Trigger references multiple targets {[target_reference.name for target_reference in target_references]}"
            assert target_references[0].unlock_guids, \
                f"Trigger references target {target_references[0].name}, which has no guids"
            trigger.target_guid = target_references[0].unlock_guids[0]

    def _flatten_trigger(self, trigger: Trigger) -> Trigger:
        if trigger.trigger_type in [TriggerType.ALL, TriggerType.LINEAR, TriggerType.ANY]:
            trigger.triggers = [self._flatten_trigger(subtrigger) for subtrigger in trigger.triggers]
            trigger.triggers = [flat_trigger for subtrigger in trigger.triggers for flat_trigger in (
                subtrigger.triggers if subtrigger.trigger_type == trigger.trigger_type else [subtrigger])]

        return trigger

    def _regenerate_trigger_ap_location_name(self, trigger: Trigger) -> None:
        if trigger.ap_location_name_generated:
            if trigger.trigger_type in [TriggerType.ALL, TriggerType.LINEAR, TriggerType.ANY]:
                for subtrigger in trigger.triggers:
                    self._regenerate_trigger_ap_location_name(subtrigger)

            trigger.ap_location_name = ""
            trigger.post_init()

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
        elif trigger.trigger_type in [TriggerType.UNLOCK, TriggerType.COUNTER, TriggerType.ITEM_SET_ACTIVE, TriggerType.FACTORY_PRODUCTIVITY]:
            return Trigger.FALSE() if not len([unlock for unlock in self._a1800_unlocks if unlock.name == trigger.unlock_name
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
        elif trigger.trigger_type == TriggerType.OBJECT_POSITION:
            return Trigger.FALSE() if not len([unlock for unlock in self._a1800_unlocks if unlock.name == trigger.unlock_name
                                               and trigger.region in unlock.region]) or not len([unlock for unlock in self._a1800_unlocks if unlock.name == trigger.target_name
                                                                                                 and trigger.region in unlock.region]) else trigger
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

    def _apply_options(self, parsed_options: ParsedOptions) -> None:
        global _a1800_unlocks

        self._a1800_unlocks = [unlock for unlock in _a1800_unlocks if any(
            dlc in parsed_options.enabled_dlcs for dlc in unlock.dlc)]

        if parsed_options.enable_start_with_flagship:
            self._a1800_unlocks.append(
                A1800Unlock("Flagship Start", DLC.VANILLA, Region.OW,
                            output={"Seafaring"},
                            type=UnlockType.META | UnlockType.FACTORY),
            )
            self._a1800_unlocks.append(
                A1800Unlock("Flagship Start with Fish", DLC.VANILLA, Region.OW,
                            input={"Fish"}, output={"Expeditions: Level 1"},
                            type=UnlockType.META | UnlockType.FACTORY),
            )
            self._a1800_unlocks.append(
                A1800Unlock("Flagship Start with Fish and Work Clothes", DLC.VANILLA, Region.OW,
                            input={"Fish", "Work Clothes"}, output={"Expeditions: Level 2"},
                            type=UnlockType.META | UnlockType.FACTORY),
            )

        if DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES in parsed_options.enabled_dlcs:
            for unlock in self._a1800_unlocks:
                if unlock.name == "Post Office" and unlock.region == Region.AR:
                    unlock.guids = [4260]
                    unlock.unlock_guids = [4260]
                    unlock.lock_guids.append(4532)
                    unlock.dlc = {DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES}
                    unlock.maintenance.add("Explorers")
                    unlock.output.add(("Local Mail", Region.AR))
                    break

        if DLC.DOCKLANDS in parsed_options.enabled_dlcs and not parsed_options.enable_docklands_logic:
            for unlock in self._a1800_unlocks:
                if unlock.name == "Docklands Main Wharf" and unlock.region == Region.OW:
                    unlock.output = {("Docklands", Region.OW)}

        self._clean_dlc_references(parsed_options.enabled_dlcs)

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
