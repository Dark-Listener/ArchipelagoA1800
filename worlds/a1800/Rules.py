from typing import Iterable, Optional, TYPE_CHECKING

from rule_builder.rules import And, False_, HasAll, Or, Rule, True_

from .data import A1800Requirement, ALL_REGIONS, A1800_DATA, RequirementType, Trigger, TriggerType
from .Locations import LOCATIONS

if TYPE_CHECKING:
    from . import A1800World


def _create_rule(data: Iterable[A1800Requirement] | Trigger) -> Optional[Rule["A1800World"]]:
    if isinstance(data, Trigger):
        match(data.trigger_type):
            case TriggerType.TRUE:
                return True_()
            case TriggerType.FALSE:
                return False_()
            case TriggerType.ALL:
                return And(*[rule for trigger in data.triggers for rule in [_create_rule(trigger)] if rule is not None])
            case TriggerType.ANY:
                return Or(*[rule for trigger in data.triggers for rule in [_create_rule(trigger)] if rule is not None])
            case TriggerType.SESSION_ENTER:
                return _create_rule(A1800_DATA.find_session(data.session).requirements)
            case TriggerType.POPULATION:
                return _create_rule({A1800Requirement(data.population, data.region)})
            case TriggerType.COUNTER:
                return _create_rule({A1800Requirement(data.product_name, data.region)})
            case TriggerType.UNLOCK:
                return _create_rule({A1800Requirement(data.unlock_name, data.region, type=RequirementType.UNLOCK)})
            case TriggerType.DLC:
                assert False, "TriggerType DLC should never be used for rules"
    else:
        if data:
            return HasAll(*set([ap_item_name for requirement in data for ap_item_name in requirement.ap_item_names]))
        else:
            return None


def _create_and_set_rule(world: "A1800World", location_name: str, data: Iterable[A1800Requirement] | Trigger) -> None:
    rule = _create_rule(data)
    if rule is not None:
        world.set_rule(world.multiworld.get_location(location_name, world.player), rule)


def set_rules(world: "A1800World") -> None:
    for region in A1800_DATA.get_regions():
        if region.region.full_name != world.origin_region_name:
            world.set_rule(
                world.get_entrance(f"{world.origin_region_name} => {region.region.full_name}"),
                HasAll(*set([ap_item_name for requirement in region.requirements
                             for ap_item_name in requirement.ap_item_names]))
            )

    for data in LOCATIONS.get_unlock_location_data_list():
        assert data.trigger, "Unlock location has no trigger"
        _create_and_set_rule(world, data.name, data.trigger)

    location_requirements = A1800_DATA.get_location_requirements()
    for data in LOCATIONS.get_event_location_data_list():
        if data.name in location_requirements:
            _create_and_set_rule(world, data.name, location_requirements[data.name])

    world.set_completion_rule(HasAll(*A1800Requirement("Victory", ALL_REGIONS).ap_item_names))
