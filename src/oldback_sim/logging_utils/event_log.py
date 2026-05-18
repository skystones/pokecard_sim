from dataclasses import dataclass, field
from oldback_sim.logging_utils.schemas import Event

@dataclass
class EventLog:
    events: list[Event] = field(default_factory=list)

    def add(self, kind: str, payload: dict, turn: int) -> Event:
        ev = Event(idx=len(self.events), turn=turn, kind=kind, payload=payload)
        self.events.append(ev)
        return ev
