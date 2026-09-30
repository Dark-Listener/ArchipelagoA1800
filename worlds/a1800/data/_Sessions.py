from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ._Enums import ALL_REGIONS, DLC, Region, Session, TriggerConditionType
from ._ParsedOptions import ParsedOptions
from ._Requirement import A1800Requirement
from ._TriggerCondition import TriggerCondition

if TYPE_CHECKING:
    from . import A1800Data


A1800_SESSIONS: dict[Session, tuple[DLC, set[tuple[str, Region]]]] = {
    Session.OW: (DLC.VANILLA, set()),
    Session.NW: (DLC.VANILLA, set()),
    Session.CT: (DLC.SUNKEN_TREASURES, {
        ("Expedition: Cape Trelawney", ALL_REGIONS),
        ("Seafaring", ALL_REGIONS),
        ("Expeditions: Level 1", ALL_REGIONS),
    }),
    Session.AR: (DLC.THE_PASSAGE, set()),
    Session.EN: (DLC.LAND_OF_LIONS, set()),
}


@dataclass
class A1800Session:
    session: Session
    dlc: DLC
    requirements: set[A1800Requirement]

    def post_init(self, A1800_DATA: "A1800Data") -> None:
        anno_region = A1800_DATA.find_region(self.session.region)
        assert anno_region, \
            f"Trying to create session {self.session.name} for non-existent region {self.session.region}"
        self.requirements |= anno_region.entry_requirements


class Sessions:
    def __init__(self, A1800_DATA: "A1800Data") -> None:
        self._A1800_DATA = A1800_DATA

        global A1800_SESSIONS

        self._a1800_sessions = {
            session: A1800Session(session, dlc, {self._A1800_DATA.make_requirement(
                name, region) for name, region in requirements})
            for session, (dlc, requirements) in A1800_SESSIONS.items() if dlc in self._A1800_DATA.get_parsed_options().enabled_dlcs
        }
        for a1800_session in self._a1800_sessions.values():
            a1800_session.post_init(self._A1800_DATA)

        if Session.CT in self._a1800_sessions:
            unlock = None
            if self._A1800_DATA.get_parsed_options().enforce_cape_trelawney == ParsedOptions.EnforceCapeTrelawney.BY_ARTISANS:
                unlock = next(self._A1800_DATA.find_unlocks("Artisan Residence", Region.OW))
            if self._A1800_DATA.get_parsed_options().enforce_cape_trelawney == ParsedOptions.EnforceCapeTrelawney.BY_ENGINEERS:
                unlock = next(self._A1800_DATA.find_unlocks("Engineer Residence", Region.OW))
            if self._A1800_DATA.get_parsed_options().enforce_cape_trelawney == ParsedOptions.EnforceCapeTrelawney.BY_INVESTORS:
                unlock = next(self._A1800_DATA.find_unlocks("Investor Residence", Region.OW))
            if unlock:
                unlock.cost |= {requirement.name for requirement in self._a1800_sessions[Session.CT].requirements}

        for unlock in self._A1800_DATA.get_unlocks():
            unlock.condition = self._clean_dlc_condition(
                self._A1800_DATA.get_parsed_options().enabled_dlcs, unlock.condition)

        # Assure all references exist
        for session in self._a1800_sessions.values():
            for requirement in session.requirements:
                assert next(self._A1800_DATA.find_products(requirement.name, requirement.region), None) \
                    or next(self._A1800_DATA.find_unlocks(requirement.name, requirement.region), None), \
                    f"Session {session.session.full_name} references non-existent requirement {requirement}"

    def get_sessions(self) -> Sequence[A1800Session]:
        return list(self._a1800_sessions.values())

    def find_session(self, session: Session) -> A1800Session:
        return self._a1800_sessions[session]

    def _clean_dlc_condition(self, enabled_dlcs: DLC, condition: TriggerCondition) -> TriggerCondition:
        if condition.type_ in [TriggerConditionType.ALL, TriggerConditionType.LINEAR]:
            condition.conditions = [clean_condition for subcondition in condition.conditions for clean_condition in [
                self._clean_dlc_condition(enabled_dlcs, subcondition)] if clean_condition.type_ != TriggerConditionType.TRUE]

            if len(condition.conditions) == 0:
                return TriggerCondition.TRUE()
            elif len(condition.conditions) == 1:
                return condition.conditions[0]
            elif any([subcondition.type_ == TriggerConditionType.FALSE for subcondition in condition.conditions]):
                return TriggerCondition.FALSE()
            else:
                return condition
        elif condition.type_ == TriggerConditionType.ANY:
            condition.conditions = [clean_condition for subcondition in condition.conditions for clean_condition in [
                self._clean_dlc_condition(enabled_dlcs, subcondition)] if clean_condition.type_ != TriggerConditionType.FALSE]

            if len(condition.conditions) == 0:
                return TriggerCondition.FALSE()
            elif len(condition.conditions) == 1:
                return condition.conditions[0]
            elif any([subcondition.type_ == TriggerConditionType.TRUE for subcondition in condition.conditions]):
                return TriggerCondition.TRUE()
            else:
                return condition
        elif condition.type_ in [TriggerConditionType.SESSION_ENTER, TriggerConditionType.POPULATION_HAPPINESS]:
            return TriggerCondition.FALSE() if not condition.session in self._a1800_sessions else condition
        else:
            return condition
