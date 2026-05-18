from oldback_sim.cards.effect_context import EffectContext
from oldback_sim.cards.effects import apply_pokemon_effect, count_effective_energy
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.rng import RNG
from oldback_sim.logging_utils.event_log import EventLog


def test_ditto_transform_to_electrode_then_eneene_attaches_special_energy():
    state = GameState(players={
        "self": PlayerState(active="ditto#1", bench=["shining_raichu#1"], prizes=["p1"]),
        "opponent": PlayerState(prizes=["op1", "op2"]),
    }, turn=2)
    log = EventLog()
    ctx = EffectContext(state=state, rng=RNG(1), event_log=log, actor_player_id="self", opponent_player_id="opponent", source_card="ditto#1", targets={"coin_result": True, "transform_to": "electrode_base"})
    apply_pokemon_effect("great_transform", ctx)

    ctx2 = EffectContext(state=state, rng=RNG(1), event_log=log, actor_player_id="self", opponent_player_id="opponent", source_card="ditto#1", targets={"attach_target": "shining_raichu#1", "energy_type": "water"})
    apply_pokemon_effect("eneene", ctx2)

    assert "ditto#1" in state.players["self"].discard
    assert state.players["opponent"].hand == ["op1"]
    attached = state.players["self"].attached_cards["shining_raichu#1"]
    assert any(t.startswith("eneene::ditto#1::water::2") for t in attached)
    assert count_effective_energy(attached, "water") == 2


def test_ditto_transform_to_rattata_can_use_mischief():
    state = GameState(players={
        "self": PlayerState(active="ditto#1", deck=["top_card"], prizes=["prize_card"]),
        "opponent": PlayerState(),
    }, turn=2)
    log = EventLog()

    transform_ctx = EffectContext(
        state=state,
        rng=RNG(3),
        event_log=log,
        actor_player_id="self",
        opponent_player_id="opponent",
        source_card="ditto#1",
        targets={"coin_result": True, "transform_to": "rattata_team_rocket"},
    )
    apply_pokemon_effect("great_transform", transform_ctx)

    mischief_ctx = EffectContext(
        state=state,
        rng=RNG(3),
        event_log=log,
        actor_player_id="self",
        opponent_player_id="opponent",
        source_card="ditto#1",
        targets={"prize_index": 0},
    )
    apply_pokemon_effect("mischief", mischief_ctx)

    assert state.players["self"].used_flags["transform_target::ditto#1"] == "rattata_team_rocket"
    assert state.players["self"].deck[0] == "prize_card"
    assert state.players["self"].prizes[0] == "top_card"