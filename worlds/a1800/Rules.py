from typing import Iterable, Optional, TYPE_CHECKING, cast

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
            case TriggerType.LINEAR:
                return And(*[rule for trigger in data.triggers for rule in [_create_rule(trigger)] if rule is not None])
            case TriggerType.ANY:
                return Or(*[rule for trigger in data.triggers for rule in [_create_rule(trigger)] if rule is not None])
            case TriggerType.SESSION_ENTER:
                return _create_rule(A1800_DATA.find_session(data.session).requirements)
            case TriggerType.POPULATION:
                return _create_rule({A1800Requirement(data.population_name, data.region)})
            case TriggerType.POPULATION_HAPPINESS:
                populations = list(A1800_DATA.find_unlocks(data.unlock_name, data.region))
                assert len(populations) == 1, \
                    f"Trigger {data.trigger_type.name} {data.amount} {data.product_name} has 0 or multiple "\
                    "population residences"
                population = populations[0]
                return _create_rule({A1800Requirement(data.population_name, data.region)} | {A1800Requirement(name, population.region) for name in population.luxury})
            case TriggerType.COUNTER:
                unlock = next(A1800_DATA.find_unlocks(data.unlock_name, data.region))
                return _create_rule({A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost})
            case TriggerType.COUNTER_GOOD_IN_REGION:
                a1800_region = A1800_DATA.find_region(data.region)
                assert a1800_region, \
                    f"Trigger {data.trigger_type.name} {data.amount} {data.product_name} in {data.region.name} "\
                    f"has 0 or multiple regions"
                return _create_rule(
                    {A1800Requirement(data.product_name, data.product_region)} | a1800_region.requirements)
            case TriggerType.COUNTER_EXPEDITION_SOLVED:
                return _create_rule({A1800Requirement(name, region) for name, region in data.requirements})
            case TriggerType.UNLOCK:
                return _create_rule({A1800Requirement(data.unlock_name, data.region, type=RequirementType.UNLOCK)})
            case TriggerType.QUEST_COMPLETE:
                return _create_rule({A1800Requirement(name, region) for name, region in data.requirements})
            case TriggerType.EVENT_ACTIVE:
                return _create_rule({A1800Requirement(data.product_name, data.region)})
            case TriggerType.OBJECT_POSITION:
                unlock = next(A1800_DATA.find_unlocks(data.unlock_name, data.region))
                target = next(A1800_DATA.find_unlocks(data.target_name, data.region))
                return _create_rule(
                    {A1800Requirement(unlock.name, unlock.region), A1800Requirement(target.name, unlock.region)}
                    | {A1800Requirement(name, unlock.region) for name in unlock.cost | target.cost}
                )
            case TriggerType.ITEM_SET_ACTIVE:
                unlock = next(A1800_DATA.find_unlocks(data.unlock_name, data.unlock_region))
                return _create_rule({A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost} | {A1800Requirement(name, region) for name, region in data.requirements})
            case TriggerType.FACTORY_PRODUCTIVITY:
                unlock = next(A1800_DATA.find_unlocks(data.unlock_name, data.region))
                return _create_rule({A1800Requirement(unlock.name, unlock.region)} | {A1800Requirement(name, unlock.region) for name in unlock.cost | unlock.maintenance | cast(set[str], next(zip(*unlock.input)))})
            case TriggerType.ACTIVE_DLC:
                assert False, "TriggerType ACTIVE_DLC should never be used for rules"
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
