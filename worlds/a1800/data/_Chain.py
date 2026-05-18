from collections.abc import Sequence
from dataclasses import dataclass
from typing import Iterator

from ._Enums import DLC, NO_REGION, Region


@dataclass
class A1800Chain:
    name: str
    dlc: DLC
    region: Region
    guid: int
    elements: set[tuple[str, Region]]


_a1800_chains: list[A1800Chain] = [
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
]


def get_chains() -> Sequence[A1800Chain]:
    global _a1800_chains
    return _a1800_chains


def find_chains(name: str, region: Region = NO_REGION) -> Iterator[A1800Chain]:
    return (chain for chain in _a1800_chains if chain.name == name and region in chain.region)
