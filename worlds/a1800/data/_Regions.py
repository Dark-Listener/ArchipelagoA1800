from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Optional

from ._Enums import ALL_REGIONS, DLC, Region, START_REGION
from ._ParsedOptions import ParsedOptions
from ._Products import PRODUCTS
from ._Requirement import A1800Requirement
from ._Unlocks import UNLOCKS


_a1800_regions: dict[Region, tuple[DLC, set[tuple[str, Region]], set[tuple[str, Region]]]] = {
    Region.OW: (DLC.VANILLA, set(), set()),
    Region.NW: (DLC.VANILLA, {
        ("Expedition: New World", ALL_REGIONS),
        ("Sea Travel", ALL_REGIONS),
    }, {
        ("Settling", Region.NW),
        ("Road Network", Region.NW),
        ("Small Warehouse", Region.NW),
    }),
    Region.AR: (DLC.THE_PASSAGE, {
        ("Expedition: The Arctic", ALL_REGIONS),
        ("Sea Travel", ALL_REGIONS),
        ("Artisans", Region.OW),
    }, {
        ("Settling", Region.AR),
        ("Road Network", Region.AR),
        ("Small Warehouse", Region.AR),
    }),
    Region.EN: (DLC.LAND_OF_LIONS, {
        ("Expedition: Enbesa", ALL_REGIONS),
        ("Sea Travel", ALL_REGIONS),
    }, {
        ("Initial Settling", Region.EN),
        ("Road Network", Region.EN),
        ("Small Warehouse", Region.EN),
        ("Wanza Woodcutter", Region.EN),
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

    def init(self, parsed_options: ParsedOptions) -> None:
        global _a1800_regions

        self._a1800_regions = {
            region: A1800Region(
                region,
                dlc,
                {A1800Requirement(name, region) for name, region in entry_requirements},
                {A1800Requirement(name, region) for name, region in build_requirements}
            ) for region, (dlc, entry_requirements, build_requirements) in _a1800_regions.items() if dlc in parsed_options.enabled_dlcs
        }

        self._initialized = True

        # Assure START_REGION has no requirements
        assert not self._a1800_regions[START_REGION].requirements, \
            f"Start region {self._a1800_regions[START_REGION]} has non-empty requirements"

        # Assure all references exist
        for region in self._a1800_regions.values():
            for requirement in region.requirements:
                assert next(PRODUCTS.find_products(requirement.name, requirement.region), None) \
                    or next(UNLOCKS.find_unlocks(requirement.name, requirement.region), None), \
                    f"Region {region.region.full_name} references non-existent requirement {requirement}"

    def get_regions(self) -> Sequence[A1800Region]:
        assert self._initialized, "The Anno 1800 regions module was used before it was initialized."
        return list(self._a1800_regions.values())

    def find_region(self, region: Region) -> Optional[A1800Region]:
        assert self._initialized, "The Anno 1800 regions module was used before it was initialized."
        return self._a1800_regions[region] if region in self._a1800_regions else None


REGIONS = _Regions()
