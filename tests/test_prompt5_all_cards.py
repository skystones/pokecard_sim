from oldback_sim.cards.effect_context import EffectContext
from oldback_sim.cards.effects.pokemon import apply_pokemon_effect
from oldback_sim.cards.effects.trainers import apply_trainer_effect
from oldback_sim.cards.effects.energy import apply_energy_effect
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.rng import RNG
from oldback_sim.logging_utils.event_log import EventLog


def mkctx(state, targets=None):
    return EffectContext(state=state, rng=RNG(7), event_log=EventLog(), actor_player_id="self", opponent_player_id="opponent", targets=targets or {})


def test_all_trainers_and_pokemon_smoke():
    s = GameState(players={
        "self": PlayerState(active="a", bench=["b"], hand=["professor_oak", "bill", "kurumi", "pokemon_trader", "x"], deck=["p1", "p2", "p3", "p4", "p5", "p6", "p7", "p8"], discard=["d1"], prizes=["pr1", "pr2"]),
        "opponent": PlayerState(active="oa", bench=["ob"], hand=["bill", "energy"], deck=["opd1", "opd2", "opd3"], prizes=["opp1"]),
    }, turn=1)

    apply_trainer_effect("bill", mkctx(s))
    apply_trainer_effect("kurumi", mkctx(s, {"return_cards": ["x", "p1"]}))
    apply_trainer_effect("bills_teleporter", mkctx(s))
    apply_trainer_effect("erika", mkctx(s, {"self_draw": 1, "opp_draw": 1}))
    apply_trainer_effect("sabrinas_gaze", mkctx(s))
    apply_trainer_effect("sticky_gas", mkctx(s))
    apply_trainer_effect("miniskirt", mkctx(s))
    apply_trainer_effect("impostor_professor_oak", mkctx(s))
    apply_trainer_effect("team_rocket_announcement", mkctx(s))
    s.players["self"].hand.append("ditto_expansion_sheet")
    s.players["self"].deck.append("gastly_expansion_sheet")
    apply_trainer_effect("pokemon_trader", mkctx(s, {"return_pokemon": "ditto_expansion_sheet", "take_pokemon": "gastly_expansion_sheet"}))
    apply_trainer_effect("etiquette", mkctx(s, {"take_basic": "p2"}))
    apply_trainer_effect("recycle", mkctx(s, {"target": "d1"}))
    apply_trainer_effect("warp_point", mkctx(s))

    apply_pokemon_effect("thunder_squall", mkctx(s, {"opponent_bench_target": "ob", "water_energy_count": 2}))
    apply_pokemon_effect("lightning_slash", mkctx(s))
    apply_pokemon_effect("water_slash", mkctx(s, {"extra_water": 1}))
    apply_pokemon_effect("electric_shock", mkctx(s))
    apply_pokemon_effect("group_spark", mkctx(s))
    apply_pokemon_effect("mischief", mkctx(s, {"prize_index": 0}))
    apply_pokemon_effect("bite", mkctx(s))
    apply_pokemon_effect("engage", mkctx(s, {"self_return_hand": True, "opp_return_hand": True}))
    apply_pokemon_effect("hidden_power", mkctx(s))
    apply_pokemon_effect("scare", mkctx(s))
    apply_pokemon_effect("darkness", mkctx(s))
    apply_pokemon_effect("electricity", mkctx(s))

    apply_energy_effect("water_energy", mkctx(s, {"attach_target": "a"}))
    apply_energy_effect("full_heal_energy", mkctx(s, {"attach_target": "a"}))

    assert s.players["opponent"].trainer_lock_until_end_of_turn is True
    assert s.global_effects["sticky_gas_active"] is True
