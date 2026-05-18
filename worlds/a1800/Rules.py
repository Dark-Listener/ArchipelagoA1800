from typing import TYPE_CHECKING

from rule_builder.rules import HasAll

from .data import A1800Requirement, ALL_REGIONS, ANNO_DATA
from .Locations import LOCATIONS

if TYPE_CHECKING:
    from . import A1800World


def _create_rule(world: "A1800World", location_name: str, *requirements: A1800Requirement) -> None:
    world.set_rule(world.multiworld.get_location(location_name, world.player), HasAll(
        *set([ap_item_name for requirement in requirements for ap_item_name in requirement.ap_item_names])))


def set_rules(world: "A1800World") -> None:
    for region in ANNO_DATA.get_regions():
        if region.region.full_name != world.origin_region_name:
            world.create_entrance(
                world.get_region(world.origin_region_name),
                world.get_region(region.region.full_name),
                HasAll(*set([ap_item_name for requirement in region.requirements
                             for ap_item_name in requirement.ap_item_names]))
            )

    for data in LOCATIONS.get_unlock_location_data_list():
        assert data.population, f"Location data {data} has no population set"
        _create_rule(world, data.name, A1800Requirement(data.population, data.region))

    for data in LOCATIONS.get_event_location_data_list():
        requirements = next(
            (requirement for name, requirement in ANNO_DATA.get_location_requirements() if name == data.name), None)
        if requirements:
            _create_rule(world, data.name, *requirements)

    world.set_completion_rule(HasAll(*A1800Requirement("Victory", ALL_REGIONS).ap_item_names))
