from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.actions import ActionKind


def _state(self_ps: PlayerState, opp_ps: PlayerState | None = None):
    return GameState(players={"self": self_ps, "opponent": opp_ps or PlayerState()}, active_player="self")


def test_bench_basic_actions():
    s = _state(PlayerState(active="ditto#1", hand=["voltorb_expansion_sheet#1", "electrode_base#1"]))
    acts = legal_actions(s, "self")
    bench = [a for a in acts if a.kind == ActionKind.BENCH_BASIC_FROM_HAND]
    assert len(bench) == 1
    s.players["self"].bench = [f"b{i}" for i in range(5)]
    assert not [a for a in legal_actions(s, "self") if a.kind == ActionKind.BENCH_BASIC_FROM_HAND]


def test_attach_energy_actions():
    s = _state(PlayerState(active="ditto#1", bench=["voltorb#1"], hand=["water_energy#1"]))
    assert len([a for a in legal_actions(s, "self") if a.kind == ActionKind.ATTACH_ENERGY]) == 2
    s.players["self"].used_flags["used_manual_energy_attachment_this_turn"] = True
    assert not [a for a in legal_actions(s, "self") if a.kind == ActionKind.ATTACH_ENERGY]


def test_trainer_actions():
    s = _state(PlayerState(active="ditto#1", hand=["professor_oak#1", "erika#1"]))
    assert len([a for a in legal_actions(s, "self") if a.kind == ActionKind.PLAY_TRAINER]) == 2
    s.players["self"].trainer_lock_until_end_of_turn = True
    assert not [a for a in legal_actions(s, "self") if a.kind == ActionKind.PLAY_TRAINER]


def test_retreat_actions():
    s = _state(PlayerState(active="ditto#1", bench=["voltorb#1"], attached_cards={"ditto#1": ["water_energy#1"]}, used_flags={"retreat_cost::ditto#1": 0}))
    assert [a for a in legal_actions(s, "self") if a.kind == ActionKind.RETREAT]
    s.players["self"].used_flags["status_sleep::ditto#1"] = True
    assert not [a for a in legal_actions(s, "self") if a.kind == ActionKind.RETREAT]


def test_pokemon_power_actions():
    s = _state(PlayerState(active="ditto_expansion_sheet#1", bench=["voltorb#1"]))
    assert [a for a in legal_actions(s, "self") if a.kind == ActionKind.USE_POKEMON_POWER and a.params.get("ability_id") == "great_transform"]
    s.players["self"].used_flags["used_power::great_transform::ditto_expansion_sheet#1"] = True
    assert not [a for a in legal_actions(s, "self") if a.kind == ActionKind.USE_POKEMON_POWER and a.params.get("ability_id") == "great_transform"]


def test_attack_actions_and_end_turn_gate():
    s = _state(PlayerState(active="shining_raichu#1", attached_cards={"shining_raichu#1": ["eneene::x::water::2", "eneene::x::lightning::2"]}))
    attacks = [a for a in legal_actions(s, "self") if a.kind == ActionKind.USE_ATTACK]
    assert any(a.params["attack_id"] == "thundersquall" for a in attacks)
    assert any(a.kind == ActionKind.END_TURN for a in legal_actions(s, "self"))
    s.global_effects["pending_choice"] = True
    assert not any(a.kind == ActionKind.END_TURN for a in legal_actions(s, "self"))
