from oldback_sim.engine.actions import Action, ActionKind
from oldback_sim.engine.simulator import Simulator
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.zones import Zone


def _state():
    return GameState(
        players={
            "self": PlayerState(
                active="ditto#1",
                hand=["bill#1", "x#1"],
                deck=["d1", "d2", "d3"],
            ),
            "opponent": PlayerState(active="opp#1"),
        },
        active_player="self",
    )


def test_play_trainer_moves_card_from_hand_to_discard_and_applies_effect():
    s = _state()
    sim = Simulator(s)
    action = Action(
        kind=ActionKind.PLAY_TRAINER,
        actor_player_id="self",
        card_instance_id="bill#1",
        card_id="bill",
        source_zone=Zone.HAND,
    )

    sim.step(action)

    me = s.players["self"]
    assert "bill#1" not in me.hand
    assert "bill#1" in me.discard
    assert len(me.hand) == 3
    assert me.deck == ["d3"]


def test_play_trainer_rejects_illegal_action():
    s = _state()
    sim = Simulator(s)
    action = Action(
        kind=ActionKind.PLAY_TRAINER,
        actor_player_id="self",
        card_instance_id="bill#999",
        card_id="bill",
        source_zone=Zone.HAND,
    )

    try:
        sim.step(action)
        assert False, "expected ValueError"
    except ValueError:
        pass
