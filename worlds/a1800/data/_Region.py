from collections.abc import Sequence
from dataclasses import dataclass

from ._Enums import ALL_REGIONS, DLC, Region
from ._Requirement import A1800Requirement


@dataclass
class A1800Region:
    region: Region
    dlc: DLC
    requirements: set[A1800Requirement]


_a1800_regions: list[A1800Region] = [
    A1800Region(Region.OW, DLC.VANILLA, set()),
    A1800Region(Region.NW, DLC.VANILLA, {
        A1800Requirement("Artisans", Region.OW),
        A1800Requirement("Sea Travel", ALL_REGIONS),
    }),
]

# Assure regions only have a single region flag
for region in _a1800_regions:
    assert region.region in Region.__members__.values()


def get_regions() -> Sequence[A1800Region]:
    global _a1800_regions
    return _a1800_regions


def get_start_region() -> A1800Region:
    global _a1800_regions
    return next(region for region in _a1800_regions if not region.requirements)
