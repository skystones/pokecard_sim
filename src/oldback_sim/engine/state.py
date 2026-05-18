from __future__ import annotations

from dataclasses import dataclass, field

PlayerId = str
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
    used_flags: dict[str, bool | str] = field(default_factory=dict)
    trainer_lock_until_end_of_turn: bool = False
    known_prizes: set[int] = field(default_factory=set)


@dataclass(slots=True)
class GameState:
    players: dict[PlayerId, PlayerState]
    turn: int = 1
    active_player: PlayerId = "self"
    global_effects: dict[str, bool | int | str] = field(default_factory=dict)
