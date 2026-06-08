from typing import Self

from ._Enums import TriggerActionType


class TriggerAction:
    type_: TriggerActionType
    unlock_guids: list[int]
    unhide_guids: list[int]
    text_guid: int
    text: str

    def __init__(self, type_: TriggerActionType) -> None:
        self.type_ = type_

    @classmethod
    def UNLOCK(cls, unlock_guids: list[int], unhide_guids: list[int] = []) -> Self:
        action = cls(TriggerActionType.UNLOCK)
        action.unlock_guids = unlock_guids
        action.unhide_guids = unhide_guids
        return action

    @classmethod
    def SIDE_NOTIFICATION(cls, text_guid: int, text: str) -> Self:
        action = cls(TriggerActionType.SIDE_NOTIFICATION)
        action.text_guid = text_guid
        action.text = text
        return action
