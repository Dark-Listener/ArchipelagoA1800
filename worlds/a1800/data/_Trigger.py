from functools import reduce
from typing import Any, Callable, Self

from ._Enums import ALL_REGIONS, DLC, NO_REGION, Region, Session, START_REGION, TriggerType
from ._Products import _a1800_populations  # pyright: ignore[reportPrivateUsage]


class Trigger:
    def __init__(self, trigger_type: TriggerType, *args: Any) -> None:
        match(trigger_type):
            case TriggerType.TRUE:
                assert len(args) == 0, f"{trigger_type.name} requires no arguments"
                self.region = NO_REGION
                pass
            case TriggerType.FALSE:
                assert len(args) == 0, f"{trigger_type.name} requires no arguments"
                self.region = NO_REGION
                pass
            case TriggerType.ALL:
                assert len(args) >= 2, f"{trigger_type.name} requires at least 2 arguments"
                for arg in args:
                    assert isinstance(
                        arg, Trigger), f"{trigger_type.name} requires arguments of type Trigger, got {type(arg)} instead"
                self.triggers: list[Trigger] = list(args)
                self.region = reduce(Region.__or__, [trigger.region for trigger in self.triggers])
            case TriggerType.LINEAR:
                assert len(args) >= 2, f"{trigger_type.name} requires at least 2 arguments"
                for arg in args:
                    assert isinstance(
                        arg, Trigger), f"{trigger_type.name} requires arguments of type Trigger, got {type(arg)} instead"
                self.triggers: list[Trigger] = list(args)
                self.region = reduce(Region.__or__, [trigger.region for trigger in self.triggers])
            case TriggerType.ANY:
                assert len(args) >= 2, f"{trigger_type.name} requires at least 2 arguments"
                for arg in args:
                    assert isinstance(
                        arg, Trigger), f"{trigger_type.name} requires arguments of type Trigger, got {type(arg)} instead"
                self.triggers: list[Trigger] = list(args)
                self.region = reduce(Region.__or__, [trigger.region for trigger in self.triggers])
            case TriggerType.SESSION_ENTER:
                assert len(args) == 1, f"{trigger_type.name} requires exactly 1 argument"
                assert isinstance(args[0], Session), f"{trigger_type.name} requires an argument of type Session, got " \
                    f"{type(args[0])} instead"
                self.session: Session = args[0]
                self.region = START_REGION
            case TriggerType.POPULATION:
                assert len(args) == 3, f"{trigger_type.name} requires exactly 3 arguments"
                assert isinstance(args[0], Region) and isinstance(args[1], str) and isinstance(args[2], int), \
                    f"{trigger_type.name} requires arguments of types (str, Region, int), got " \
                    f"({type(args[0])}, {type(args[1])}, {type(args[2])}) instead"
                self.region: Region = args[0]
                self.population: str = args[1]
                self.amount: int = args[2]
                self.guid: int = next(population for population in _a1800_populations if population.name ==
                                      self.population and self.region in population.region).guid
            case TriggerType.UNLOCK:
                assert len(args) == 3, f"{trigger_type.name} requires exactly 3 arguments"
                assert isinstance(args[0], int) and isinstance(args[1], str) and isinstance(args[2], Region), \
                    f"{trigger_type.name} requires arguments of types (int, str, Region), got "\
                    f"({type(args[0])}, {type(args[1])}, {type(args[2])}) instead"
                self.guid = args[0]
                self.unlock_name = args[1]
                self.region = args[2]
            case TriggerType.COUNTER:
                assert len(args) == 5, f"{trigger_type.name} requires exactly 5 arguments"
                assert isinstance(args[0], int) and isinstance(args[1], int) and isinstance(args[2], str) \
                    and isinstance(args[3], str) and isinstance(args[4], Region), f"{trigger_type.name} requires "\
                    f"arguments of types (int, int, str, str, Region), got "\
                    f"({type(args[0])}, {type(args[1])}, {type(args[2])}, {type(args[3])}, {type(args[4])}) instead"
                self.guid = args[0]
                self.amount = args[1]
                self.unlock_name = args[2]
                self.product_name = args[3]
                self.region = args[4]
            case TriggerType.COUNTER_GOOD_IN_REGION:
                assert len(args) == 5, f"{trigger_type.name} requires exactly 5 arguments"
                assert isinstance(args[0], int) and isinstance(args[1], int) and isinstance(args[2], str) \
                    and isinstance(args[3], Region) and isinstance(args[4], Region), f"{trigger_type.name} requires "\
                    f"arguments of types (int, int, str, Region, Region), got "\
                    f"({type(args[0])}, {type(args[1])}, {type(args[2])}, {type(args[3])}, {type(args[4])}) instead"
                self.guid = args[0]
                self.amount = args[1]
                self.product_name = args[2]
                self.product_region = args[3]
                self.region = args[4]
            case TriggerType.DLC:
                assert len(args) == 1, f"{trigger_type.name} requires exactly 1 arguments"
                assert isinstance(args[0], DLC), f"{trigger_type.name} requires an argument of type DLC, got " \
                    f"{type(args[0])} instead"
                self.dlc = args[0]
                self.guids = {dlc.guid for dlc in DLC.__members__.values() if dlc != DLC.VANILLA and dlc in self.dlc}
                self.region = START_REGION

        self.trigger_type: TriggerType = trigger_type
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
                out_name = f"On entering: {self.session.name}"
            case TriggerType.POPULATION:
                out_name = f"{self.amount} {self.population if self.amount != 1 else self.population[:-1]}"
                if len([population for population in _a1800_populations
                        if population.name == self.population and self.region in population.region]) > 1:
                    out_name += f" ({self.region})"
            case TriggerType.UNLOCK:
                out_name = f"On unlocking: "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerType.COUNTER:
                out_name = f"Have at least {self.amount} "\
                    f"{f'{self.region.name}: ' if self.region and self.region != ALL_REGIONS else ''}{self.unlock_name}"
            case TriggerType.COUNTER_GOOD_IN_REGION:
                out_name = f"Have at least {self.amount} "\
                    f"{f'{self.product_region.name}: ' if self.product_region and self.product_region != ALL_REGIONS else ''}"\
                    f"{self.product_name[:-1] if self.product_name.endswith('s') else self.product_name} "\
                    f"in {self.region.full_name}"
            case TriggerType.DLC:
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
            case TriggerType.UNLOCK:
                return self.trigger_type, self.guid
            case TriggerType.COUNTER:
                return self.trigger_type, self.guid, self.amount
            case TriggerType.COUNTER_GOOD_IN_REGION:
                return self.trigger_type, self.guid, self.region.value, self.amount
            case TriggerType.DLC:
                return self.trigger_type, self.dlc.value

    def add_rules_requirement(self, name: str, region: Region) -> Self:
        if not self.rules_requirements:
            self.rules_requirements: set[tuple[str, Region]] = {(name, region)}
        else:
            self.rules_requirements.add((name, region))
        return self


