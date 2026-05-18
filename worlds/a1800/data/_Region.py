from collections.abc import Sequence
from dataclasses import dataclass

from ._Enums import ALL_REGIONS, DLC, Region
from ._Requirement import A1800Requirement


@dataclass
class A1800Region:
    region: Region
    dlc: DLC
    requirements: set[A1800Requirement]


_a1800_regions: dict[Region, A1800Region] = {
    Region.OW: A1800Region(Region.OW, DLC.VANILLA, set()),
    Region.NW: A1800Region(Region.NW, DLC.VANILLA, {
        A1800Requirement("Artisans", Region.OW),
        A1800Requirement("Sea Travel", ALL_REGIONS),
    }),
}

# Assure regions are unique
for region, anno_region in _a1800_regions.items():
    assert anno_region.region == region, f"Region {region} dict entry does not match"


def get_regions() -> Sequence[A1800Region]:
    global _a1800_regions
    return list(_a1800_regions.values())


def find_region(region: Region) -> A1800Region:
    global _a1800_regions
    return _a1800_regions[region]


def get_start_region() -> A1800Region:
    global _a1800_regions
    return next(region for region in _a1800_regions.values() if not region.requirements)
