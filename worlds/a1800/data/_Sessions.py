from dataclasses import dataclass

from ._Enums import DLC, Region, Session
from ._Regions import REGIONS
from ._Requirement import A1800Requirement


_a1800_sessions: dict[Session, tuple[DLC, set[tuple[str, Region]]]] = {
    Session.OW: (DLC.VANILLA, set()),
    Session.NW: (DLC.VANILLA, set()),
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

    def init(self, enabled_dlcs: set[DLC]) -> None:
        global _a1800_sessions

        self._a1800_sessions = {
            session: A1800Session(session, dlc, {A1800Requirement(name, region) for name, region in requirements})
            for session, (dlc, requirements) in _a1800_sessions.items() if dlc in enabled_dlcs
        }

        self._initialized = True

    def find_session(self, session: Session) -> A1800Session:
        assert self._initialized, "The Anno 1800 sessions module was used before it was initialized."
        return self._a1800_sessions[session]


SESSIONS = _Sessions()
