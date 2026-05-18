from functools import reduce
from typing import Any, Callable

from ._Enums import NO_REGION, Region, Session, TriggerType
from ._Product import find_populations


class Trigger:
    def __init__(self, trigger_type: TriggerType, *args: Any) -> None:
        match(trigger_type):
            case TriggerType.TRUE:
                assert len(args) == 0, f"{trigger_type} requires no arguments"
                self.region = NO_REGION
                pass
            case TriggerType.ALL:
                assert len(args) >= 2, f"{trigger_type} requires at least 2 arguments"
                for arg in args:
                    assert isinstance(
                        arg, Trigger), f"{trigger_type} requires arguments of type Trigger, got {type(arg)} instead"
                self.triggers: list[Trigger] = list(args)
                self.region = reduce(Region.__or__, [trigger.region for trigger in self.triggers])
            case TriggerType.ANY:
                assert len(args) >= 2, f"{trigger_type} requires at least 2 arguments"
                for arg in args:
                    assert isinstance(
                        arg, Trigger), f"{trigger_type} requires arguments of type Trigger, got {type(arg)} instead"
                self.triggers: list[Trigger] = list(args)
                self.region = reduce(Region.__or__, [trigger.region for trigger in self.triggers])
            case TriggerType.SESSION_ENTER:
                assert len(args) == 1, f"{trigger_type} requires at exactly 1 argument"
                assert isinstance(args[0], Session), f"{trigger_type} requires arguments of type str, got " \
                    f"{type(args[0])} instead"
                self.session: Session = args[0]
                self.region = self.session.region
            case TriggerType.POPULATION:
                assert len(args) == 3, f"{trigger_type} requires at exactly 3 arguments"
                assert isinstance(args[0], Region) and isinstance(args[1], str) and isinstance(args[2], int), \
                    f"{trigger_type} requires arguments of type (str, Region, int), got " \
                    f"({type(args[0])}, {type(args[1])}, {type(args[2])}) instead"
                self.region: Region = args[0]
                self.population: str = args[1]
                self.amount: int = args[2]
                self.guid: int = next(find_populations(self.population, self.region)).guid
        self.trigger_type: TriggerType = trigger_type
        self.ap_location_name: str = self._get_ap_location_name()

    def _get_ap_location_name(self) -> str:
        match(self.trigger_type):
            case TriggerType.TRUE:
                return "True"
            case TriggerType.ALL:
                out_name = f"({self.triggers[0].get_ap_location_name()})"
                for trigger in self.triggers[1:]:
                    out_name += f" AND ({trigger.get_ap_location_name()})"
            case TriggerType.ANY:
                out_name = f"({self.triggers[0].get_ap_location_name()})"
                for trigger in self.triggers[1:]:
                    out_name += f" OR ({trigger.get_ap_location_name()})"
            case TriggerType.SESSION_ENTER:
                out_name = f"On entering: {self.session.name}"
            case TriggerType.POPULATION:
                out_name = f"{self.amount} {self.population if self.amount != 1 else self.population[:-1]}"
                if len(list(find_populations(self.population))) > 1:
                    out_name += f" ({self.region})"
        return out_name

    def get_ap_location_name(self, name: str = "") -> str:
        return f"{self.ap_location_name}{f' ({name})' if name else ''}"

    def get_sort_key(self) -> tuple[TriggerType | Session | int, ...]:
        match(self.trigger_type):
            case TriggerType.TRUE:
                return self.trigger_type,
            case TriggerType.ALL:
                return self.trigger_type, *[key for sort_key in
                                            sorted([trigger.get_sort_key() for trigger in self.triggers])
                                            for key in sort_key]
            case TriggerType.ANY:
                return self.trigger_type, *[key for sort_key in
                                            sorted([trigger.get_sort_key() for trigger in self.triggers])
                                            for key in sort_key]
            case TriggerType.SESSION_ENTER:
                return self.trigger_type, self.session
            case TriggerType.POPULATION:
                return self.trigger_type, self.guid, self.amount


TRUE: Trigger = Trigger(TriggerType.TRUE)
ALL: Callable[..., Trigger] = lambda *triggers: Trigger(TriggerType.ALL, *triggers)
ANY: Callable[..., Trigger] = lambda *triggers: Trigger(TriggerType.ANY, *triggers)
POPULATION: Callable[[Region, str, int], Trigger] = lambda region, population, amount: Trigger(
    TriggerType.POPULATION, region, population, amount)
SESSION_ENTER: Callable[[Session], Trigger] = lambda session: Trigger(TriggerType.SESSION_ENTER, session)
