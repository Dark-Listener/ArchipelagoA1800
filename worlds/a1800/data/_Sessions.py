from dataclasses import dataclass


from ._Enums import ALL_REGIONS, DLC, Region, Session, TriggerType
from ._Products import PRODUCTS
from ._Regions import REGIONS
from ._Requirement import A1800Requirement
from ._Trigger import FALSE, TRUE, Trigger
from ._Unlocks import UNLOCKS


_a1800_sessions: dict[Session, tuple[DLC, set[tuple[str, Region]]]] = {
    Session.OW: (DLC.VANILLA, set()),
    Session.NW: (DLC.VANILLA, set()),
    Session.CT: (DLC.SUNKEN_TREASURES, {("Expedition: Cape Trelawney", ALL_REGIONS)}),
    Session.AR: (DLC.THE_PASSAGE, set()),
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

    def init(self, enabled_dlcs: DLC) -> None:
        global _a1800_sessions

        self._a1800_sessions = {
            session: A1800Session(session, dlc, {A1800Requirement(name, region) for name, region in requirements})
            for session, (dlc, requirements) in _a1800_sessions.items() if dlc in enabled_dlcs
        }

        for unlock in UNLOCKS.get_unlocks():
            unlock.trigger = self._clean_dlc_trigger(enabled_dlcs, unlock.trigger)

        self._initialized = True

        # Assure all references exist
        for session in self._a1800_sessions.values():
            for requirement in session.requirements:
                assert next(PRODUCTS.find_products(requirement.name, requirement.region), None) \
                    or next(UNLOCKS.find_unlocks(requirement.name, requirement.region), None), \
                    f"Session {session.session.full_name} references non-existent requirement {requirement}"

    def find_session(self, session: Session) -> A1800Session:
        assert self._initialized, "The Anno 1800 sessions module was used before it was initialized."
        return self._a1800_sessions[session]

    def _clean_dlc_trigger(self, enabled_dlcs: DLC, trigger: Trigger) -> Trigger:
        match(trigger.trigger_type):
            case TriggerType.TRUE:
                return trigger
            case TriggerType.FALSE:
                return trigger
            case TriggerType.ALL:
                trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                    self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.TRUE]

                if len(trigger.triggers) == 0:
                    return TRUE
                elif len(trigger.triggers) == 1:
                    return trigger.triggers[0]
                elif any([subtrigger.trigger_type == TriggerType.FALSE for subtrigger in trigger.triggers]):
                    return FALSE
                else:
                    return trigger
            case TriggerType.ANY:
                trigger.triggers = [clean_trigger for subtrigger in trigger.triggers for clean_trigger in [
                    self._clean_dlc_trigger(enabled_dlcs, subtrigger)] if clean_trigger.trigger_type != TriggerType.FALSE]

                if len(trigger.triggers) == 0:
                    return FALSE
                elif len(trigger.triggers) == 1:
                    return trigger.triggers[0]
                elif any([subtrigger.trigger_type == TriggerType.TRUE for subtrigger in trigger.triggers]):
                    return TRUE
                else:
                    return trigger
            case TriggerType.SESSION_ENTER:
                return FALSE if not trigger.session in self._a1800_sessions else trigger
            case TriggerType.POPULATION:
                return trigger
            case TriggerType.UNLOCK:
                return trigger
            case TriggerType.DLC:
                return trigger


SESSIONS = _Sessions()
