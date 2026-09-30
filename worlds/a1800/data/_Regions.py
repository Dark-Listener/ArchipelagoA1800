from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from ._Enums import ALL_REGIONS, DLC, Region, START_REGION
from ._Requirement import A1800Requirement

if TYPE_CHECKING:
    from . import A1800Data


A1800_REGIONS: dict[Region, tuple[DLC, set[tuple[str, Region]], set[tuple[str, Region]]]] = {
    Region.OW: (DLC.VANILLA, set(), set()),
    Region.NW: (DLC.VANILLA, {
        ("Expedition: New World", ALL_REGIONS),
        ("Seafaring", ALL_REGIONS),
        ("Expeditions: Level 1", ALL_REGIONS),
    }, {
        ("Settling", Region.NW),
        ("Road Network", Region.NW),
        ("Small Warehouse", Region.NW),
    }),
    Region.AR: (DLC.THE_PASSAGE, {
        ("Expedition: The Arctic", ALL_REGIONS),
        ("Seafaring", ALL_REGIONS),
        ("Expeditions: Level 2", ALL_REGIONS),
    }, {
        ("Settling", Region.AR),
        ("Road Network", Region.AR),
        ("Small Warehouse", Region.AR),
    }),
    Region.EN: (DLC.LAND_OF_LIONS, {
        ("Expedition: Enbesa", ALL_REGIONS),
        ("Seafaring", ALL_REGIONS),
        ("Expeditions: Level 1", ALL_REGIONS),
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
    trading_post_guids: list[int] = field(default_factory=lambda: list())

    def post_init(self, A1800_DATA: "A1800Data") -> None:
        self.requirements = self.entry_requirements | self.build_requirements
        self.trading_post_guids = next(A1800_DATA.find_unlocks("Small Trading Post", self.region)).guids


class Regions:
    def __init__(self, A1800_DATA: "A1800Data") -> None:
        self._A1800_DATA = A1800_DATA

        global A1800_REGIONS

        self._a1800_regions = {
            region: A1800Region(
                region,
                dlc,
                {self._A1800_DATA.make_requirement(name, region)
                 for name, region in entry_requirements},
                {self._A1800_DATA.make_requirement(name, region) for name, region in build_requirements}
            ) for region, (dlc, entry_requirements, build_requirements) in A1800_REGIONS.items() if dlc in self._A1800_DATA.get_parsed_options().enabled_dlcs
        }
        for a1800_region in self._a1800_regions.values():
            a1800_region.post_init(self._A1800_DATA)

        # Assure START_REGION has no requirements
        assert not self._a1800_regions[START_REGION].requirements, \
            f"Start region {self._a1800_regions[START_REGION]} has non-empty requirements"

        # Assure all references exist
        for region in self._a1800_regions.values():
            for requirement in region.requirements:
                assert next(self._A1800_DATA.find_products(requirement.name, requirement.region), None) \
                    or next(self._A1800_DATA.find_unlocks(requirement.name, requirement.region), None), \
                    f"Region {region.region.full_name} references non-existent requirement {requirement}"

    def get_regions(self) -> Sequence[A1800Region]:
        return list(self._a1800_regions.values())

    def find_region(self, region: Region) -> Optional[A1800Region]:
        return self._a1800_regions[region] if region in self._a1800_regions else None
