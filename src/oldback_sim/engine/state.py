from __future__ import annotations

from dataclasses import dataclass, field
from oldback_sim.cards.effect_context import PlayerId

CardId = str

@dataclass(slots=True)
class PlayerState:
    hand: list[CardId] = field(default_factory=list)
    deck: list[CardId] = field(default_factory=list)
    discard: list[CardId] = field(default_factory=list)
    prizes: list[CardId] = field(default_factory=list)
    active: CardId | None = None
    bench: list[CardId] = field(default_factory=list)
    attached_cards: dict[CardId, list[CardId]] = field(default_factory=dict)
    used_flags: dict[str, bool] = field(default_factory=dict)

@dataclass(slots=True)
class GameState:
    players: dict[PlayerId, PlayerState]
    turn: int = 1
    active_player: PlayerId = "self"
