from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.objectives.objective_mode import ObjectiveMode, estimate_p_finish_this_turn, select_objective_mode


def test_estimate_p_finish_this_turn_non_turn2_zero():
    s = GameState(players={"self": PlayerState(), "opponent": PlayerState()}, turn=1)
    assert estimate_p_finish_this_turn(s) == 0.0


def test_select_mode_current_mvp_always_finish():
    s = GameState(players={"self": PlayerState(hand=["miniskirt#1"], active="ditto_expansion_sheet#1"), "opponent": PlayerState()}, turn=2)
    assert select_objective_mode(s, threshold=0.99) == ObjectiveMode.FINISH_THIS_TURN
