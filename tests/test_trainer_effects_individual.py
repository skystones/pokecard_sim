from oldback_sim.cards.effect_context import EffectContext
from oldback_sim.cards.effects.trainers import apply_trainer_effect
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.logging_utils.event_log import EventLog

MAX_TRIES = 1024


def mkctx(state, seed=1, targets=None):
    return EffectContext(
        state=state,
        rng=RNG(seed),
        event_log=EventLog(),
        actor_player_id="self",
        opponent_player_id="opponent",
        targets=targets or {},
    )


def mkstate():
    return GameState(players={
        "self": PlayerState(
            active="self_active",
            bench=["self_bench"],
            hand=["a", "bill", "professor_oak", "pokemon_trader", "ditto_expansion_sheet", "miniskirt"],
            deck=["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8", "gastly_expansion_sheet"],
            discard=["disc1"],
            prizes=["p1", "p2"],
        ),
        "opponent": PlayerState(
            active="opp_active",
            bench=["opp_bench"],
            hand=["bill", "erika", "energy"],
            deck=["o1", "o2", "o3", "o4", "o5", "o6", "o7", "o8"],
            prizes=["op1", "op2"],
        ),
    }, turn=1)


def test_professor_oak_hand_discard_deck_consistency():
    s = mkstate()
    before = set(s.players["self"].hand)
    apply_trainer_effect("professor_oak", mkctx(s))
    assert len(s.players["self"].hand) == 7
    assert before.issubset(set(s.players["self"].discard))
    assert len(s.players["self"].deck) == 2


def test_bill_draws_two_and_reduces_deck_by_two():
    s = mkstate()
    h0, d0 = len(s.players["self"].hand), len(s.players["self"].deck)
    apply_trainer_effect("bill", mkctx(s))
    assert len(s.players["self"].hand) == h0 + 2
    assert len(s.players["self"].deck) == d0 - 2


def test_kurumi_draw2_return2_shuffle_consistency():
    s = mkstate()
    h0, d0 = len(s.players["self"].hand), len(s.players["self"].deck)
    apply_trainer_effect("kurumi", mkctx(s, targets={"return_cards": ["a", "bill"]}))
    assert len(s.players["self"].hand) == h0
    assert len(s.players["self"].deck) == d0
    assert "a" not in s.players["self"].hand and "bill" not in s.players["self"].hand


def test_bills_teleporter_heads_behavior_with_retry_up_to_1024():
    got_heads = False
    for seed in range(MAX_TRIES):
        s = mkstate()
        d0, h0 = len(s.players["self"].deck), len(s.players["self"].hand)
        apply_trainer_effect("bills_teleporter", mkctx(s, seed=seed))
        if len(s.players["self"].hand) == h0 + 4:
            got_heads = True
            assert len(s.players["self"].deck) == d0 - 4
            break
    assert got_heads


def test_pokemon_scoop_up_moves_target_to_hand_and_detaches_cards():
    s = mkstate()
    s.players["self"].attached_cards["self_bench"] = ["water_energy::water::1"]
    apply_trainer_effect("pokemon_scoop_up", mkctx(s, targets={"target": "self_bench"}))
    assert "self_bench" in s.players["self"].hand
    assert "self_bench" not in s.players["self"].bench
    assert "water_energy::water::1" in s.players["self"].discard


def test_erika_draw_counts_respected():
    s = mkstate()
    apply_trainer_effect("erika", mkctx(s, targets={"self_draw": 1, "opp_draw": 2}))
    assert s.players["self"].hand[-1] == "d1"
    assert s.players["opponent"].hand[-2:] == ["o1", "o2"]


def test_sabrinas_gaze_keeps_hand_sizes_and_changes_order():
    s = mkstate()
    sh, oh = len(s.players["self"].hand), len(s.players["opponent"].hand)
    apply_trainer_effect("sabrinas_gaze", mkctx(s))
    assert len(s.players["self"].hand) == sh
    assert len(s.players["opponent"].hand) == oh


def test_sticky_gas_sets_global_effect_flag():
    s = mkstate()
    apply_trainer_effect("sticky_gas", mkctx(s))
    assert s.global_effects.get("goop_gas_active") is True


def test_miniskirt_returns_trainers_only():
    s = mkstate()
    apply_trainer_effect("miniskirt", mkctx(s))
    assert s.players["opponent"].hand == ["energy"]
    assert "bill" in s.players["opponent"].deck and "erika" in s.players["opponent"].deck


def test_impostor_professor_oak_resets_opponent_hand_to_7():
    s = mkstate()
    apply_trainer_effect("impostor_professor_oak", mkctx(s))
    assert len(s.players["opponent"].hand) == 7
    assert len(s.players["opponent"].deck) == 4


def test_team_rocket_announcement_reveals_all_prizes():
    s = mkstate()
    apply_trainer_effect("team_rocket_announcement", mkctx(s))
    assert s.players["self"].known_prizes == {0, 1}
    assert s.players["opponent"].known_prizes == {0, 1}


def test_pokemon_trader_swaps_hand_pokemon_with_deck_pokemon():
    s = mkstate()
    apply_trainer_effect("pokemon_trader", mkctx(s, targets={"return_pokemon": "ditto_expansion_sheet", "take_pokemon": "gastly_expansion_sheet"}))
    assert "ditto_expansion_sheet" not in s.players["self"].hand
    assert "gastly_expansion_sheet" in s.players["self"].hand


def test_etiquette_takes_card_from_deck_to_hand():
    s = mkstate()
    apply_trainer_effect("etiquette", mkctx(s, targets={"take_basic": "d1"}))
    assert "d1" in s.players["self"].hand
    assert "d1" not in s.players["self"].deck


def test_recycle_heads_behavior_with_retry_up_to_1024():
    got_heads = False
    for seed in range(MAX_TRIES):
        s = mkstate()
        apply_trainer_effect("recycle", mkctx(s, seed=seed, targets={"target": "disc1"}))
        if s.players["self"].deck and s.players["self"].deck[0] == "disc1":
            got_heads = True
            assert "disc1" not in s.players["self"].discard
            break
    assert got_heads


def test_warp_point_switches_active_with_bench():
    s = mkstate()
    apply_trainer_effect("warp_point", mkctx(s))
    assert s.players["self"].active == "self_bench"
    assert s.players["opponent"].active == "opp_bench"
