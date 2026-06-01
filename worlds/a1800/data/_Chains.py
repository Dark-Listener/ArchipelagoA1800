from collections.abc import Sequence
from typing import Iterator, Optional

from ._Enums import DLC, NO_REGION, Region
from ._ParsedOptions import ParsedOptions


class A1800Chain:
    name: str
    dlc: set[DLC]
    region: Region
    guid: int
    elements: set[tuple[str, Region]]

    def __init__(self, name: str, dlc: DLC | set[DLC], region: Region, guid: int, elements: set[tuple[str, Region]]) -> None:
        self.name = name
        self.dlc = {dlc} if isinstance(dlc, DLC) else dlc
        self.region = region
        self.guid = guid
        self.elements = elements

    def __str__(self) -> str:
        return f"(Chain: {self.name}, {self.region})"


_a1800_chains: list[A1800Chain] = [
    ################################################################################################################
    ### VANILLA                                                                                                  ###
    ################################################################################################################
    A1800Chain("Timber", DLC.VANILLA, Region.OW, 500091,
               {("Lumberjack's Hut", Region.OW), ("Sawmill", Region.OW)}),
    A1800Chain("Work Clothes", DLC.VANILLA, Region.OW, 500505,
               {("Sheep Farm", Region.OW), ("Framework Knitters", Region.OW)}),
    A1800Chain("Schnapps", DLC.VANILLA, Region.OW, 500002,
               {("Potato Farm", Region.OW), ("Schnapps Distillery", Region.OW)}),
    A1800Chain("Bricks", DLC.VANILLA, Region.OW, 500024,
               {("Clay Pit", Region.OW), ("Brick Factory", Region.OW)}),
    A1800Chain("Sausages", DLC.VANILLA, Region.OW, 25000244,
               {("Pig Farm", Region.OW), ("Slaughterhouse", Region.OW)}),
    A1800Chain("Bread", DLC.VANILLA, Region.OW, 500004,
               {("Grain Farm", Region.OW), ("Flour Mill", Region.OW), ("Bakery", Region.OW)}),
    A1800Chain("Sails", DLC.VANILLA, Region.OW, 500009,
               {("Sheep Farm", Region.OW), ("Sailmakers", Region.OW)}),
    A1800Chain("Steel Beams", DLC.VANILLA, Region.OW, 500005,
               {("Charcoal Kiln", Region.OW), ("Iron Mine", Region.OW), ("Furnace", Region.OW),
                ("Steelworks", Region.OW)}),
    A1800Chain("Soap", DLC.VANILLA, Region.OW, 25000220,
               {("Pig Farm", Region.OW), ("Rendering Works", Region.OW), ("Soap Factory", Region.OW)}),
    A1800Chain("Weapons", DLC.VANILLA, Region.OW, 500145,
               {("Charcoal Kiln", Region.OW), ("Iron Mine", Region.OW), ("Furnace", Region.OW),
                ("Weapon Factory", Region.OW)}),
    A1800Chain("Beer", DLC.VANILLA, Region.OW, 500006,
               {("Grain Farm", Region.OW), ("Malthouse", Region.OW), ("Hop Farm", Region.OW), ("Brewery", Region.OW)}),
    A1800Chain("Windows", DLC.VANILLA, Region.OW, 500010,
               {("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Lumberjack's Hut", Region.OW),
                ("Window Makers", Region.OW)}),
    A1800Chain("Canned Food", DLC.VANILLA, Region.OW, 500008,
               {("Cattle Farm", Region.OW), ("Red Pepper Farm", Region.OW), ("Artisanal Kitchen", Region.OW),
                ("Iron Mine", Region.OW), ("Cannery", Region.OW)}),
    A1800Chain("Sewing Machines", DLC.VANILLA, Region.OW, 500003,
               {("Coal Mine", Region.OW), ("Iron Mine", Region.OW), ("Furnace", Region.OW),
                ("Lumberjack's Hut", Region.OW), ("Sewing Machine Factory", Region.OW)}),
    A1800Chain("Rum", DLC.VANILLA, Region.OW, 500013,
               {("Sugar Cane Plantation", Region.NW), ("Lumberjack's Hut", Region.OW), ("Rum Distillery", Region.NW)}),
    A1800Chain("Fur Coats", DLC.VANILLA, Region.OW, 500019,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Hunting Cabin", Region.OW),
                ("Fur Dealer", Region.OW)}),
    A1800Chain("Reinforced Concrete", DLC.VANILLA, Region.OW, 500016,
               {("Coal Mine", Region.OW), ("Iron Mine", Region.OW), ("Furnace", Region.OW),
                ("Limestone Quarry", Region.OW), ("Concrete Factory", Region.OW)}),
    A1800Chain("Electricity", DLC.VANILLA, Region.OW, 500506,
               {("Oil Refinery", Region.OW), ("Rails", Region.OW | Region.NW), ("Small Oil Harbour", Region.OW),
                ("Oil Store", Region.OW), ("Oil Power Plant", Region.OW)}),
    A1800Chain("Spectacles", DLC.VANILLA, Region.OW, 500901,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Spectacle Factory", Region.OW)}),
    A1800Chain("Penny Farthings", DLC.VANILLA, Region.OW, 500012,
               {("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Caoutchouc Plantation", Region.NW), ("Bicycle Factory", Region.OW)}),
    A1800Chain("Steam Motors", DLC.VANILLA, Region.OW, 500023,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Motor Assembly Line", Region.OW)}),
    A1800Chain("Advanced Weapons", DLC.VANILLA, Region.OW, 500029,
               {("Pig Farm", Region.OW), ("Rendering Works", Region.OW), ("Saltpetre Works", Region.OW),
                ("Dynamite Factory", Region.OW), ("Iron Mine", Region.OW), ("Coal Mine", Region.OW),
                ("Furnace", Region.OW), ("Heavy Weapons Factory", Region.OW)}),
    A1800Chain("Coffee", DLC.VANILLA, Region.OW, 500902,
               {("Coffee Plantation", Region.NW), ("Coffee Roaster", Region.NW)}),
    A1800Chain("Pocket Watches", DLC.VANILLA, Region.OW, 500015,
               {("Gold Mine", Region.NW), ("Coal Mine", Region.OW), ("Goldsmiths", Region.OW),
                ("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Clockmakers", Region.OW)}),
    A1800Chain("Light Bulbs", DLC.VANILLA, Region.OW, 500017,
               {("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Coal Mine", Region.OW),
                ("Filament Factory", Region.OW), ("Light Bulb Factory", Region.OW)}),
    A1800Chain("Champagne", DLC.VANILLA, Region.OW, 500434,
               {("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Vineyard", Region.OW),
                ("Champagne Cellar", Region.OW)}),
    A1800Chain("Cigars", DLC.VANILLA, Region.OW, 500018,
               {("Tobacco Plantation", Region.NW), ("Lumberjack's Hut", Region.OW), ("Marquetry Workshop", Region.OW),
                ("Cigar Factory", Region.NW)}),
    A1800Chain("Jewellery", DLC.VANILLA, Region.OW, 500022,
               {("Gold Mine", Region.NW), ("Coal Mine", Region.OW), ("Goldsmiths", Region.OW),
                ("Pearl Farm", Region.NW), ("Jewellers", Region.OW)}),
    A1800Chain("Chocolate", DLC.VANILLA, Region.OW, 500014,
               {("Sugar Cane Plantation", Region.NW), ("Sugar Refinery", Region.NW), ("Cocoa Plantation", Region.NW),
                ("Chocolate Factory", Region.NW)}),
    A1800Chain("Gramophones", DLC.VANILLA, Region.OW, 500020,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Lumberjack's Hut", Region.OW), ("Marquetry Workshop", Region.NW), ("Gramophone Factory", Region.OW)}),
    A1800Chain("Steam Carriages", DLC.VANILLA, Region.OW, 500021,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Motor Assembly Line", Region.OW), ("Lumberjack's Hut", Region.OW),
                ("Caoutchouc Plantation", Region.NW), ("Coachmakers", Region.OW), ("Cab Assembly Line", Region.OW)}),
    A1800Chain("Timber", DLC.VANILLA, Region.NW, 500904,
               {("Lumberjack's Hut", Region.NW), ("Sawmill", Region.NW)}),
    A1800Chain("Fried Plantains", DLC.VANILLA, Region.NW, 500905,
               {("Fish Oil Factory", Region.NW), ("Plantain Plantation", Region.NW),
                ("Fried Plantain Kitchen", Region.NW)}),
    A1800Chain("Fur Coats", DLC.VANILLA, Region.NW, 501637,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Hunting Cabin", Region.OW),
                ("Fur Dealer", Region.OW)}),
    A1800Chain("Rum", DLC.VANILLA, Region.NW, 500906,
               {("Sugar Cane Plantation", Region.NW), ("Lumberjack's Hut", Region.NW), ("Rum Distillery", Region.NW)}),
    A1800Chain("Sails", DLC.VANILLA, Region.NW, 500907,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Sailmakers", Region.NW)}),
    A1800Chain("Ponchos", DLC.VANILLA, Region.NW, 500908,
               {("Alpaca Farm", Region.NW), ("Poncho Darner", Region.NW)}),
    A1800Chain("Bricks", DLC.VANILLA, Region.NW, 500910,
               {("Clay Pit", Region.NW), ("Brick Factory", Region.NW)}),
    A1800Chain("Tortillas", DLC.VANILLA, Region.NW, 500911,
               {("Cattle Farm", Region.NW), ("Corn Farm", Region.NW), ("Tortilla Maker", Region.NW)}),
    A1800Chain("Coffee", DLC.VANILLA, Region.NW, 500913,
               {("Coffee Plantation", Region.NW), ("Coffee Roaster", Region.NW)}),
    A1800Chain("Bombins", DLC.VANILLA, Region.NW, 500912,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Alpaca Farm", Region.NW),
                ("Felt Producer", Region.NW), ("Bombin Weaver", Region.NW)}),
    A1800Chain("Electricity", DLC.VANILLA, Region.NW, 500916,
               {("Oil Refinery", Region.NW), ("Rails", Region.OW | Region.NW), ("Small Oil Harbour", Region.NW),
                ("Oil Store", Region.NW), ("Oil Power Plant", Region.OW)}),
    A1800Chain("Beer", DLC.VANILLA, Region.NW, 501429,
               {("Grain Farm", Region.OW), ("Malthouse", Region.OW), ("Hop Farm", Region.OW), ("Brewery", Region.OW)}),
    A1800Chain("Cigars", DLC.VANILLA, Region.NW, 500914,
               {("Tobacco Plantation", Region.NW), ("Lumberjack's Hut", Region.NW), ("Marquetry Workshop", Region.NW),
                ("Cigar Factory", Region.NW)}),
    A1800Chain("Sewing Machines", DLC.VANILLA, Region.NW, 501254,
               {("Coal Mine", Region.OW), ("Iron Mine", Region.OW), ("Furnace", Region.OW),
                ("Lumberjack's Hut", Region.NW), ("Sewing Machine Factory", Region.OW)}),
    A1800Chain("Chocolate", DLC.VANILLA, Region.NW, 500909,
               {("Sugar Cane Plantation", Region.NW), ("Sugar Refinery", Region.NW), ("Cocoa Plantation", Region.NW),
                ("Chocolate Factory", Region.NW)}),

    ################################################################################################################
    ### THE_PASSAGE                                                                                              ###
    ################################################################################################################
    A1800Chain("Electricity (Gas)", DLC.THE_PASSAGE, Region.OW, 117559,
               {("Arctic Gas Mine", Region.AR), ("Gas-Fired Power Plant", Region.OW)}),
    A1800Chain("Heater", DLC.THE_PASSAGE, Region.AR, 112856,
               {("Charcoal Kiln", Region.AR), ("Heater", Region.AR)}),
    A1800Chain("Timber", DLC.THE_PASSAGE, Region.AR, 112709,
               {("Lumberjack's Hut", Region.AR), ("Sawmill", Region.AR)}),
    A1800Chain("Pemmican", DLC.THE_PASSAGE, Region.AR, 112710,
               {("Caribou Hunting Cabin", Region.AR), ("Whaling Station", Region.AR),
                ("Pemmican Cookhouse", Region.AR)}),
    A1800Chain("Sleeping Bags", DLC.THE_PASSAGE, Region.AR, 112712,
               {("Goose Farm", Region.AR), ("Seal Hunting Docks", Region.AR), ("Sleeping Bag Factory", Region.AR)}),
    A1800Chain("Oil Lamps", DLC.THE_PASSAGE, Region.AR, 112713,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Whaling Station", Region.AR), ("Oil Lamp Factory", Region.AR)}),
    A1800Chain("Schnapps", DLC.THE_PASSAGE, Region.AR, 117077,
               {("Potato Farm", Region.OW), ("Schnapps Distillery", Region.OW)}),
    A1800Chain("Parkas", DLC.THE_PASSAGE, Region.AR, 112711,
               {("Seal Hunting Docks", Region.AR), ("Bear Hunting Cabin", Region.AR), ("Parka Factory", Region.AR)}),
    A1800Chain("Canned Food", DLC.THE_PASSAGE, Region.AR, 117268,
               {("Cattle Farm", Region.OW), ("Red Pepper Farm", Region.OW), ("Artisanal Kitchen", Region.OW),
                ("Iron Mine", Region.OW), ("Cannery", Region.OW)}),
    A1800Chain("Husky Sleds", DLC.THE_PASSAGE, Region.AR, 112714,
               {("Lumberjack's Hut", Region.AR), ("Seal Hunting Docks", Region.AR), ("Sled Frame Factory", Region.AR),
                ("Husky Farm", Region.AR), ("Husky Sled Factory", Region.AR)}),
    A1800Chain("Coffee", DLC.THE_PASSAGE, Region.AR, 117075,
               {("Coffee Plantation", Region.NW), ("Coffee Roaster", Region.NW)}),
    A1800Chain("Electricity (Gas)", DLC.THE_PASSAGE, Region.AR, 117556,
               {("Arctic Gas Mine", Region.AR), ("Gas-Fired Power Plant", Region.OW)}),

    ################################################################################################################
    ### BRIGHT_HARVEST                                                                                           ###
    ################################################################################################################
    A1800Chain("Fuel", DLC.BRIGHT_HARVEST, Region.OW, 269756,
               {("Oil Refinery", Region.OW), ("Rails", Region.OW | Region.NW), ("Small Oil Harbour", Region.OW),
                ("Oil Store", Region.OW), ("Fuel Station", Region.OW)}),
    A1800Chain("Fuel", DLC.BRIGHT_HARVEST, Region.NW, 269835,
               {("Oil Refinery", Region.NW), ("Rails", Region.OW | Region.NW), ("Small Oil Harbour", Region.NW),
                ("Oil Store", Region.NW), ("Fuel Station", Region.NW)}),

    ################################################################################################################
    ### LAND_OF_LIONS                                                                                            ###
    ################################################################################################################
    A1800Chain("Coffee (alt)", DLC.LAND_OF_LIONS, Region.OW, 124740,
               {("Grain Farm", Region.OW), ("Malthouse", Region.OW), ("Advanced Coffee Roaster", Region.OW)}),
    A1800Chain("Rum (alt)", DLC.LAND_OF_LIONS, Region.OW, 124741,
               {("Potato Farm", Region.OW), ("Coal Mine", Region.OW), ("Advanced Rum Distillery", Region.OW)}),
    A1800Chain("Cotton Fabric (alt)", DLC.LAND_OF_LIONS, Region.OW, 124742,
               {("Lumberjack's Hut", Region.OW), ("Sheep Farm", Region.OW), ("Advanced Cotton Mill", Region.OW)}),
    A1800Chain("Rum (Scholars)", DLC.LAND_OF_LIONS, Region.OW, 127050,
               {("Sugar Cane Plantation", Region.NW), ("Lumberjack's Hut", Region.OW), ("Rum Distillery", Region.NW)}),
    A1800Chain("Bombins", DLC.LAND_OF_LIONS, Region.OW, 120290,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Alpaca Farm", Region.NW),
                ("Felt Producer", Region.NW), ("Bombin Weaver", Region.NW)}),
    A1800Chain("Leather Boots", DLC.LAND_OF_LIONS, Region.OW, 118737,
               {("Sanga Farm", Region.EN), ("Bootmakers", Region.OW)}),
    A1800Chain("Tailored Suits", DLC.LAND_OF_LIONS, Region.OW, 118738,
               {("Cotton Plantation", Region.NW), ("Cotton Mill", Region.NW), ("Linseed Farm", Region.EN),
                ("Linen Mill", Region.EN), ("Tailor's Shop", Region.OW)}),
    A1800Chain("Hibiscus Tea", DLC.LAND_OF_LIONS, Region.OW, 120286,
               {("Hibiscus Farm", Region.EN), ("Tea Spicer", Region.EN)}),
    A1800Chain("Seafood Stew", DLC.LAND_OF_LIONS, Region.OW, 120287,
               {("Spice Farm", Region.EN), ("Teff Farm", Region.EN), ("Teff Mill", Region.EN),
                ("Lobster Fishery", Region.EN), ("Wat Kitchen", Region.EN)}),
    A1800Chain("Tapestries", DLC.LAND_OF_LIONS, Region.OW, 120288,
               {("Linseed Farm", Region.EN), ("Linen Mill", Region.EN), ("Indigo Farm", Region.EN),
                ("Tapestry Looms", Region.EN)}),
    A1800Chain("Clay Pipes", DLC.LAND_OF_LIONS, Region.OW, 120289,
               {("Clay Collector", Region.EN), ("Tobacco Plantation", Region.NW), ("Pipe Maker", Region.EN)}),
    A1800Chain("Telephones", DLC.LAND_OF_LIONS, Region.OW, 118739,
               {("Lumberjack's Hut", Region.OW), ("Marquetry Workshop", Region.OW), ("Coal Mine", Region.OW),
                ("Filament Factory", Region.OW), ("Telephone Manufacturer", Region.OW)}),
    A1800Chain("Irrigation", DLC.LAND_OF_LIONS, Region.EN, 117782,
               {("Canal", Region.EN), ("Water Pump", Region.EN)}),
    A1800Chain("Finery", DLC.LAND_OF_LIONS, Region.EN, 114565,
               {("Linseed Farm", Region.EN), ("Linen Mill", Region.EN), ("Embroiderer", Region.EN)}),
    A1800Chain("Dried Meat", DLC.LAND_OF_LIONS, Region.EN, 114556,
               {("Sanga Farm", Region.EN), ("Salt Works", Region.EN), ("Dry-House", Region.EN)}),
    A1800Chain("Hibiscus Tea", DLC.LAND_OF_LIONS, Region.EN, 114563,
               {("Hibiscus Farm", Region.EN), ("Tea Spicer", Region.EN)}),
    A1800Chain("Mud Bricks", DLC.LAND_OF_LIONS, Region.EN, 114566,
               {("Clay Collector", Region.EN), ("Teff Farm", Region.EN), ("Brick Dry-House", Region.EN)}),
    A1800Chain("Ceramics", DLC.LAND_OF_LIONS, Region.EN, 118726,
               {("Clay Collector", Region.EN), ("Indigo Farm", Region.EN), ("Ceramics Workshop", Region.EN)}),
    A1800Chain("Tapestries", DLC.LAND_OF_LIONS, Region.EN, 114568,
               {("Linseed Farm", Region.EN), ("Linen Mill", Region.EN), ("Indigo Farm", Region.EN),
                ("Tapestry Looms", Region.EN)}),
    A1800Chain("Seafood Stew", DLC.LAND_OF_LIONS, Region.EN, 114570,
               {("Spice Farm", Region.EN), ("Teff Farm", Region.EN), ("Teff Mill", Region.EN),
                ("Lobster Fishery", Region.EN), ("Wat Kitchen", Region.EN)}),
    A1800Chain("Clay Pipes", DLC.LAND_OF_LIONS, Region.EN, 114619,
               {("Clay Collector", Region.EN), ("Tobacco Plantation", Region.NW), ("Pipe Maker", Region.EN)}),
    A1800Chain("Illuminated Script", DLC.LAND_OF_LIONS, Region.EN, 117713,
               {("Lumberjack's Hut", Region.OW), ("Paper Mill", Region.EN), ("Indigo Farm", Region.EN),
                ("Luminer", Region.EN)}),
    A1800Chain("Spectacles", DLC.LAND_OF_LIONS, Region.EN, 117740,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Spectacle Factory", Region.OW)}),
    A1800Chain("Lanterns", DLC.LAND_OF_LIONS, Region.EN, 117714,
               {("Sand Mine", Region.OW), ("Glassmakers", Region.OW), ("Cotton Plantation", Region.NW),
                ("Apiary", Region.EN), ("Chandler", Region.EN), ("Lanternsmith", Region.EN)}),

    ### Needs Bright Harvest ###
    A1800Chain("Fuel", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119030,
               {("Oil Refinery", Region.OW), ("Rails", Region.EN), ("Small Oil Harbour", Region.EN),
                ("Oil Store", Region.EN), ("Fuel Station", Region.EN)}),

    ################################################################################################################
    ### TOURIST_SEASON                                                                                           ###
    ################################################################################################################
    A1800Chain("Shampoo", DLC.TOURIST_SEASON, Region.OW, 137608,
               {("Pig Farm", Region.OW), ("Rendering Works", Region.OW), ("Soap Factory", Region.OW),
                ("Orchard: Cinnamon", Region.NW), ("Orchard: Coconut Oil", Region.NW),
                ("Chemical Plant: Shampoo", Region.OW)}),
    A1800Chain("Lemonade", DLC.TOURIST_SEASON, Region.OW, 137607,
               {("Orchard: Citrus", Region.NW), ("Sugar Cane Plantation", Region.NW), ("Sugar Refinery", Region.NW),
                ("Saltpetre Works", Region.OW), ("Chemical Plant: Lemonade", Region.OW)}),
    A1800Chain("Souvenirs", DLC.TOURIST_SEASON, Region.OW, 137609,
               {("Orchard: Camphor Wax", Region.NW), ("Cotton Plantation", Region.NW), ("Sand Mine", Region.OW),
                ("Glassmakers", Region.OW), ("Chemical Plant: Souvenirs", Region.OW)}),

    ################################################################################################################
    ### THE_HIGH_LIFE                                                                                            ###
    ################################################################################################################
    A1800Chain("Elevators", DLC.THE_HIGH_LIFE, Region.OW, 137602,
               {("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Motor Assembly Line", Region.OW), ("Lumberjack's Hut", Region.OW), ("Marquetry Workshop", Region.NW),
                ("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Assembly Line: Elevators", Region.OW)}),
    A1800Chain("Chewing Gum", DLC.THE_HIGH_LIFE, Region.OW | Region.NW, 137604,
               {("Orchard: Cinnamon", Region.NW), ("Sugar Cane Plantation", Region.NW), ("Sugar Refinery", Region.NW),
                ("Caoutchouc Plantation", Region.NW), ("Chemical Plant: Chewing Gum", Region.NW)}),
    A1800Chain("Biscuits", DLC.THE_HIGH_LIFE, Region.OW, 137601,
               {("Orchard: Citrus", Region.NW), ("Grain Farm", Region.OW), ("Flour Mill", Region.OW),
                ("Pig Farm", Region.OW), ("Rendering Works", Region.OW), ("Assembly Line: Biscuits", Region.OW)}),
    A1800Chain("Ethanol", DLC.THE_HIGH_LIFE, Region.NW, 137605,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW)}),
    A1800Chain("Celluloid", DLC.THE_HIGH_LIFE, Region.OW | Region.NW, 137606,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Camphor Wax", Region.NW), ("Cotton Plantation", Region.NW),
                ("Chemical Plant: Celluloid", Region.NW)}),
    A1800Chain("Cognac", DLC.THE_HIGH_LIFE, Region.OW, 137599,
               {("Sugar Cane Plantation", Region.NW), ("Sugar Refinery", Region.NW), ("Vineyard", Region.OW),
                ("Orchard: Cherry Wood", Region.OW), ("Artisan's Workshop: Cognac", Region.OW)}),
    A1800Chain("Lacquer", DLC.THE_HIGH_LIFE, Region.OW, 137603,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Resin", Region.OW), ("Sand Mine", Region.OW), ("Artisan's Workshop: Lacquer", Region.OW)}),
    A1800Chain("Typewriters", DLC.THE_HIGH_LIFE, Region.OW, 137600,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Resin", Region.OW), ("Sand Mine", Region.OW), ("Artisan's Workshop: Lacquer", Region.OW),
                ("Zinc Mine", Region.OW), ("Copper Mine", Region.OW), ("Brass Smeltery", Region.OW),
                ("Iron Mine", Region.OW), ("Coal Mine", Region.OW), ("Furnace", Region.OW),
                ("Assembly Line: Typewriters", Region.OW)}),
    A1800Chain("Billiard Tables", DLC.THE_HIGH_LIFE, Region.OW, 137597,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Camphor Wax", Region.NW), ("Cotton Plantation", Region.NW),
                ("Chemical Plant: Celluloid", Region.NW), ("Alpaca Farm", Region.NW), ("Felt Producer", Region.NW),
                ("Orchard: Cherry Wood", Region.OW), ("Artisan's Workshop: Billiard Tables", Region.OW)}),
    A1800Chain("Violins", DLC.THE_HIGH_LIFE, Region.OW, 137598,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Resin", Region.OW), ("Sand Mine", Region.OW), ("Artisan's Workshop: Lacquer", Region.OW),
                ("Orchard: Cherry Wood", Region.OW), ("Iron Mine", Region.OW), ("Coal Mine", Region.OW),
                ("Furnace", Region.OW), ("Artisan's Workshop: Violins", Region.OW)}),
    A1800Chain("Toys", DLC.THE_HIGH_LIFE, Region.OW, 137596,
               {("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Resin", Region.OW), ("Sand Mine", Region.OW), ("Artisan's Workshop: Lacquer", Region.OW),
                ("Corn Farm", Region.NW), ("Lumberjack's Hut", Region.NW), ("Chemical Plant: Ethanol", Region.NW),
                ("Orchard: Camphor Wax", Region.NW), ("Cotton Plantation", Region.NW),
                ("Chemical Plant: Celluloid", Region.NW), ("Alpaca Farm", Region.NW), ("Felt Producer", Region.NW),
                ("Artisan's Workshop: Toys", Region.OW)}),

    ################################################################################################################
    ### EMPIRE_OF_THE_SKIES                                                                                      ###
    ################################################################################################################
    A1800Chain("Aluminium Profiles", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 1351,
               {("Charcoal Kiln", Region.NW), ("Bauxite Mine", Region.NW), ("Aluminium Smelter", Region.NW)}),
    A1800Chain("Helium", DLC.EMPIRE_OF_THE_SKIES, Region.NW, 1361,
               {("Saltpetre Works", Region.OW), ("Fish Oil Factory", Region.NW), ("Industrial Oil Press", Region.NW),
                ("Clay Pit", Region.NW), ("Helium Extractor", Region.NW)}),
]


# Assure uniqueness
assert len(_a1800_chains) == len({chain.guid for chain in _a1800_chains}), "Duplicate guid in chains"
assert len(_a1800_chains) == len({(chain.name, chain.region) for chain in _a1800_chains}), \
    "Duplicate name/region pair in chains"


class _Chains:
    _initialized: bool = False

    def init(self, parsed_options: ParsedOptions) -> None:
        global _a1800_chains

        self._a1800_chains = [chain for chain in _a1800_chains if any(
            dlc in parsed_options.enabled_dlcs for dlc in chain.dlc)]

        self._initialized = True

    def get_chains(self) -> Sequence[A1800Chain]:
        assert self._initialized, "The Anno 1800 chains module was used before it was initialized."
        return self._a1800_chains

    def find_chains(self, name: str, unlock_name: str, unlock_region: Region, region: Optional[Region] = None) -> Iterator[A1800Chain]:
        assert self._initialized, "The Anno 1800 chains module was used before it was initialized."
        return (chain for chain in self._a1800_chains if chain.name == name and
                next((element_name for element_name, element_region in chain.elements
                      if element_name == unlock_name and element_region == unlock_region), None)
                and (region in chain.region if region else chain.region & unlock_region != NO_REGION))


CHAINS = _Chains()
