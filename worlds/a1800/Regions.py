from typing import TYPE_CHECKING

from BaseClasses import Region

from .data import A1800Region, ANNO_DATA
from .Locations import A1800Location, LOCATIONS

if TYPE_CHECKING:
    from . import A1800World


def create_regions(world: "A1800World") -> None:
    for region in ANNO_DATA.get_regions():
        _create_region(world, region)


def _create_region(world: "A1800World", a1800_region: A1800Region) -> Region:
    region = Region(a1800_region.region.full_name, world.player, world.multiworld)

    for data in LOCATIONS.get_location_data_list():
        if data.region == a1800_region.region:
            location = A1800Location(world.player, data, region)
            region.locations.append(location)

    world.multiworld.regions.append(region)
    return region
