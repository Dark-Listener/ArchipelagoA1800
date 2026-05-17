from collections.abc import Sequence
from dataclasses import dataclass
from enum import auto, Flag, KEEP

from ._Dlc import DLC


class Region(Flag, boundary=KEEP):
    OW = auto()
    NW = auto()
    EN = auto()
    AR = auto()

    @property
    def full_name(self) -> str:
        global _REGION_NAMES

        out_name = ""
        for region, full_name in _REGION_NAMES.items():
            if region in self:
                if out_name:
                    out_name += "|"
                out_name += full_name
        return out_name


_REGION_NAMES = {
    Region.OW: "Old World",
    Region.NW: "New World",
    Region.EN: "Enbesa",
    Region.AR: "Arctic",
}

NO_REGION = Region(0)

ALL_REGIONS = Region.OW | Region.NW | Region.EN | Region.AR


@dataclass
class A1800Region:
    region: Region
    dlc: DLC
    requirements: set[str]


_a1800_regions: list[A1800Region] = [
    A1800Region(Region.OW, DLC.VANILLA, set()),
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
