from collections.abc import Sequence
from typing import Iterator

from ._Enums import ALL_REGIONS, DLC, NO_REGION, ProductType, Region
from ._ParsedOptions import ParsedOptions


class A1800Product:
    name: str
    dlc: set[DLC]
    region: Region
    guid: int
    type: ProductType

    def __init__(self, name: str, dlc: DLC | set[DLC], region: Region, guid: int, type: ProductType) -> None:
        self.name = name
        self.dlc = {dlc} if isinstance(dlc, DLC) else dlc
        self.region = region
        self.guid = guid
        self.type = type

    def __str__(self) -> str:
        return f"({self.type.full_name}: {self.name}, {self.region})"


_a1800_products: list[A1800Product] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    A1800Product("Sea Travel", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Air Travel", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Oil Transport", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),

    A1800Product("Victory", DLC.VANILLA, ALL_REGIONS, 0, ProductType.META),

    A1800Product("Road Network", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Settling", DLC.VANILLA, Region.OW | Region.NW, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Medium Storage", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Riot Control", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Large Storage", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Healthcare", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Grand Storage", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Railway", DLC.VANILLA, Region.OW | Region.NW, 0, ProductType.META),
    A1800Product("Oil Harbour", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("Oil Field", DLC.VANILLA, Region.OW, 0, ProductType.META),
    A1800Product("World's Fair: Exhibitions", DLC.VANILLA, Region.OW, 135020, ProductType.META),
    A1800Product("Road Network", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Riot Control", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Medium Storage", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Healthcare", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Oil Harbour", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Oil Field", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Large Storage", DLC.VANILLA, Region.NW, 0, ProductType.META),
    A1800Product("Grand Storage", DLC.VANILLA, Region.NW, 0, ProductType.META),

    A1800Product("World's Fair: Foundations", DLC.VANILLA, Region.OW, 0, ProductType.STAGE),
    A1800Product("World's Fair: Superstructure", DLC.VANILLA, Region.OW, 0, ProductType.STAGE),
    A1800Product("World's Fair: Glazing", DLC.VANILLA, Region.OW, 0, ProductType.STAGE),
    A1800Product("World's Fair: Infrastructure", DLC.VANILLA, Region.OW, 0, ProductType.STAGE),

    A1800Product("Farmers", DLC.VANILLA, Region.OW, 15000000, ProductType.WORKFORCE),
    A1800Product("Workers", DLC.VANILLA, Region.OW, 15000001, ProductType.WORKFORCE),
    A1800Product("Artisans", DLC.VANILLA, Region.OW, 15000002, ProductType.WORKFORCE),
    A1800Product("Engineers", DLC.VANILLA, Region.OW, 15000003, ProductType.WORKFORCE),
    A1800Product("Investors", DLC.VANILLA, Region.OW, 15000004, ProductType.WORKFORCE),
    A1800Product("Jornaleros", DLC.VANILLA, Region.NW, 15000005, ProductType.WORKFORCE),
    A1800Product("Obreros", DLC.VANILLA, Region.NW, 15000006, ProductType.WORKFORCE),

    A1800Product("Wood", DLC.VANILLA, ALL_REGIONS, 120008, ProductType.GOOD),
    A1800Product("Timber", DLC.VANILLA, ALL_REGIONS, 1010196, ProductType.GOOD),
    A1800Product("Fish", DLC.VANILLA, ALL_REGIONS, 1010200, ProductType.GOOD),
    A1800Product("Wool", DLC.VANILLA, ALL_REGIONS, 1010197, ProductType.GOOD),
    A1800Product("Work Clothes", DLC.VANILLA, ALL_REGIONS, 1010237, ProductType.GOOD),
    A1800Product("Potatoes", DLC.VANILLA, ALL_REGIONS, 1010195, ProductType.GOOD),
    A1800Product("Schnapps", DLC.VANILLA, ALL_REGIONS, 1010216, ProductType.GOOD),
    A1800Product("Clay", DLC.VANILLA, ALL_REGIONS, 1010201, ProductType.GOOD),
    A1800Product("Bricks", DLC.VANILLA, ALL_REGIONS, 1010205, ProductType.GOOD),
    A1800Product("Pigs", DLC.VANILLA, ALL_REGIONS, 1010199, ProductType.GOOD),
    A1800Product("Sausages", DLC.VANILLA, ALL_REGIONS, 1010238, ProductType.GOOD),
    A1800Product("Grain", DLC.VANILLA, ALL_REGIONS, 1010192, ProductType.GOOD),
    A1800Product("Flour", DLC.VANILLA, ALL_REGIONS, 1010235, ProductType.GOOD),
    A1800Product("Bread", DLC.VANILLA, ALL_REGIONS, 1010213, ProductType.GOOD),
    A1800Product("Sails", DLC.VANILLA, ALL_REGIONS, 1010210, ProductType.GOOD),
    A1800Product("Coal", DLC.VANILLA, ALL_REGIONS, 1010226, ProductType.GOOD),
    A1800Product("Iron", DLC.VANILLA, ALL_REGIONS, 1010227, ProductType.GOOD),
    A1800Product("Steel", DLC.VANILLA, ALL_REGIONS, 1010219, ProductType.GOOD),
    A1800Product("Steel Beams", DLC.VANILLA, ALL_REGIONS, 1010218, ProductType.GOOD),
    A1800Product("Tallow", DLC.VANILLA, ALL_REGIONS, 1010234, ProductType.GOOD),
    A1800Product("Soap", DLC.VANILLA, ALL_REGIONS, 1010203, ProductType.GOOD),
    A1800Product("Weapons", DLC.VANILLA, ALL_REGIONS, 1010221, ProductType.GOOD),
    A1800Product("Hops", DLC.VANILLA, ALL_REGIONS, 1010194, ProductType.GOOD),
    A1800Product("Malt", DLC.VANILLA, ALL_REGIONS, 1010236, ProductType.GOOD),
    A1800Product("Beer", DLC.VANILLA, ALL_REGIONS, 1010214, ProductType.GOOD),
    A1800Product("Quartz Sand", DLC.VANILLA, ALL_REGIONS, 1010228, ProductType.GOOD),
    A1800Product("Glass", DLC.VANILLA, ALL_REGIONS, 1010241, ProductType.GOOD),
    A1800Product("Windows", DLC.VANILLA, ALL_REGIONS, 1010207, ProductType.GOOD),
    A1800Product("Beef", DLC.VANILLA, ALL_REGIONS, 1010193, ProductType.GOOD),
    A1800Product("Red Peppers", DLC.VANILLA, ALL_REGIONS, 1010198, ProductType.GOOD),
    A1800Product("Goulash", DLC.VANILLA, ALL_REGIONS, 1010215, ProductType.GOOD),
    A1800Product("Canned Food", DLC.VANILLA, ALL_REGIONS, 1010217, ProductType.GOOD),
    A1800Product("Sewing Machines", DLC.VANILLA, ALL_REGIONS, 1010206, ProductType.GOOD),
    A1800Product("Furs", DLC.VANILLA, ALL_REGIONS, 1010209, ProductType.GOOD),
    A1800Product("Cotton", DLC.VANILLA, ALL_REGIONS, 1010253, ProductType.GOOD),
    A1800Product("Cotton Fabric", DLC.VANILLA, ALL_REGIONS, 1010240, ProductType.GOOD),
    A1800Product("Fur Coats", DLC.VANILLA, ALL_REGIONS, 1010247, ProductType.GOOD),
    A1800Product("Cement", DLC.VANILLA, ALL_REGIONS, 1010231, ProductType.GOOD),
    A1800Product("Reinforced Concrete", DLC.VANILLA, ALL_REGIONS, 1010202, ProductType.GOOD),
    A1800Product("Oil", DLC.VANILLA, Region.OW, 1010566, ProductType.GOOD),
    A1800Product("Zinc", DLC.VANILLA, ALL_REGIONS, 1010229, ProductType.GOOD),
    A1800Product("Copper", DLC.VANILLA, ALL_REGIONS, 1010230, ProductType.GOOD),
    A1800Product("Brass", DLC.VANILLA, ALL_REGIONS, 1010204, ProductType.GOOD),
    A1800Product("Spectacles", DLC.VANILLA, ALL_REGIONS, 120030, ProductType.GOOD),
    A1800Product("Caoutchouc", DLC.VANILLA, ALL_REGIONS, 1010255, ProductType.GOOD),
    A1800Product("Penny Farthings", DLC.VANILLA, ALL_REGIONS, 1010245, ProductType.GOOD),
    A1800Product("Steam Motors", DLC.VANILLA, ALL_REGIONS, 1010224, ProductType.GOOD),
    A1800Product("Saltpetre", DLC.VANILLA, ALL_REGIONS, 1010232, ProductType.GOOD),
    A1800Product("Dynamite", DLC.VANILLA, ALL_REGIONS, 1010222, ProductType.GOOD),
    A1800Product("Advanced Weapons", DLC.VANILLA, ALL_REGIONS, 1010223, ProductType.GOOD),
    A1800Product("Gold Ore", DLC.VANILLA, ALL_REGIONS, 1010233, ProductType.GOOD),
    A1800Product("Gold", DLC.VANILLA, ALL_REGIONS, 1010249, ProductType.GOOD),
    A1800Product("Pocket Watches", DLC.VANILLA, ALL_REGIONS, 1010246, ProductType.GOOD),
    A1800Product("Filaments", DLC.VANILLA, ALL_REGIONS, 1010243, ProductType.GOOD),
    A1800Product("Light Bulbs", DLC.VANILLA, ALL_REGIONS, 1010208, ProductType.GOOD),
    A1800Product("Grapes", DLC.VANILLA, ALL_REGIONS, 120014, ProductType.GOOD),
    A1800Product("Champagne", DLC.VANILLA, ALL_REGIONS, 120016, ProductType.GOOD),
    A1800Product("Wood Veneers", DLC.VANILLA, ALL_REGIONS, 1010242, ProductType.GOOD),
    A1800Product("Pearls", DLC.VANILLA, ALL_REGIONS, 1010256, ProductType.GOOD),
    A1800Product("Jewellery", DLC.VANILLA, ALL_REGIONS, 1010250, ProductType.GOOD),
    A1800Product("Gramophones", DLC.VANILLA, ALL_REGIONS, 1010248, ProductType.GOOD),
    A1800Product("Chassis", DLC.VANILLA, ALL_REGIONS, 1010211, ProductType.GOOD),
    A1800Product("Steam Carriages", DLC.VANILLA, ALL_REGIONS, 1010225, ProductType.GOOD),

    A1800Product("Fish Oil", DLC.VANILLA, ALL_REGIONS, 120042, ProductType.GOOD),
    A1800Product("Plantains", DLC.VANILLA, ALL_REGIONS, 120041, ProductType.GOOD),
    A1800Product("Fried Plantains", DLC.VANILLA, ALL_REGIONS, 120033, ProductType.GOOD),
    A1800Product("Sugar Cane", DLC.VANILLA, ALL_REGIONS, 1010251, ProductType.GOOD),
    A1800Product("Rum", DLC.VANILLA, ALL_REGIONS, 1010257, ProductType.GOOD),
    A1800Product("Alpaca Wool", DLC.VANILLA, ALL_REGIONS, 120036, ProductType.GOOD),
    A1800Product("Ponchos", DLC.VANILLA, ALL_REGIONS, 120043, ProductType.GOOD),
    A1800Product("Corn", DLC.VANILLA, ALL_REGIONS, 120034, ProductType.GOOD),
    A1800Product("Tortillas", DLC.VANILLA, ALL_REGIONS, 120035, ProductType.GOOD),
    A1800Product("Coffee Beans", DLC.VANILLA, ALL_REGIONS, 120031, ProductType.GOOD),
    A1800Product("Coffee", DLC.VANILLA, ALL_REGIONS, 120032, ProductType.GOOD),
    A1800Product("Felt", DLC.VANILLA, ALL_REGIONS, 120044, ProductType.GOOD),
    A1800Product("Bombins", DLC.VANILLA, ALL_REGIONS, 120037, ProductType.GOOD),
    A1800Product("Oil", DLC.VANILLA, Region.NW, 1010566, ProductType.GOOD),
    A1800Product("Tobacco", DLC.VANILLA, ALL_REGIONS, 1010252, ProductType.GOOD),
    A1800Product("Cigars", DLC.VANILLA, ALL_REGIONS, 1010259, ProductType.GOOD),
    A1800Product("Cocoa", DLC.VANILLA, ALL_REGIONS, 1010254, ProductType.GOOD),
    A1800Product("Sugar", DLC.VANILLA, ALL_REGIONS, 1010239, ProductType.GOOD),
    A1800Product("Chocolate", DLC.VANILLA, ALL_REGIONS, 1010258, ProductType.GOOD),

    A1800Product("Market", DLC.VANILLA, Region.OW, 120020, ProductType.SERVICE),
    A1800Product("Pub", DLC.VANILLA, Region.OW, 1010349, ProductType.SERVICE),
    A1800Product("Church", DLC.VANILLA, Region.OW, 1010350, ProductType.SERVICE),
    A1800Product("School", DLC.VANILLA, Region.OW, 1010351, ProductType.SERVICE),
    A1800Product("Variety Theatre", DLC.VANILLA, Region.OW, 1010352, ProductType.SERVICE),
    A1800Product("University", DLC.VANILLA, Region.OW, 1010353, ProductType.SERVICE),
    A1800Product("Electricity", DLC.VANILLA, Region.OW, 120022, ProductType.SERVICE),
    A1800Product("Bank", DLC.VANILLA, Region.OW, 1010356, ProductType.SERVICE),
    A1800Product("Members Club", DLC.VANILLA, Region.OW, 1010355, ProductType.SERVICE),
    A1800Product("World's Fair", DLC.VANILLA, Region.OW, 133536, ProductType.SERVICE),
    A1800Product("Market", DLC.VANILLA, Region.NW, 120020, ProductType.SERVICE),
    A1800Product("Chapel", DLC.VANILLA, Region.NW, 1010350, ProductType.SERVICE),
    A1800Product("Boxing Arena", DLC.VANILLA, Region.NW, 1010349, ProductType.SERVICE),

    ################################################################################################################
    ### SUNKEN_TREASURES                                                                                         ###
    ################################################################################################################
    A1800Product("Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112518, ProductType.GOOD),
    A1800Product("Nice Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112520, ProductType.GOOD),
    A1800Product("Special Scrap", DLC.SUNKEN_TREASURES, ALL_REGIONS, 112523, ProductType.GOOD),

    ################################################################################################################
    ### BRIGHT_HARVEST                                                                                           ###
    ################################################################################################################
    A1800Product("Fuel", DLC.BRIGHT_HARVEST, Region.OW, 270042, ProductType.SERVICE),
    A1800Product("Fuel", DLC.BRIGHT_HARVEST, Region.NW, 270042, ProductType.SERVICE),

    ################################################################################################################
    ### THE_PASSAGE                                                                                              ###
    ################################################################################################################
    A1800Product("Road Network", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Settling", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Plateau Settling", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Healthcare", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Medium Storage", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Medium Plateu Storage", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Large Storage", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),
    A1800Product("Large Plateu Storage", DLC.THE_PASSAGE, Region.AR, 0, ProductType.META),

    A1800Product("Arctic Airship Hangar: Foundations", DLC.THE_PASSAGE, Region.AR, 0, ProductType.STAGE),
    A1800Product("Arctic Airship Hangar: Structure", DLC.THE_PASSAGE, Region.AR, 0, ProductType.STAGE),
    A1800Product("Arctic Airship Hangar: Roof", DLC.THE_PASSAGE, Region.AR, 0, ProductType.STAGE),

    A1800Product("Explorers", DLC.THE_PASSAGE, Region.AR, 112642, ProductType.WORKFORCE),
    A1800Product("Technicians", DLC.THE_PASSAGE, Region.AR, 112643, ProductType.WORKFORCE),

    A1800Product("Caribou Meat", DLC.THE_PASSAGE, ALL_REGIONS, 112694, ProductType.GOOD),
    A1800Product("Whale Oil", DLC.THE_PASSAGE, ALL_REGIONS, 112699, ProductType.GOOD),
    A1800Product("Pemmican", DLC.THE_PASSAGE, ALL_REGIONS, 112705, ProductType.GOOD),
    A1800Product("Goose Feathers", DLC.THE_PASSAGE, ALL_REGIONS, 112697, ProductType.GOOD),
    A1800Product("Seal Skin", DLC.THE_PASSAGE, ALL_REGIONS, 112696, ProductType.GOOD),
    A1800Product("Sleeping Bags", DLC.THE_PASSAGE, ALL_REGIONS, 112701, ProductType.GOOD),
    A1800Product("Oil Lamps", DLC.THE_PASSAGE, ALL_REGIONS, 112702, ProductType.GOOD),
    A1800Product("Bear Fur", DLC.THE_PASSAGE, ALL_REGIONS, 112695, ProductType.GOOD),
    A1800Product("Parkas", DLC.THE_PASSAGE, ALL_REGIONS, 112700, ProductType.GOOD),
    A1800Product("Lost Expedition Scrap", DLC.THE_PASSAGE, ALL_REGIONS, 115980, ProductType.GOOD),
    A1800Product("Huskies", DLC.THE_PASSAGE, ALL_REGIONS, 112698, ProductType.GOOD),
    A1800Product("Sleds", DLC.THE_PASSAGE, ALL_REGIONS, 112704, ProductType.GOOD),
    A1800Product("Husky Sleds", DLC.THE_PASSAGE, ALL_REGIONS, 112703, ProductType.GOOD),
    A1800Product("Arctic Gas", DLC.THE_PASSAGE, ALL_REGIONS, 112706, ProductType.GOOD),

    A1800Product("Heat", DLC.THE_PASSAGE, Region.AR, 112708, ProductType.SERVICE),
    A1800Product("Canteen", DLC.THE_PASSAGE, Region.AR, 114890, ProductType.SERVICE),
    A1800Product("Post Office", DLC.THE_PASSAGE, Region.AR, 112693, ProductType.SERVICE),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
    A1800Product("Research", DLC.LAND_OF_LIONS, Region.OW, 0, ProductType.META),
    A1800Product("Permit: Scholar Residence", DLC.LAND_OF_LIONS, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Permit: Advanced Coffee Roaster", DLC.LAND_OF_LIONS, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Permit: Advanced Rum Distillery", DLC.LAND_OF_LIONS, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Permit: Advanced Cotton Mill", DLC.LAND_OF_LIONS, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Permit: Advanced Pier", DLC.LAND_OF_LIONS, ALL_REGIONS, 0, ProductType.META),
    A1800Product("Initial Settling", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Road Network", DLC.THE_PASSAGE, Region.EN, 0, ProductType.META),
    A1800Product("Settling", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Canal System", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Irrigation", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Fire Protection", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Riot Control", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Medium Storage", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Healthcare", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Large Storage", DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),

    A1800Product("Research Institute: Foundations", DLC.LAND_OF_LIONS, Region.OW, 0, ProductType.STAGE),
    A1800Product("Research Institute: Superstructure", DLC.LAND_OF_LIONS, Region.OW, 0, ProductType.STAGE),

    A1800Product("Scholars", DLC.LAND_OF_LIONS, Region.OW, 118745, ProductType.WORKFORCE),
    A1800Product("Shepherds", DLC.LAND_OF_LIONS, Region.EN, 114329, ProductType.WORKFORCE),
    A1800Product("Elders", DLC.LAND_OF_LIONS, Region.EN, 114330, ProductType.WORKFORCE),

    A1800Product("Research Points", DLC.LAND_OF_LIONS, ALL_REGIONS, 119392, ProductType.GOOD),
    A1800Product("Leather Boots", DLC.LAND_OF_LIONS, ALL_REGIONS, 114428, ProductType.GOOD),
    A1800Product("Tailored Suits", DLC.LAND_OF_LIONS, ALL_REGIONS, 114430, ProductType.GOOD),
    A1800Product("Telephones", DLC.LAND_OF_LIONS, ALL_REGIONS, 114431, ProductType.GOOD),
    A1800Product("Wanza Timber", DLC.LAND_OF_LIONS, ALL_REGIONS, 114356, ProductType.GOOD),
    A1800Product("Goat Milk", DLC.LAND_OF_LIONS, ALL_REGIONS, 114371, ProductType.GOOD),
    A1800Product("Linseed", DLC.LAND_OF_LIONS, ALL_REGIONS, 114365, ProductType.GOOD),
    A1800Product("Linen", DLC.LAND_OF_LIONS, ALL_REGIONS, 114391, ProductType.GOOD),
    A1800Product("Finery", DLC.LAND_OF_LIONS, ALL_REGIONS, 114401, ProductType.GOOD),
    A1800Product("Sanga Cow", DLC.LAND_OF_LIONS, ALL_REGIONS, 114357, ProductType.GOOD),
    A1800Product("Salt", DLC.LAND_OF_LIONS, ALL_REGIONS, 114358, ProductType.GOOD),
    A1800Product("Dried Meat", DLC.LAND_OF_LIONS, ALL_REGIONS, 114359, ProductType.GOOD),
    A1800Product("Hibiscus Petals", DLC.LAND_OF_LIONS, ALL_REGIONS, 114364, ProductType.GOOD),
    A1800Product("Hibiscus Tea", DLC.LAND_OF_LIONS, ALL_REGIONS, 114390, ProductType.GOOD),
    A1800Product("Teff", DLC.LAND_OF_LIONS, ALL_REGIONS, 114367, ProductType.GOOD),
    A1800Product("Mud Bricks", DLC.LAND_OF_LIONS, ALL_REGIONS, 114402, ProductType.GOOD),
    A1800Product("Indigo Dye", DLC.LAND_OF_LIONS, ALL_REGIONS, 114368, ProductType.GOOD),
    A1800Product("Ceramics", DLC.LAND_OF_LIONS, ALL_REGIONS, 118724, ProductType.GOOD),
    A1800Product("Tapestries", DLC.LAND_OF_LIONS, ALL_REGIONS, 114404, ProductType.GOOD),
    A1800Product("Spices", {DLC.LAND_OF_LIONS, DLC.SEEDS_OF_CHANGE}, ALL_REGIONS, 114369, ProductType.GOOD),
    A1800Product("Spiced Flour", DLC.LAND_OF_LIONS, ALL_REGIONS, 114408, ProductType.GOOD),
    A1800Product("Lobster", DLC.LAND_OF_LIONS, ALL_REGIONS, 118728, ProductType.GOOD),
    A1800Product("Seafood Stew", DLC.LAND_OF_LIONS, ALL_REGIONS, 114410, ProductType.GOOD),
    A1800Product("Clay Pipes", DLC.LAND_OF_LIONS, ALL_REGIONS, 114414, ProductType.GOOD),
    A1800Product("Paper", DLC.LAND_OF_LIONS, ALL_REGIONS, 117702, ProductType.GOOD),
    A1800Product("Illuminated Script", DLC.LAND_OF_LIONS, ALL_REGIONS, 117698, ProductType.GOOD),
    A1800Product("Beeswax", DLC.LAND_OF_LIONS, ALL_REGIONS, 114370, ProductType.GOOD),
    A1800Product("Ornate Candles", DLC.LAND_OF_LIONS, ALL_REGIONS, 117701, ProductType.GOOD),
    A1800Product("Lanterns", DLC.LAND_OF_LIONS, ALL_REGIONS, 117699, ProductType.GOOD),

    A1800Product("Radio Tower", DLC.LAND_OF_LIONS, Region.OW, 114425, ProductType.SERVICE),
    A1800Product("Market", DLC.LAND_OF_LIONS, Region.EN, 120020, ProductType.SERVICE),
    A1800Product("Musicians' Court", DLC.LAND_OF_LIONS, Region.EN, 114361, ProductType.SERVICE),
    A1800Product("Monastery", DLC.LAND_OF_LIONS, Region.EN, 114362, ProductType.SERVICE),

    ### Needs Bright Harvest ###
    A1800Product("Railway", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),
    A1800Product("Oil Harbour", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 0, ProductType.META),

    A1800Product("Oil", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 1010566, ProductType.GOOD),

    A1800Product("Fuel", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 270042, ProductType.SERVICE),

    ################################################################################################################
    ### TOURIST_SEASON                                                                                           ###
    ################################################################################################################
    A1800Product("Public Transport", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.META),
    A1800Product("Restaurant (Blank)", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.META),
    A1800Product("Cafe (Blank)", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.META),
    A1800Product("Bar (Blank)", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.META),
    A1800Product("The Iron Tower (Blank)", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.META),

    A1800Product("The Iron Tower: Foundations", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.STAGE),
    A1800Product("The Iron Tower: Superstructure", DLC.TOURIST_SEASON, Region.OW, 0, ProductType.STAGE),

    A1800Product("Tourists", DLC.TOURIST_SEASON, Region.OW, 601379, ProductType.WORKFORCE),

    A1800Product("Jam", DLC.TOURIST_SEASON, ALL_REGIONS, 133183, ProductType.GOOD),
    A1800Product("Coconut Oil", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE,
                 DLC.NEW_WORLD_RISING}, ALL_REGIONS, 133095, ProductType.GOOD),
    A1800Product("Cinnamon", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE}, ALL_REGIONS, 133093, ProductType.GOOD),
    A1800Product("Shampoo", DLC.TOURIST_SEASON, ALL_REGIONS, 133181, ProductType.GOOD),
    A1800Product("Citrus", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE,
                 DLC.NEW_WORLD_RISING}, ALL_REGIONS, 133097, ProductType.GOOD),
    A1800Product("Lemonade", DLC.TOURIST_SEASON, ALL_REGIONS, 133185, ProductType.GOOD),
    A1800Product("Camphor Wax", {DLC.TOURIST_SEASON, DLC.THE_HIGH_LIFE,
                 DLC.NEW_WORLD_RISING}, ALL_REGIONS, 134616, ProductType.GOOD),
    A1800Product("Souvenirs", DLC.TOURIST_SEASON, ALL_REGIONS, 133532, ProductType.GOOD),

    A1800Product("Tourist Mooring", DLC.TOURIST_SEASON, Region.OW, 133891, ProductType.SERVICE),
    A1800Product("Zoo", DLC.TOURIST_SEASON, Region.OW, 601485, ProductType.SERVICE),
    A1800Product("Museum", DLC.TOURIST_SEASON, Region.OW, 133535, ProductType.SERVICE),
    A1800Product("Restaurant", DLC.TOURIST_SEASON, Region.OW, 132751, ProductType.SERVICE),
    A1800Product("Cafe", DLC.TOURIST_SEASON, Region.OW, 132755, ProductType.SERVICE),
    A1800Product("Bar", DLC.TOURIST_SEASON, Region.OW, 132754, ProductType.SERVICE),
    A1800Product("The Iron Tower", DLC.TOURIST_SEASON, Region.OW, 132761, ProductType.SERVICE),

    ### Needs Botanica ###
    A1800Product("Botanical Garden", DLC.BOTANICA | DLC.TOURIST_SEASON, Region.OW, 355, ProductType.SERVICE),

    ### Needs Seat of Power ###
    A1800Product("Palace", DLC.SEAT_OF_POWER | DLC.TOURIST_SEASON, Region.OW, 134257, ProductType.SERVICE),

    ### Needs Docklands ###
    A1800Product("Docklands", DLC.DOCKLANDS | DLC.TOURIST_SEASON, Region.OW, 134781, ProductType.SERVICE),

    ################################################################################################################
    ### THE_HIGH_LIFE                                                                                            ###
    ################################################################################################################
    A1800Product("Department Store (Blank)", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.META),
    A1800Product("Furniture Store (Blank)", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.META),
    A1800Product("Drug Store (Blank)", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.META),

    A1800Product("Skyline Tower: Foundations", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.STAGE),
    A1800Product("Skyline Tower: Superstructure", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.STAGE),
    A1800Product("Skyline Tower: Glazing", DLC.THE_HIGH_LIFE, Region.OW, 0, ProductType.STAGE),

    A1800Product("Elevators", DLC.THE_HIGH_LIFE, ALL_REGIONS, 134623, ProductType.GOOD),
    # Cinnamon -> Tourist Season
    A1800Product("Chewing Gum", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135186, ProductType.GOOD),
    # Citrus -> Tourist Season
    A1800Product("Biscuits", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135229, ProductType.GOOD),
    # Camphor Wax -> Tourist Season
    A1800Product("Ethanol", {DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, ALL_REGIONS, 135130, ProductType.GOOD),
    A1800Product("Celluloid", {DLC.THE_HIGH_LIFE, DLC.NEW_WORLD_RISING}, ALL_REGIONS, 135150, ProductType.GOOD),
    A1800Product("Cherry Wood", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135087, ProductType.GOOD),
    A1800Product("Cognac", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135234, ProductType.GOOD),
    A1800Product("Resin", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135086, ProductType.GOOD),
    A1800Product("Lacquer", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135129, ProductType.GOOD),
    A1800Product("Typewriters", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135230, ProductType.GOOD),
    A1800Product("Billiard Tables", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135232, ProductType.GOOD),
    A1800Product("Violins", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135233, ProductType.GOOD),
    # Coconut Oil -> Tourist Season
    A1800Product("Toys", DLC.THE_HIGH_LIFE, ALL_REGIONS, 135231, ProductType.GOOD),

    A1800Product("Department Store", DLC.THE_HIGH_LIFE, Region.OW, 135108, ProductType.SERVICE),
    A1800Product("Furniture Store", DLC.THE_HIGH_LIFE, Region.OW, 135107, ProductType.SERVICE),
    A1800Product("Drug Store", DLC.THE_HIGH_LIFE, Region.OW, 135109, ProductType.SERVICE),

    A1800Product("Toasters", DLC.THE_HIGH_LIFE, Region.OW, 135816, ProductType.STORE),
    A1800Product("Vacuum Cleaners", DLC.THE_HIGH_LIFE, Region.OW, 135877, ProductType.STORE),
    A1800Product("Crockery", DLC.THE_HIGH_LIFE, Region.OW, 135876, ProductType.STORE),
    A1800Product("Banker's Lamps", DLC.THE_HIGH_LIFE, Region.OW, 135880, ProductType.STORE),
    A1800Product("Vanity Screens", DLC.THE_HIGH_LIFE, Region.OW, 135881, ProductType.STORE),
    A1800Product("Writing Desks", DLC.THE_HIGH_LIFE, Region.OW, 135882, ProductType.STORE),
    A1800Product("Toothpaste", DLC.THE_HIGH_LIFE, Region.OW, 135885, ProductType.STORE),
    A1800Product("Detergent", DLC.THE_HIGH_LIFE, Region.OW, 135886, ProductType.STORE),
    A1800Product("Lipstick", DLC.THE_HIGH_LIFE, Region.OW, 135887, ProductType.STORE),

    ### Needs The Passage ###
    A1800Product("Refrigerators", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW, 135878, ProductType.STORE),
    A1800Product("Four-Poster Beds", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW, 135883, ProductType.STORE),
    A1800Product("Face Cream", DLC.THE_PASSAGE | DLC.THE_HIGH_LIFE, Region.OW, 135888, ProductType.STORE),

    ### Needs Land of Lions ###
    A1800Product("Briefcases", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW, 135879, ProductType.STORE),
    A1800Product("Lounge Seating", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW, 135884, ProductType.STORE),
    A1800Product("Pomade", DLC.LAND_OF_LIONS | DLC.THE_HIGH_LIFE, Region.OW, 135889, ProductType.STORE),

    ### Needs Tourist Season ###
    A1800Product("Skyline Tower", DLC.TOURIST_SEASON | DLC.THE_HIGH_LIFE, Region.OW, 137757, ProductType.SERVICE),

    ################################################################################################################
    ### SEEDS_OF_CHANGE                                                                                          ###
    ################################################################################################################
    A1800Product("Hot Sauce", DLC.SEEDS_OF_CHANGE, ALL_REGIONS, 25506, ProductType.GOOD),
    A1800Product("Atole", DLC.SEEDS_OF_CHANGE, ALL_REGIONS, 25131, ProductType.GOOD),
    A1800Product("Dung", DLC.SEEDS_OF_CHANGE, ALL_REGIONS, 24807, ProductType.GOOD),
    A1800Product("Fertiliser", DLC.SEEDS_OF_CHANGE, ALL_REGIONS, 24808, ProductType.GOOD),

    A1800Product("Hacienda", DLC.SEEDS_OF_CHANGE, Region.NW, 25546, ProductType.SERVICE),

    ################################################################################################################
    ### EMPIRE_OF_THE_SKIES                                                                                      ###
    ################################################################################################################
    A1800Product("Airship Platform", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 0, ProductType.META),
    A1800Product("Airmail Sorting Office", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 0, ProductType.META),
    A1800Product("Airship Platform", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 0, ProductType.META),
    A1800Product("Airmail Sorting Office", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 0, ProductType.META),

    A1800Product("Rigid Airship Hangar: Foundations", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 0, ProductType.STAGE),
    A1800Product("Rigid Airship Hangar: Structure", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 0, ProductType.STAGE),
    A1800Product("Rigid Airship Hangar: Roof", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 0, ProductType.STAGE),
    A1800Product("Rigid Airship Hangar: Foundations", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 0, ProductType.STAGE),
    A1800Product("Rigid Airship Hangar: Structure", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 0, ProductType.STAGE),
    A1800Product("Rigid Airship Hangar: Roof", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 0, ProductType.STAGE),

    A1800Product("Local Mail", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 535, ProductType.GOOD),
    A1800Product("Regional Mail", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 536, ProductType.GOOD),
    A1800Product("Overseas Mail", DLC.EMPIRE_OF_THE_SKIES, Region.OW, 2524, ProductType.GOOD),
    A1800Product("Local Mail", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 535, ProductType.GOOD),
    A1800Product("Regional Mail", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 536, ProductType.GOOD),
    A1800Product("Overseas Mail", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 2524, ProductType.GOOD),
    A1800Product("Bauxite", {DLC.EMPIRE_OF_THE_SKIES, DLC.NEW_WORLD_RISING}, ALL_REGIONS, 836, ProductType.GOOD),
    A1800Product("Aluminium Profiles", {DLC.EMPIRE_OF_THE_SKIES,
                 DLC.NEW_WORLD_RISING}, ALL_REGIONS, 838, ProductType.GOOD),
    A1800Product("Industrial Lubricant", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 1414, ProductType.GOOD),
    A1800Product("Helium", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 840, ProductType.GOOD),
    A1800Product("Bombs", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 846, ProductType.GOOD),
    A1800Product("Sea Mines", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 847, ProductType.GOOD),
    A1800Product("Pamphlets", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 848, ProductType.GOOD),
    A1800Product("Care Packages", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 849, ProductType.GOOD),
    A1800Product("Water Drop", DLC.EMPIRE_OF_THE_SKIES, ALL_REGIONS, 850, ProductType.GOOD),

    # Needs The Passage
    A1800Product("Airship Platform", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 0, ProductType.META),
    A1800Product("Airmail Sorting Office", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 0, ProductType.META),

    A1800Product("Local Mail", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 535, ProductType.GOOD),
    A1800Product("Regional Mail", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 536, ProductType.GOOD),
    A1800Product("Overseas Mail", DLC.THE_PASSAGE | DLC.EMPIRE_OF_THE_SKIES, Region.AR, 2524, ProductType.GOOD),

    ################################################################################################################
    ### NEW_WORLD_RISING                                                                                         ###
    ################################################################################################################
    A1800Product("Nandu Farm", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.META),
    A1800Product("Cattle Farm", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.META),
    A1800Product("Alpaca Farm", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.META),
    A1800Product("Grand Stadium: Football Championships", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.META),

    A1800Product("Dam: Foundations", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.STAGE),
    A1800Product("Dam: Structure", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.STAGE),
    A1800Product("Dam: Engineering", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.STAGE),
    A1800Product("Grand Stadium: Foundations", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.STAGE),
    A1800Product("Grand Stadium: Superstructure", DLC.NEW_WORLD_RISING, Region.NW, 0, ProductType.STAGE),

    A1800Product("Artistas", DLC.NEW_WORLD_RISING, Region.NW, 5403, ProductType.WORKFORCE),

    # Bauxite -> Empire of the Skies
    # Aluminium Profiles -> Empire of the Skies
    A1800Product("Nandu Leather", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5384, ProductType.GOOD),
    A1800Product("Nandu Feathers", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5401, ProductType.GOOD),
    A1800Product("Soccer Balls", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5803, ProductType.GOOD),
    A1800Product("Herbs", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5383, ProductType.GOOD),
    # Citrus -> Tourist Season or The High Life
    A1800Product("Mezcal", DLC.NEW_WORLD_RISING, ALL_REGIONS, 6600, ProductType.GOOD),
    A1800Product("Calamari", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5380, ProductType.GOOD),
    A1800Product("Jalea", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5381, ProductType.GOOD),
    A1800Product("Milk", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5385, ProductType.GOOD),
    A1800Product("Ice Cream", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5382, ProductType.GOOD),
    A1800Product("Orchid", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5386, ProductType.GOOD),
    # Coconut Oil -> Tourist Season or The High Life
    # Ethanol -> The High Life
    A1800Product("Perfumes", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5388, ProductType.GOOD),
    A1800Product("Minerals", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5398, ProductType.GOOD),
    A1800Product("Pigments", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5400, ProductType.GOOD),
    A1800Product("Costumes", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5389, ProductType.GOOD),
    A1800Product("Fire Extinguishers", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5393, ProductType.GOOD),
    # Camphor Wax -> Tourist Season or The High Life
    # Celluloid -> The High Life
    A1800Product("Electric Cables", DLC.NEW_WORLD_RISING, ALL_REGIONS, 6280, ProductType.GOOD),
    A1800Product("Motor", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5390, ProductType.GOOD),
    A1800Product("Fans", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5395, ProductType.GOOD),
    A1800Product("Film Reels", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5392, ProductType.GOOD),
    A1800Product("Police Equipment", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5394, ProductType.GOOD),
    A1800Product("Scooters", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5391, ProductType.GOOD),
    A1800Product("Medicine", DLC.NEW_WORLD_RISING, ALL_REGIONS, 5397, ProductType.GOOD),

    A1800Product("Electricity", DLC.NEW_WORLD_RISING, Region.NW, 1010354, ProductType.SERVICE),
    A1800Product("Beach", DLC.NEW_WORLD_RISING, Region.NW, 6265, ProductType.SERVICE),
    A1800Product("Samba School", DLC.NEW_WORLD_RISING, Region.NW, 5831, ProductType.SERVICE),
    A1800Product("Cinema", DLC.NEW_WORLD_RISING, Region.NW, 5830, ProductType.SERVICE),
]

_a1800_populations = [product for product in _a1800_products if product.type == ProductType.WORKFORCE]

# Assure populations only have a single region flag
for population in _a1800_products:
    if population.type == ProductType.WORKFORCE:
        assert population.region in Region.__members__.values(), \
            f"Population {population.name} has multiple regions: {population.region}"


class _Products:
    _initialized: bool = False

    def init(self, parsed_options: ParsedOptions) -> None:
        global _a1800_products, _a1800_populations

        self._a1800_products = [product for product in _a1800_products if any(
            dlc in parsed_options.enabled_dlcs for dlc in product.dlc)]
        self._a1800_populations = [population for population in _a1800_populations if any(
            dlc in parsed_options.enabled_dlcs for dlc in population.dlc)]

        self._initialized = True

    def get_products(self) -> Sequence[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return self._a1800_products

    def find_products(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return (product for product in self._a1800_products if product.name == name and region in product.region)

    def get_populations(self) -> Sequence[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return self._a1800_populations

    def find_populations(self, name: str, region: Region = NO_REGION) -> Iterator[A1800Product]:
        assert self._initialized, "The Anno 1800 products module was used before it was initialized."
        return (population for population in self._a1800_populations if population.name == name and region in population.region)


PRODUCTS = _Products()
