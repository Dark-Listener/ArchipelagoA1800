from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule, CollectionRule

from .data import A1800Requirement, A1800Rule, ALL_REGIONS, ANNO_DATA, player_has
from .Locations import get_event_location_data_list, get_unlock_location_data_list

if TYPE_CHECKING:
    from . import A1800World


def _has(player: int, rule: A1800Rule) -> CollectionRule:
    return lambda state, player=player, rule=rule: rule(state, player)


class _Rules:
    def __init__(self, world: "A1800World") -> None:
        self.world = world

    def create_rule(self, location_name: str, rule: A1800Rule) -> None:
        set_rule(self.world.multiworld.get_location(location_name,
                 self.world.player), _has(self.world.player, rule))


def set_rules(world: "A1800World") -> None:
    rules = _Rules(world)

    for data in get_unlock_location_data_list():
        assert data.population
        rules.create_rule(data.name, player_has(A1800Requirement(data.population, data.region)))

    for data in get_event_location_data_list():
        rule = next((rule for name, rule in ANNO_DATA.get_rules() if name == data.name), None)
        if rule:
            rules.create_rule(data.name, rule)

    world.multiworld.completion_condition[world.player] = _has(
        world.player, player_has(A1800Requirement("Victory", ALL_REGIONS)))
