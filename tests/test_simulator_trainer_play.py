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
    me = s.players["self"]
    hand_before = len(me.hand)
    deck_before = len(me.deck)
    discard_before = len(me.discard)
    action = Action(
        kind=ActionKind.PLAY_TRAINER,
        actor_player_id="self",
        card_instance_id="bill#1",
        card_id="bill",
        source_zone=Zone.HAND,
    )

    sim.step(action)

    assert "bill#1" not in me.hand
    assert "bill#1" in me.discard
    # Bill: 手札から1枚使って2枚ドローするため、最終的に手札は+1
    assert len(me.hand) == hand_before + 1
    assert len(me.deck) == deck_before - 2
    assert len(me.discard) == discard_before + 1


def test_play_professor_oak_keeps_zone_count_consistent():
    s = GameState(
        players={
            "self": PlayerState(
                active="ditto#1",
                hand=["professor_oak#1", "x#1", "y#1"],
                deck=["d1", "d2", "d3", "d4", "d5", "d6", "d7", "d8"],
            ),
            "opponent": PlayerState(active="opp#1"),
        },
        active_player="self",
    )
    sim = Simulator(s)
    me = s.players["self"]
    action = Action(
        kind=ActionKind.PLAY_TRAINER,
        actor_player_id="self",
        card_instance_id="professor_oak#1",
        card_id="professor_oak",
        source_zone=Zone.HAND,
    )

    sim.step(action)

    assert "professor_oak#1" in me.discard
    assert "x#1" in me.discard and "y#1" in me.discard
    assert len(me.hand) == 7
    assert len(me.deck) == 1


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
