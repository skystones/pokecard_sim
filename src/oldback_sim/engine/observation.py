from __future__ import annotations

from dataclasses import dataclass
from oldback_sim.engine.state import GameState

@dataclass(slots=True)
class PublicPlayerView:
    active: str | None
    bench: list[str]
    discard: list[str]
    deck_count: int
    prizes_count: int

@dataclass(slots=True)
class Observation:
    player_id: str
    turn: int
    hand: list[str]
    self_view: PublicPlayerView
    opponent_view: PublicPlayerView
    subgoal_progress: dict[str, bool]


def build_observation(state: GameState, player_id: str, subgoal_progress: dict[str, bool] | None = None) -> Observation:
    opponent_id = [pid for pid in state.players if pid != player_id][0]
    me = state.players[player_id]
    op = state.players[opponent_id]
    return Observation(
        player_id=player_id,
        turn=state.turn,
        hand=list(me.hand),
        self_view=PublicPlayerView(me.active, list(me.bench), list(me.discard), len(me.deck), len(me.prizes)),
        opponent_view=PublicPlayerView(op.active, list(op.bench), list(op.discard), len(op.deck), len(op.prizes)),
        subgoal_progress=subgoal_progress or {},
    )
