from collections.abc import Sequence
from dataclasses import dataclass

from ._Enums import ALL_REGIONS, DLC, Region, Session, TriggerConditionType
from ._ParsedOptions import ParsedOptions
from ._Products import PRODUCTS
from ._Regions import REGIONS
from ._Requirement import A1800Requirement
from ._TriggerCondition import TriggerCondition
from ._Unlocks import UNLOCKS


_a1800_sessions: dict[Session, tuple[DLC, set[tuple[str, Region]]]] = {
    Session.OW: (DLC.VANILLA, set()),
    Session.NW: (DLC.VANILLA, set()),
    Session.CT: (DLC.SUNKEN_TREASURES, {("Expedition: Cape Trelawney", ALL_REGIONS)}),
    Session.AR: (DLC.THE_PASSAGE, set()),
    Session.EN: (DLC.LAND_OF_LIONS, set()),
}


@dataclass
class A1800Session:
    session: Session
    dlc: DLC
    requirements: set[A1800Requirement]

    def __post_init__(self) -> None:
        anno_region = REGIONS.find_region(self.session.region)
        assert anno_region, \
            f"Trying to create session {self.session.name} for non-existent region {self.session.region}"
        self.requirements |= anno_region.entry_requirements


class _Sessions:
    _initialized: bool = False

    def init(self, parsed_options: ParsedOptions) -> None:
        global _a1800_sessions

        self._a1800_sessions = {
            session: A1800Session(session, dlc, {A1800Requirement(name, region) for name, region in requirements})
            for session, (dlc, requirements) in _a1800_sessions.items() if dlc in parsed_options.enabled_dlcs
        }

        for unlock in UNLOCKS.get_unlocks():
            unlock.condition = self._clean_dlc_condition(parsed_options.enabled_dlcs, unlock.condition)

        self._initialized = True

        # Assure all references exist
        for session in self._a1800_sessions.values():
            for requirement in session.requirements:
                assert next(PRODUCTS.find_products(requirement.name, requirement.region), None) \
                    or next(UNLOCKS.find_unlocks(requirement.name, requirement.region), None), \
                    f"Session {session.session.full_name} references non-existent requirement {requirement}"

    def get_sessions(self) -> Sequence[A1800Session]:
        assert self._initialized, "The Anno 1800 sessions module was used before it was initialized."
        return list(self._a1800_sessions.values())

    def find_session(self, session: Session) -> A1800Session:
        assert self._initialized, "The Anno 1800 sessions module was used before it was initialized."
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


SESSIONS = _Sessions()
