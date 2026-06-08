from functools import reduce
from typing import Self

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, START_REGION, TriggerConditionType


class TriggerCondition:
    type_: TriggerConditionType

    region: Region
    conditions: list[Self]
    session: Session
    guid: int
    target_guid: int
    guids: set[int]
    population_name: str
    product_name: str
    product_region: Region
    unlock_name: str
    unlock_region: Region
    target_name: str
    amount: int
    distance: int
    requirements: set[tuple[str, Region]]
    dlc: DLC

    ap_location_name: str
    ap_location_name_generated: bool = False

    def __init__(self, type_: TriggerConditionType) -> None:
        self.type_ = type_

    def post_init(self) -> None:
        try:
            if not self.ap_location_name:
                self.ap_location_name = self._get_ap_location_name()
                self.ap_location_name_generated = True
        except AttributeError:
            self.ap_location_name = self._get_ap_location_name()
            self.ap_location_name_generated = True

    def _get_ap_location_name(self) -> str:
        match(self.type_):
            case TriggerConditionType.TRUE:
                out_name = "True"
            case TriggerConditionType.FALSE:
                out_name = "False"
            case TriggerConditionType.ALL:
                out_name = f"({self.conditions[0].get_ap_location_name()})"
                for trigger in self.conditions[1:]:
                    out_name += f" AND ({trigger.get_ap_location_name()})"
            case TriggerConditionType.LINEAR:
                out_name = f"({self.conditions[0].get_ap_location_name()})"
                for trigger in self.conditions[1:]:
                    out_name += f" THEN ({trigger.get_ap_location_name()})"
            case TriggerConditionType.ANY:
                out_name = f"({self.conditions[0].get_ap_location_name()})"
                for trigger in self.conditions[1:]:
                    out_name += f" OR ({trigger.get_ap_location_name()})"
            case TriggerConditionType.SESSION_ENTER:
                out_name = f"Enter: {self.session.full_name}"
            case TriggerConditionType.POPULATION:
                out_name = f"{self.amount} {self.population_name if self.amount != 1 else self.population_name[:-1]}"
            case TriggerConditionType.POPULATION_HAPPINESS:
                out_name = f"{self.amount} happiness with {self.population_name}"
            case TriggerConditionType.UNLOCK:
                out_name = f"Unlock: "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerConditionType.COUNTER:
                out_name = f"Build {self.amount} "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerConditionType.COUNTER_GOOD_IN_REGION:
                region_prefix = f"{self.product_region.name}: " if self.product_region and self.product_region != ALL_REGIONS else ""
                out_name = f"Have {self.amount} {'tons' if self.amount > 1 else 'ton'} of "\
                    f"{region_prefix}{self.product_name} in {self.region.full_name} trading posts"
            case TriggerConditionType.COUNTER_EXPEDITION_SOLVED:
                assert False, "Trigger type COUNTER_EXPEDITION_SOLVED should have set ap_location_name already"
            case TriggerConditionType.QUEST_COMPLETE:
                assert False, "Trigger type QUEST_COMPLETE should have set ap_location_name already"
            case TriggerConditionType.EVENT_ACTIVE:
                region_prefix = f"{self.region.name}: " if self.region and self.region != ALL_REGIONS else ""
                out_name = f"Have a "\
                    f"{region_prefix}{self.product_name[:-1] if self.product_name.endswith('s') else self.product_name} active"
            case TriggerConditionType.OBJECT_POSITION:
                region_prefix = f"{self.region.name}: " if self.region and self.region != ALL_REGIONS else ""
                out_name = f"Build a {region_prefix}{self.target_name} within {self.distance} squares of a {region_prefix}{self.unlock_name}"
            case TriggerConditionType.ACTIVE_DLC:
                if self.dlc in DLC.__members__.values():
                    out_name = f"DLC active: {self.dlc.name}"
                else:
                    out_name = ""
                    for name in {dlc.name for dlc in DLC.__members__.values() if dlc in self.dlc and dlc.name}:
                        if out_name:
                            out_name += ", "
                        out_name += name
                    out_name = "DLCs active: " + out_name
            case TriggerConditionType.FACTORY_PRODUCTIVITY:
                out_name = f"Reach {self.amount}% productivity in a "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerConditionType.ITEM_SET_ACTIVE:
                assert False, "Trigger type ITEM_SET_ACTIVE should have set ap_location_name already"
        return out_name

    def get_ap_location_name(self, name: str = "") -> str:
        return f"{self.ap_location_name}{f' ({name})' if name else ''}"

    def get_sort_key(self) -> tuple[TriggerConditionType | Session | int | DLC, ...]:
        match(self.type_):
            case TriggerConditionType.TRUE:
                return self.type_,
            case TriggerConditionType.FALSE:
                return self.type_,
            case TriggerConditionType.ALL:
                return self.type_, *[key for sort_key in
                                     sorted([trigger.get_sort_key() for trigger in self.conditions])
                                     for key in sort_key]
            case TriggerConditionType.LINEAR:
                return self.type_, *[key for sort_key in [trigger.get_sort_key() for trigger in self.conditions]
                                     for key in sort_key]
            case TriggerConditionType.ANY:
                return self.type_, *[key for sort_key in
                                     sorted([trigger.get_sort_key() for trigger in self.conditions])
                                     for key in sort_key]
            case TriggerConditionType.SESSION_ENTER:
                return self.type_, self.session.value
            case TriggerConditionType.POPULATION:
                return self.type_, self.guid, self.amount
            case TriggerConditionType.POPULATION_HAPPINESS:
                return self.type_, self.guid, self.region.value, self.amount
            case TriggerConditionType.UNLOCK:
                return self.type_, self.guid
            case TriggerConditionType.COUNTER:
                return self.type_, self.guid, self.amount
            case TriggerConditionType.COUNTER_GOOD_IN_REGION:
                return self.type_, self.guid, self.region.value, self.amount
            case TriggerConditionType.COUNTER_EXPEDITION_SOLVED:
                return self.type_, self.guid, self.amount
            case TriggerConditionType.QUEST_COMPLETE:
                return self.type_, self.guid
            case TriggerConditionType.EVENT_ACTIVE:
                return self.type_, self.guid
            case TriggerConditionType.OBJECT_POSITION:
                return self.type_, self.guid, self.target_guid, self.distance
            case TriggerConditionType.ITEM_SET_ACTIVE:
                return self.type_, self.guid, self.unlock_region.value
            case TriggerConditionType.FACTORY_PRODUCTIVITY:
                return self.type_, self.guid, self.amount
            case TriggerConditionType.ACTIVE_DLC:
                return self.type_, self.dlc.value

    def add_rules_requirement(self, name: str, region: Region) -> Self:
        if not self.rules_requirements:
            self.rules_requirements: set[tuple[str, Region]] = {(name, region)}
        else:
            self.rules_requirements.add((name, region))
        return self

    @classmethod
    def TRUE(cls, *, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.TRUE)
        condition.region = NO_REGION
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def FALSE(cls, *, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.FALSE)
        condition.region = NO_REGION
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def ALL(cls, condition_1: Self, condition_2: Self, *conditions: Self, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.ALL)
        condition.conditions = [condition_1, condition_2] + list(conditions)
        condition.region = reduce(
            Region.__or__, [subcondition.region for subcondition in condition.conditions], NO_REGION)
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def LINEAR(cls, condition_1: Self, condition_2: Self, *conditions: Self, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.LINEAR)
        condition.conditions = [condition_1, condition_2] + list(conditions)
        condition.region = reduce(
            Region.__or__, [subcondition.region for subcondition in condition.conditions], NO_REGION)
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def ANY(cls, condition_1: Self, condition_2: Self, *conditions: Self, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.ANY)
        condition.conditions = [condition_1, condition_2] + list(conditions)
        condition.region = reduce(
            Region.__or__, [subcondition.region for subcondition in condition.conditions], NO_REGION)
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def SESSION_ENTER(cls, session: Session) -> Self:
        condition = cls(TriggerConditionType.SESSION_ENTER)
        condition.session = session
        condition.region = START_REGION
        condition.post_init()
        return condition

    @classmethod
    def POPULATION(cls, population_name: str, region: Region, amount: int, *, guid: int = 0) -> Self:
        condition = cls(TriggerConditionType.POPULATION)
        condition.population_name = population_name
        condition.region = region
        condition.amount = amount
        condition.guid = guid
        condition.post_init()
        return condition

    @classmethod
    def POPULATION_HAPPINESS(cls, population_name: str, session: Session, amount: int, unlock_name: str, *, guid: int = 0) -> Self:
        condition = cls(TriggerConditionType.POPULATION_HAPPINESS)
        condition.population_name = population_name
        condition.session = session
        condition.region = session.region
        condition.amount = amount
        condition.unlock_name = unlock_name
        condition.guid = guid
        condition.post_init()
        return condition

    @classmethod
    def UNLOCK(cls, unlock_name: str, region: Region, *, guid: int = 0) -> Self:
        condition = cls(TriggerConditionType.UNLOCK)
        condition.unlock_name = unlock_name
        condition.region = region
        condition.guid = guid
        condition.post_init()
        return condition

    @classmethod
    def COUNTER(cls, unlock_name: str, region: Region, amount: int, *, guid: int = 0, ap_location_name: str = "", requirements: set[tuple[str, Region]] = set()) -> Self:
        condition = cls(TriggerConditionType.COUNTER)
        condition.unlock_name = unlock_name
        condition.region = region
        condition.amount = amount
        condition.guid = guid
        condition.ap_location_name = ap_location_name
        condition.requirements = requirements
        condition.post_init()
        return condition

    @classmethod
    def COUNTER_GOOD_IN_REGION(cls, product_name: str, product_region: Region, amount: int, region: Region, *, guid: int = 0, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.COUNTER_GOOD_IN_REGION)
        condition.product_name = product_name
        condition.product_region = product_region
        condition.amount = amount
        condition.region = region
        condition.guid = guid
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def COUNTER_EXPEDITION_SOLVED(cls, ap_location_name: str, amount: int, guid: int, requirements: set[tuple[str, Region]]) -> Self:
        condition = cls(TriggerConditionType.COUNTER_EXPEDITION_SOLVED)
        condition.ap_location_name = ap_location_name
        condition.amount = amount
        condition.guid = guid
        condition.requirements = requirements
        condition.region = reduce(Region.__or__, [region for _, region in requirements], NO_REGION)
        condition.post_init()
        return condition

    @classmethod
    def QUEST_COMPLETE(cls, ap_location_name: str, guid: int, requirements: set[tuple[str, Region]]) -> Self:
        condition = cls(TriggerConditionType.QUEST_COMPLETE)
        condition.ap_location_name = ap_location_name
        condition.guid = guid
        condition.requirements = requirements
        condition.region = reduce(Region.__or__, [region for _, region in requirements], NO_REGION)
        condition.post_init()
        return condition

    @classmethod
    def EVENT_ACTIVE(cls, product_name: str, region: Region, *, guid: int = 0, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.EVENT_ACTIVE)
        condition.product_name = product_name
        condition.region = region
        condition.guid = guid
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def OBJECT_POSITION(cls, unlock_name: str, region: Region, distance: int, target_name: str, *, guid: int = 0, target_guid: int = 0, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.OBJECT_POSITION)
        condition.unlock_name = unlock_name
        condition.region = region
        condition.distance = distance
        condition.target_name = target_name
        condition.guid = guid
        condition.target_guid = target_guid
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def ITEM_SET_ACTIVE(cls, unlock_name: str, unlock_region: Region, ap_location_name: str, guid: int, requirements: set[tuple[str, Region]]) -> Self:
        condition = cls(TriggerConditionType.ITEM_SET_ACTIVE)
        condition.unlock_name = unlock_name
        condition.unlock_region = unlock_region
        condition.ap_location_name = ap_location_name
        condition.guid = guid
        condition.requirements = requirements
        condition.region = unlock_region | reduce(Region.__or__, [region for _, region in requirements], NO_REGION)
        condition.post_init()
        return condition

    @classmethod
    def FACTORY_PRODUCTIVITY(cls, unlock_name: str, region: Region, amount: int, *, guid: int = 0, ap_location_name: str = "") -> Self:
        condition = cls(TriggerConditionType.FACTORY_PRODUCTIVITY)
        condition.unlock_name = unlock_name
        condition.region = region
        condition.amount = amount
        condition.guid = guid
        condition.ap_location_name = ap_location_name
        condition.post_init()
        return condition

    @classmethod
    def ACTIVE_DLC(cls, dlc: DLC) -> Self:
        condition = cls(TriggerConditionType.ACTIVE_DLC)
        condition.dlc = dlc
        condition.guids = {dlc.guid for dlc in DLC.__members__.values() if dlc != DLC.VANILLA and dlc in condition.dlc}
        condition.region = START_REGION
        condition.post_init()
        return condition
