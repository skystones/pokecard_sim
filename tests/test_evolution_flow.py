from oldback_sim.engine.actions import ActionKind
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.simulator import Simulator
from oldback_sim.engine.state import GameState, PlayerState


def test_evolve_replaces_target_and_keeps_attached_cards():
    s = GameState(
        players={
            "self": PlayerState(
                active="voltorb_expansion_sheet#1",
                hand=["electrode_base#1"],
                attached_cards={"voltorb_expansion_sheet#1": ["water_energy#1"]},
                used_flags={"in_play_turn::voltorb_expansion_sheet#1": 1},
            ),
            "opponent": PlayerState(),
        },
        turn=2,
        active_player="self",
    )
    sim = Simulator(s)
    evolve = next(a for a in legal_actions(s, "self") if a.kind == ActionKind.EVOLVE_FROM_HAND)
    sim.step(evolve)

    me = s.players["self"]
    assert me.active == "electrode_base#1"
    assert me.attached_cards["electrode_base#1"] == ["water_energy#1"]
    assert "voltorb_expansion_sheet#1" not in me.attached_cards
