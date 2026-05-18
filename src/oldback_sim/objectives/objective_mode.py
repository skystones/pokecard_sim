from __future__ import annotations

from enum import Enum

from oldback_sim.engine.state import GameState


class ObjectiveMode(str, Enum):
    FINISH_THIS_TURN = "finish_this_turn"
    KEEP_LOCK_AND_PREPARE = "keep_lock_and_prepare"
    HYBRID = "hybrid"


def estimate_p_finish_this_turn(state: GameState) -> float:
    """Estimate turn-completion probability at start of turn 2.

    MVP implementation intentionally simple for 2-turn completion objective.
    TODO: replace with rollout/value-estimator and belief sampling.
    """
    me = state.players["self"]
    if state.turn != 2:
        return 0.0
    has_raichu_or_ditto = any(c.split("#", 1)[0] in {"shining_raichu", "ditto_expansion_sheet"} for c in [me.active, *me.bench] if c)
    has_combo_trainer = any(c.split("#", 1)[0] in {"impostor_professor_oak", "miniskirt"} for c in me.hand)
    return 0.7 if has_raichu_or_ditto and has_combo_trainer else 0.3


def select_objective_mode(state: GameState, threshold: float = 0.55) -> ObjectiveMode:
    p_finish = estimate_p_finish_this_turn(state)
    if p_finish >= threshold:
        return ObjectiveMode.FINISH_THIS_TURN
    # TODO: implement KEEP_LOCK_AND_PREPARE policy/search.
    return ObjectiveMode.FINISH_THIS_TURN
