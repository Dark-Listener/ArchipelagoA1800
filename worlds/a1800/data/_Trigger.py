from functools import reduce
from typing import Self

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, START_REGION, TriggerType


class Trigger:
    trigger_type: TriggerType

    region: Region
    triggers: list[Self]
    session: Session
    guid: int
    guids: set[int]
    population_name: str
    product_name: str
    product_region: Region
    unlock_name: str
    amount: int
    requirements: set[tuple[str, Region]]
    dlc: DLC

    ap_location_name: str

    def __init__(self, trigger_type: TriggerType) -> None:
        self.trigger_type = trigger_type

    def post_init(self) -> None:
        try:
            if not self.ap_location_name:
                self.ap_location_name: str = self._get_ap_location_name()
        except AttributeError:
            self.ap_location_name: str = self._get_ap_location_name()

    def _get_ap_location_name(self) -> str:
        match(self.trigger_type):
            case TriggerType.TRUE:
                out_name = "True"
            case TriggerType.FALSE:
                out_name = "False"
            case TriggerType.ALL:
                out_name = f"({self.triggers[0].get_ap_location_name()})"
                for trigger in self.triggers[1:]:
                    out_name += f" AND ({trigger.get_ap_location_name()})"
            case TriggerType.LINEAR:
                out_name = f"({self.triggers[0].get_ap_location_name()})"
                for trigger in self.triggers[1:]:
                    out_name += f" THEN ({trigger.get_ap_location_name()})"
            case TriggerType.ANY:
                out_name = f"({self.triggers[0].get_ap_location_name()})"
                for trigger in self.triggers[1:]:
                    out_name += f" OR ({trigger.get_ap_location_name()})"
            case TriggerType.SESSION_ENTER:
                out_name = f"Enter: {self.session.full_name}"
            case TriggerType.POPULATION:
                out_name = f"{self.amount} {self.population_name if self.amount != 1 else self.population_name[:-1]}"
            case TriggerType.POPULATION_HAPPINESS:
                out_name = f"{self.amount} happiness with {self.population_name}"
            case TriggerType.UNLOCK:
                out_name = f"Unlock: "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerType.COUNTER:
                out_name = f"Build {self.amount} "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerType.COUNTER_GOOD_IN_REGION:
                out_name = f"Have {self.amount} "\
                    f"{f'{self.product_region.name}: ' if self.product_region and self.product_region != ALL_REGIONS else ''}"\
                    f"{self.product_name[:-1] if self.product_name.endswith('s') and self.amount == 1 else self.product_name} "\
                    f"in {self.region.full_name}"
            case TriggerType.COUNTER_EXPEDITION_SOLVED:
                assert False, "Trigger type COUNTER_EXPEDITION_SOLVED should have set ap_location_name already"
            case TriggerType.QUEST_COMPLETE:
                assert False, "Trigger type QUEST_COMPLETE should have set ap_location_name already"
            case TriggerType.EVENT_ACTIVE:
                out_name = f"Have a "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}"\
                    f"{self.product_name[:-1] if self.product_name.endswith('s') else self.product_name} active"
            case TriggerType.ACTIVE_DLC:
                if self.dlc in DLC.__members__.values():
                    out_name = f"DLC active: {self.dlc.name}"
                else:
                    out_name = ""
                    for name in {dlc.name for dlc in DLC.__members__.values() if dlc in self.dlc and dlc.name}:
                        if out_name:
                            out_name += ", "
                        out_name += name
                    out_name = "DLCs active: " + out_name
        return out_name

    def get_ap_location_name(self, name: str = "") -> str:
        return f"{self.ap_location_name}{f' ({name})' if name else ''}"

    def get_sort_key(self) -> tuple[TriggerType | Session | int | DLC, ...]:
        match(self.trigger_type):
            case TriggerType.TRUE:
                return self.trigger_type,
            case TriggerType.FALSE:
                return self.trigger_type,
            case TriggerType.ALL:
                return self.trigger_type, *[key for sort_key in
                                            sorted([trigger.get_sort_key() for trigger in self.triggers])
                                            for key in sort_key]
            case TriggerType.LINEAR:
                return self.trigger_type, *[key for sort_key in [trigger.get_sort_key() for trigger in self.triggers]
                                            for key in sort_key]
            case TriggerType.ANY:
                return self.trigger_type, *[key for sort_key in
                                            sorted([trigger.get_sort_key() for trigger in self.triggers])
                                            for key in sort_key]
            case TriggerType.SESSION_ENTER:
                return self.trigger_type, self.session.value
            case TriggerType.POPULATION:
                return self.trigger_type, self.guid, self.amount
            case TriggerType.POPULATION_HAPPINESS:
                return self.trigger_type, self.guid, self.region.value, self.amount
            case TriggerType.UNLOCK:
                return self.trigger_type, self.guid
            case TriggerType.COUNTER:
                return self.trigger_type, self.guid, self.amount
            case TriggerType.COUNTER_GOOD_IN_REGION:
                return self.trigger_type, self.guid, self.region.value, self.amount
            case TriggerType.COUNTER_EXPEDITION_SOLVED:
                return self.trigger_type, self.guid, self.amount
            case TriggerType.QUEST_COMPLETE:
                return self.trigger_type, self.guid
            case TriggerType.EVENT_ACTIVE:
                return self.trigger_type, self.guid
            case TriggerType.ACTIVE_DLC:
                return self.trigger_type, self.dlc.value

    def add_rules_requirement(self, name: str, region: Region) -> Self:
        if not self.rules_requirements:
            self.rules_requirements: set[tuple[str, Region]] = {(name, region)}
        else:
            self.rules_requirements.add((name, region))
        return self

    @classmethod
    def TRUE(cls) -> Self:
        trigger = cls(TriggerType.TRUE)
        trigger.region = NO_REGION
        trigger.post_init()
        return trigger

    @classmethod
    def FALSE(cls) -> Self:
        trigger = cls(TriggerType.FALSE)
        trigger.region = NO_REGION
        trigger.post_init()
        return trigger

    @classmethod
    def ALL(cls, trigger_1: Self, trigger_2: Self, *triggers: Self, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.ALL)
        trigger.triggers = [trigger_1, trigger_2] + list(triggers)
        trigger.region = reduce(Region.__or__, [subtrigger.region for subtrigger in trigger.triggers])
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def LINEAR(cls, trigger_1: Self, trigger_2: Self, *triggers: Self, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.LINEAR)
        trigger.triggers = [trigger_1, trigger_2] + list(triggers)
        trigger.region = reduce(Region.__or__, [subtrigger.region for subtrigger in trigger.triggers])
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def ANY(cls, trigger_1: Self, trigger_2: Self, *triggers: Self, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.ANY)
        trigger.triggers = [trigger_1, trigger_2] + list(triggers)
        trigger.region = reduce(Region.__or__, [subtrigger.region for subtrigger in trigger.triggers])
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def SESSION_ENTER(cls, session: Session) -> Self:
        trigger = cls(TriggerType.SESSION_ENTER)
        trigger.session = session
        trigger.region = START_REGION
        trigger.post_init()
        return trigger

    @classmethod
    def POPULATION(cls, population_name: str, region: Region, amount: int, guid: int = 0) -> Self:
        trigger = cls(TriggerType.POPULATION)
        trigger.population_name = population_name
        trigger.region = region
        trigger.amount = amount
        trigger.guid = guid
        trigger.post_init()
        return trigger

    @classmethod
    def POPULATION_HAPPINESS(cls, population_name: str, session: Session, amount: int, unlock_name: str, guid: int = 0) -> Self:
        trigger = cls(TriggerType.POPULATION_HAPPINESS)
        trigger.population_name = population_name
        trigger.session = session
        trigger.region = session.region
        trigger.amount = amount
        trigger.unlock_name = unlock_name
        trigger.guid = guid
        trigger.post_init()
        return trigger

    @classmethod
    def UNLOCK(cls, unlock_name: str, region: Region, guid: int = 0) -> Self:
        trigger = cls(TriggerType.UNLOCK)
        trigger.unlock_name = unlock_name
        trigger.region = region
        trigger.guid = guid
        trigger.post_init()
        return trigger

    @classmethod
    def COUNTER(cls, unlock_name: str, product_name: str, region: Region, amount: int, guid: int = 0, *, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.COUNTER)
        trigger.unlock_name = unlock_name
        trigger.product_name = product_name
        trigger.region = region
        trigger.amount = amount
        trigger.guid = guid
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def COUNTER_GOOD_IN_REGION(
            cls, product_name: str, product_region: Region, amount: int, region: Region, guid: int = 0, *, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.COUNTER_GOOD_IN_REGION)
        trigger.product_name = product_name
        trigger.product_region = product_region
        trigger.amount = amount
        trigger.region = region
        trigger.guid = guid
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def COUNTER_EXPEDITION_SOLVED(cls, ap_location_name: str, amount: int, guid: int, requirements: set[tuple[str, Region]]) -> Self:
        trigger = cls(TriggerType.COUNTER_EXPEDITION_SOLVED)
        trigger.ap_location_name = ap_location_name
        trigger.amount = amount
        trigger.guid = guid
        trigger.requirements = requirements
        trigger.region = reduce(Region.__or__, [region for _, region in requirements])
        trigger.post_init()
        return trigger

    @classmethod
    def QUEST_COMPLETE(cls, ap_location_name: str, guid: int, requirements: set[tuple[str, Region]]) -> Self:
        trigger = cls(TriggerType.QUEST_COMPLETE)
        trigger.ap_location_name = ap_location_name
        trigger.guid = guid
        trigger.requirements = requirements
        trigger.region = reduce(Region.__or__, [region for _, region in requirements])
        trigger.post_init()
        return trigger

    @classmethod
    def EVENT_ACTIVE(
            cls, product_name: str, region: Region, guid: int = 0, *, ap_location_name: str = "") -> Self:
        trigger = cls(TriggerType.EVENT_ACTIVE)
        trigger.product_name = product_name
        trigger.region = region
        trigger.guid = guid
        trigger.ap_location_name = ap_location_name
        trigger.post_init()
        return trigger

    @classmethod
    def ACTIVE_DLC(cls, dlc: DLC) -> Self:
        trigger = cls(TriggerType.ACTIVE_DLC)
        trigger.dlc = dlc
        trigger.guids = {dlc.guid for dlc in DLC.__members__.values() if dlc != DLC.VANILLA and dlc in trigger.dlc}
        trigger.region = START_REGION
        trigger.post_init()
        return trigger
