from collections.abc import Sequence
from dataclasses import dataclass, field

from ._Enums import ALL_REGIONS, DLC, Region, START_REGION
from ._Requirement import A1800Requirement


@dataclass
class A1800Region:
    region: Region
    dlc: DLC
    enter_requirements: set[A1800Requirement]
    build_requirements: set[A1800Requirement]
    requirements: set[A1800Requirement] = field(default_factory=lambda: set())

    def __post_init__(self) -> None:
        self.requirements = self.enter_requirements | self.build_requirements


_a1800_regions: dict[Region, A1800Region] = {
    Region.OW: A1800Region(Region.OW, DLC.VANILLA, set(), set()),
    Region.NW: A1800Region(Region.NW, DLC.VANILLA, {
        A1800Requirement("Artisans", Region.OW),
        A1800Requirement("Sea Travel", ALL_REGIONS),
    }, {
        A1800Requirement("Dirt Road", Region.NW),
        A1800Requirement("Small Trading Post", Region.NW),
        A1800Requirement("Small Warehouse", Region.NW),
    }),
}

# Assure START_REGION has no requirements
assert not _a1800_regions[START_REGION].requirements, \
    f"Start region {_a1800_regions[START_REGION]} has non-empty requirements"
# Assure regions are unique
for region, anno_region in _a1800_regions.items():
    assert anno_region.region == region, f"Region {region} dict entry does not match"


def get_regions() -> Sequence[A1800Region]:
    global _a1800_regions
    return list(_a1800_regions.values())


def find_region(region: Region) -> A1800Region:
    global _a1800_regions
    return _a1800_regions[region]
