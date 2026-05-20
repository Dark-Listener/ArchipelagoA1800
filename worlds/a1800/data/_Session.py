from dataclasses import dataclass

from ._Enums import DLC, Session
from ._Region import find_region
from ._Requirement import A1800Requirement


@dataclass
class A1800Session:
    session: Session
    dlc: DLC
    requirements: set[A1800Requirement]

    def __post_init__(self) -> None:
        self.requirements |= find_region(self.session.region).enter_requirements


_a1800_sessions: dict[Session, A1800Session] = {
    Session.OW: A1800Session(Session.OW, DLC.VANILLA, set()),
    Session.NW: A1800Session(Session.NW, DLC.VANILLA, set()),
}

# Assure sessions are unique
for session, anno_session in _a1800_sessions.items():
    assert anno_session.session == session, f"Session {session} dict entry does not match"


def find_session(session: Session) -> A1800Session:
    global _a1800_sessions
    return _a1800_sessions[session]
