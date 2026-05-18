from dataclasses import dataclass
from typing import Iterator

from ._Enums import DLC, NO_REGION, Region


@dataclass
class A1800Chain:
    name: str
    dlc: DLC
    region: Region
    guid: int
    elements: set[str]


_a1800_chains: list[A1800Chain] = [
    A1800Chain("Timber", DLC.VANILLA, Region.OW, 500091, {"Lumberjack's Hut", "Sawmill"}),
    A1800Chain("Work Clothes", DLC.VANILLA, Region.OW, 500505, {"Sheep Farm", "Framework Knitters"}),
    A1800Chain("Schnapps", DLC.VANILLA, Region.OW, 500002, {"Potato Farm", "Schnapps Distillery"}),
    A1800Chain("Bricks", DLC.VANILLA, Region.OW, 500024, {"Clay Pit", "Brick Factory"}),
    A1800Chain("Sausages", DLC.VANILLA, Region.OW, 25000244, {"Pig Farm", "Slaughterhouse"}),
    A1800Chain("Bread", DLC.VANILLA, Region.OW, 500004, {"Grain Farm", "Flour Mill", "Bakery"}),
    A1800Chain("Sails", DLC.VANILLA, Region.OW, 500009, {"Sheep Farm", "Sailmakers"}),
    A1800Chain("Steel Beams", DLC.VANILLA, Region.OW, 500005, {"Charcoal Kiln", "Iron Mine", "Furnace", "Steelworks"}),
    A1800Chain("Soap", DLC.VANILLA, Region.OW, 25000220, {"Pig Farm", "Rendering Works", "Soap Factory"}),
    A1800Chain("Weapons", DLC.VANILLA, Region.OW, 500145, {"Charcoal Kiln", "Iron Mine", "Furnace", "Weapon Factory"}),
    A1800Chain("Beer", DLC.VANILLA, Region.OW, 500006, {"Grain Farm", "Malthouse", "Hop Farm", "Brewery"}),
]


def find_chains(name: str, region: Region = NO_REGION) -> Iterator[A1800Chain]:
    return (chain for chain in _a1800_chains if chain.name == name and region in chain.region)
