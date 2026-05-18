from dataclasses import dataclass
from oldback_sim.engine.zones import Zone

@dataclass(slots=True)
class Action:
    kind: str
    card_id: str | None = None
    source_zone: Zone | None = None
    target: str | None = None
