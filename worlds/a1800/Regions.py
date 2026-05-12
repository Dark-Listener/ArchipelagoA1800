from typing import TYPE_CHECKING

from BaseClasses import Region

from .AnnoData import a1800_regions, A1800Region, get_region_name
from .Locations import A1800Location

if TYPE_CHECKING:
    from . import A1800World


def create_regions(world: "A1800World") -> None:
    for region in a1800_regions:
        _create_region(world, region)


def _create_region(world: "A1800World", a1800_region: A1800Region) -> Region:
    from .Locations import location_data_list

    region = Region(get_region_name(a1800_region), world.player, world.multiworld)

    for data in location_data_list:
        if data.region == a1800_region.name:
            location = A1800Location(world.player, data, region)
            region.locations.append(location)

    world.multiworld.regions.append(region)
    return region