TRUE: Trigger = Trigger(TriggerType.TRUE)
FALSE: Trigger = Trigger(TriggerType.FALSE)
ALL: Callable[..., Trigger] = lambda *triggers: Trigger(TriggerType.ALL, *triggers)
LINEAR: Callable[..., Trigger] = lambda *triggers: Trigger(TriggerType.LINEAR, *triggers)
ANY: Callable[..., Trigger] = lambda *triggers: Trigger(TriggerType.ANY, *triggers)
POPULATION: Callable[[Region, str, int], Trigger] = lambda region, population, amount: Trigger(
    TriggerType.POPULATION, region, population, amount)
SESSION_ENTER: Callable[[Session], Trigger] = lambda session: Trigger(TriggerType.SESSION_ENTER, session)
UNLOCK: Callable[[int, str, Region], Trigger] = lambda guid, unlock_name, region: Trigger(
    TriggerType.UNLOCK, guid, unlock_name, region)
COUNTER: Callable[[int, int, str, str, Region], Trigger] = lambda guid, amount, unlock_name, product_name, region: Trigger(
    TriggerType.COUNTER, guid, amount, unlock_name, product_name, region)
COUNTER_GOOD_IN_REGION: Callable[[int, int, str, Region, Region], Trigger] = lambda guid, amount, product_name, product_region, region: Trigger(
    TriggerType.COUNTER_GOOD_IN_REGION, guid, amount, product_name, product_region, region)
