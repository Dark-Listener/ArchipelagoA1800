from typing import TYPE_CHECKING

from rule_builder.rules import HasAll

from .data import A1800Requirement, ALL_REGIONS, ANNO_DATA
from .Locations import get_event_location_data_list, get_unlock_location_data_list

if TYPE_CHECKING:
    from . import A1800World


class _Rules:
    def __init__(self, world: "A1800World") -> None:
        self.world = world

    def create_rule(self, location_name: str, requirements: list[str]) -> None:
        self.world.set_rule(self.world.multiworld.get_location(
            location_name, self.world.player), HasAll(*requirements))


def set_rules(world: "A1800World") -> None:
    rules = _Rules(world)

    for data in get_unlock_location_data_list():
        assert data.population
        rules.create_rule(data.name, list(A1800Requirement(data.population, data.region).ap_item_names))

    for data in get_event_location_data_list():
        rule = next((rule for name, rule in ANNO_DATA.get_rules() if name == data.name), None)
        if rule:
            rules.create_rule(data.name, rule)

    world.set_completion_rule(HasAll(*A1800Requirement("Victory", ALL_REGIONS).ap_item_names))
