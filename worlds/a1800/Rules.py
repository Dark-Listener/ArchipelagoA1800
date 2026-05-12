from typing import TYPE_CHECKING

from worlds.generic.Rules import set_rule, CollectionRule

from .AnnoData import A1800Rule, player_has
from .Locations import unlock_location_data_list

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
    from .AnnoData import a1800_rules
    from .Locations import event_location_data_list

    rules = _Rules(world)

    for data in unlock_location_data_list:
        assert data.population
        rules.create_rule(data.name, player_has((data.population, frozenset({data.region}))))

    for data in event_location_data_list:
        print(f"Create event rule {data.name}")
        rule = next((rule for name, rule in a1800_rules if name == data.name), None)
        if rule:
            rules.create_rule(data.name, rule)

    world.multiworld.completion_condition[world.player] = _has(
        world.player, player_has(("Victory", frozenset({"OW", "NW", "En", "Ar"}))))
