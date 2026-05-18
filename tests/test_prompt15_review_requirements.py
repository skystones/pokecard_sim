from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.learning.env import RLEnv
from oldback_sim.logging_utils.event_log import EventLog
from oldback_sim.objectives.shining_raichu_plan import compare_scores


def test_lexicographic_order_prefers_hard_over_soft():
    # hard success probability is primary objective
    assert compare_scores((0.60, 0.0), (0.59, 100.0)) == 1


def test_lexicographic_order_uses_soft_only_on_hard_tie():
    assert compare_scores((0.50, 2.0), (0.50, 1.0)) == 1


def test_hard_failure_can_have_high_soft_score():
    # soft-like events only
    state = GameState(players={"self": PlayerState(deck=["full_heal_energy", "miniskirt"]), "opponent": PlayerState()})
    log = EventLog()
    log.add("energy_attached", {"target": "shining_raichu", "card_id": "water_energy"}, 2)
    log.add("eneene_4th_success", {"water_on_raichu": 6}, 2)

    from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, evaluate_soft_score

    assert evaluate_hard_success(state, log) is False
    assert evaluate_soft_score(state, log) >= 3


def test_rl_env_reports_invalid_action_count():
    env = RLEnv("decks/shining_raichu_v1.yaml", "decks/opponent_stub.yaml")
    env.reset(seed=123)
    _ = env.get_action_mask()
    _, _, terminated, _, info = env.step(999999)  # invalid action id
    assert terminated is True
    assert info["illegal_action"] is True
    assert info["invalid_action_count"] >= 1
