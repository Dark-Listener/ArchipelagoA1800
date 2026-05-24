from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Optional

from ._Enums import ALL_REGIONS, DLC, Region, START_REGION
from ._Requirement import A1800Requirement


_a1800_regions: dict[Region, tuple[DLC, set[tuple[str, Region]], set[tuple[str, Region]]]] = {
    Region.OW: (DLC.VANILLA, set(), set()),
    Region.NW: (DLC.VANILLA, {
        ("Artisans", Region.OW),
        ("Sea Travel", ALL_REGIONS),
    }, {
        ("Settling", Region.NW),
        ("Dirt Road", Region.NW),
        ("Small Warehouse", Region.NW),
    }),
}


@dataclass
class A1800Region:
    region: Region
    dlc: DLC
    entry_requirements: set[A1800Requirement] = field(default_factory=lambda: set())
    build_requirements: set[A1800Requirement] = field(default_factory=lambda: set())
    requirements: set[A1800Requirement] = field(default_factory=lambda: set())

    def __post_init__(self) -> None:
        self.requirements = self.entry_requirements | self.build_requirements


class _Regions:
    _initialized: bool = False

    def init(self, enabled_dlcs: DLC) -> None:
        global _a1800_regions

        self._a1800_regions = {
            region: A1800Region(
                region,
                dlc,
                {A1800Requirement(name, region) for name, region in entry_requirements},
                {A1800Requirement(name, region) for name, region in build_requirements}
            ) for region, (dlc, entry_requirements, build_requirements) in _a1800_regions.items() if dlc in enabled_dlcs
        }

        self._initialized = True

        # Assure START_REGION has no requirements
        assert not self._a1800_regions[START_REGION].requirements, \
            f"Start region {self._a1800_regions[START_REGION]} has non-empty requirements"

    def get_regions(self) -> Sequence[A1800Region]:
        assert self._initialized, "The Anno 1800 regions module was used before it was initialized."
        return list(self._a1800_regions.values())

    def find_region(self, region: Region) -> Optional[A1800Region]:
        assert self._initialized, "The Anno 1800 regions module was used before it was initialized."
        return self._a1800_regions[region] if region in self._a1800_regions else None


REGIONS = _Regions()
