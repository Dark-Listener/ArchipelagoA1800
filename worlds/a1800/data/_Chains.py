from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator, Optional

from ._Enums import DLC, NO_REGION, Region


@dataclass
class A1800Chain:
    name: str
    dlc: DLC
    region: Region
    guid: int
    elements: set[tuple[str, Region]]


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
    ### Needs Bright Harvest ###
    A1800Chain("Fuel", DLC.BRIGHT_HARVEST | DLC.LAND_OF_LIONS, Region.EN, 119030,
               {("Oil Refinery", Region.OW), ("Rails", Region.EN), ("Small Oil Harbour", Region.EN),
                ("Oil Store", Region.EN), ("Fuel Station", Region.EN)}),
]


# Assure uniqueness
assert len(_a1800_chains) == len({chain.guid for chain in _a1800_chains}), "Duplicate guid in chains"
assert len(_a1800_chains) == len({(chain.name, chain.region) for chain in _a1800_chains}), \
    "Duplicate name/region pair in chains"


class _Chains:
    _initialized: bool = False

    def init(self, enabled_dlcs: DLC) -> None:
        global _a1800_chains

        self._a1800_chains = [chain for chain in _a1800_chains if chain.dlc in enabled_dlcs]

        self._initialized = True

    def get_chains(self) -> Sequence[A1800Chain]:
        assert self._initialized, "The Anno 1800 chains module was used before it was initialized."
        return self._a1800_chains

    def find_chains(self, name: str, unlock_name: str, unlock_region: Region, region: Optional[Region] = None) -> Iterator[A1800Chain]:
        assert self._initialized, "The Anno 1800 chains module was used before it was initialized."
        return (chain for chain in self._a1800_chains if chain.name == name and
                next((element_name for element_name, element_region in chain.elements
                      if element_name == unlock_name and element_region == unlock_region), None)
                and (chain.region == region if region else chain.region & unlock_region != NO_REGION))


CHAINS = _Chains()
