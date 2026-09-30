from typing import Iterable, Optional, TYPE_CHECKING

from rule_builder.rules import And, False_, HasAll, HasAllCounts, Or, Rule, True_

from .data import A1800Requirement, ALL_REGIONS, RequirementType, TriggerCondition, TriggerConditionType

if TYPE_CHECKING:
    from . import A1800World


def _create_rule(world: "A1800World", data: Iterable[A1800Requirement] | TriggerCondition) -> Optional[Rule["A1800World"]]:
    if isinstance(data, TriggerCondition):
        condition = data
        match(condition.type_):
            case TriggerConditionType.TRUE:
                return True_()
            case TriggerConditionType.FALSE:
                return False_()
            case TriggerConditionType.ALL:
                return And(*[rule for subcondition in condition.conditions for rule in [_create_rule(world, subcondition)] if rule is not None])
            case TriggerConditionType.LINEAR:
                return And(*[rule for subcondition in condition.conditions for rule in [_create_rule(world, subcondition)] if rule is not None])
            case TriggerConditionType.ANY:
                return Or(*[rule for subcondition in condition.conditions for rule in [_create_rule(world, subcondition)] if rule is not None])
            case TriggerConditionType.SESSION_ENTER:
                return _create_rule(world, world.A1800_DATA.find_session(condition.session).requirements)
            case TriggerConditionType.POPULATION:
                return _create_rule(world, {world.A1800_DATA.make_requirement(condition.population_name, condition.region)})
            case TriggerConditionType.POPULATION_HAPPINESS:
                populations = list(world.A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                assert len(populations) == 1, \
                    f"Condition {condition.type_.name} {condition.amount} {condition.product_name} has 0 or multiple "\
                    "population residences"
                population = populations[0]
                return _create_rule(world, {world.A1800_DATA.make_requirement(condition.population_name, condition.region)} | {world.A1800_DATA.make_requirement(name, population.region) for name in population.luxury})
            case TriggerConditionType.COUNTER:
                unlock = next(world.A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                region = world.A1800_DATA.find_region(condition.region)
                region_requirements: set[A1800Requirement] = region.requirements if region else set()
                return _create_rule(world, world.A1800_DATA.get_requirements_for_construction(unlock) | region_requirements | {world.A1800_DATA.make_requirement(name, region) for name, region in condition.requirements})
            case TriggerConditionType.COUNTER_GOOD_IN_REGION:
                a1800_region = world.A1800_DATA.find_region(condition.region)
                assert a1800_region, \
                    f"Condition {condition.type_.name} {condition.amount} {condition.product_name} in {condition.region.name} "\
                    f"has 0 or multiple regions"
                return _create_rule(world,
                                    {world.A1800_DATA.make_requirement(condition.product_name, condition.product_region)} | a1800_region.requirements)
            case TriggerConditionType.COUNTER_GOOD_IN_STOCK:
                assert False, "TriggerConditionType COUNTER_GOOD_IN_STOCK should never be used for rules"
            case TriggerConditionType.COUNTER_EXPEDITION_SOLVED:
                return _create_rule(world, {world.A1800_DATA.make_requirement(name, region) for name, region in condition.requirements})
            case TriggerConditionType.UNLOCK:
                return _create_rule(world, {world.A1800_DATA.make_requirement(condition.unlock_name, condition.region, type=RequirementType.UNLOCK)})
            case TriggerConditionType.QUEST_COMPLETE:
                return _create_rule(world, {world.A1800_DATA.make_requirement(name, region) for name, region in condition.requirements})
            case TriggerConditionType.EVENT_ACTIVE:
                return _create_rule(world, {world.A1800_DATA.make_requirement(condition.product_name, condition.region)})
            case TriggerConditionType.OBJECT_POSITION:
                unlock = next(world.A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                target = next(world.A1800_DATA.find_unlocks(condition.target_name, condition.region))
                return _create_rule(world,
                                    world.A1800_DATA.get_requirements_for_construction(
                                        unlock) | world.A1800_DATA.get_requirements_for_construction(target)
                                    )
            case TriggerConditionType.ITEM_SET_ACTIVE:
                unlock = next(world.A1800_DATA.find_unlocks(condition.unlock_name, condition.unlock_region))
                return _create_rule(world, {world.A1800_DATA.make_requirement(unlock.name, unlock.region)} | {world.A1800_DATA.make_requirement(name, unlock.region) for name in unlock.cost} | {world.A1800_DATA.make_requirement(name, region) for name, region in condition.requirements})
            case TriggerConditionType.FACTORY_PRODUCTIVITY:
                unlock = next(world.A1800_DATA.find_unlocks(condition.unlock_name, condition.region))
                return _create_rule(world, {world.A1800_DATA.make_requirement(unlock.name, unlock.region)} | {world.A1800_DATA.make_requirement(name, unlock.region) for name in unlock.cost | unlock.maintenance | {name for name, _ in unlock.input}})
            case TriggerConditionType.ACTIVE_DLC:
                assert False, "TriggerConditionType ACTIVE_DLC should never be used for rules"
    else:
        if data:
            if world.A1800_DATA.get_parsed_options().enable_progressive_unlocks:
                required_counts: dict[str, int] = {}
                for requirement in data:
                    for ap_item_name in (requirement.ap_item_names if not requirement.progressive_ap_item_name else [requirement.progressive_ap_item_name]):
                        if not ap_item_name in required_counts or required_counts[ap_item_name] < requirement.amount:
                            required_counts[ap_item_name] = requirement.amount
                return HasAllCounts(required_counts)
            else:
                return HasAll(*set([ap_item_name for requirement in data for ap_item_name in requirement.ap_item_names]))
        else:
            return None


def _create_and_set_rule(world: "A1800World", location_name: str, data: Iterable[A1800Requirement] | TriggerCondition) -> None:
    rule = _create_rule(world, data)
    if rule is not None:
        world.set_rule(world.multiworld.get_location(location_name, world.player), rule)


def set_rules(world: "A1800World") -> None:
    for region in world.A1800_DATA.get_regions():
        if region.region.full_name != world.origin_region_name:
            if world.A1800_DATA.get_parsed_options().enable_progressive_unlocks:
                required_counts: dict[str, int] = {}
                for requirement in region.requirements:
                    for ap_item_name in (requirement.ap_item_names if not requirement.progressive_ap_item_name else [requirement.progressive_ap_item_name]):
                        if not ap_item_name in required_counts or required_counts[ap_item_name] < requirement.amount:
                            required_counts[ap_item_name] = requirement.amount
                rule = HasAllCounts(required_counts)
            else:
                rule = HasAll(*set([ap_item_name for requirement in region.requirements
                                    for ap_item_name in requirement.ap_item_names]))
            world.set_rule(world.get_entrance(f"{world.origin_region_name} => {region.region.full_name}"), rule)

    for data in world.LOCATIONS.get_unlock_location_data_list():
        assert data.condition, "Unlock location has no condition"
        _create_and_set_rule(world, data.name, data.condition)

    location_requirements = world.A1800_DATA.get_location_requirements()
    for data in world.LOCATIONS.get_event_location_data_list():
        if data.name in location_requirements:
            _create_and_set_rule(world, data.name, location_requirements[data.name])

    world.set_completion_rule(HasAll(*world.A1800_DATA.make_requirement("Victory", ALL_REGIONS).ap_item_names))
