from operator import __eq__
from typing import Self

from ._Enums import TriggerActionType
from ._TriggerAction import TriggerAction
from ._TriggerCondition import TriggerCondition


class Trigger:
    guid: int
    condition: TriggerCondition
    actions: list[TriggerAction]

    def __init__(self, condition: TriggerCondition, actions: TriggerAction | list[TriggerAction], *, guid: int = 0) -> None:
        self.condition = condition
        self.guid = guid

        if isinstance(actions, TriggerAction):
            self.actions = [actions]
        else:
            self.actions = actions

    @classmethod
    def from_list(cls, triggers: list[Self], *, guid: int = 0) -> Self:
        if any(trigger.guid for trigger in triggers):
            raise ValueError("Triggers in list already have guids")
        identical_condition = len({trigger.condition.get_sort_key() for trigger in triggers}) == 1
        if not identical_condition:
            raise ValueError("Triggers in list did not have identical conditions")

        unlock_actions = [
            action for trigger in triggers for action in trigger.actions if action.type_ == TriggerActionType.UNLOCK]
        remaining_actions = [
            action for trigger in triggers for action in trigger.actions if action.type_ != TriggerActionType.UNLOCK]

        actions = [TriggerAction.UNLOCK(
            [guid for action in unlock_actions for guid in action.unlock_guids],
            [guid for action in unlock_actions for guid in action.unhide_guids])] + remaining_actions

        return cls(triggers[0].condition, actions, guid=guid)
