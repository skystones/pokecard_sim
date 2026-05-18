from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class Event:
    idx: int
    turn: int
    kind: str
    payload: dict[str, Any]
