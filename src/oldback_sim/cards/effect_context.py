from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from oldback_sim.engine.state import GameState

PlayerId = str


@dataclass(slots=True)
class EffectContext:
    state: GameState
    rng: Any
    event_log: Any
    actor_player_id: PlayerId
    opponent_player_id: PlayerId
    source_card: str | None = None
    targets: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
