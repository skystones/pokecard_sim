from oldback_sim.cards.card_registry import load_card_defs, load_deck_list
from oldback_sim.engine.setup import init_game_state
from oldback_sim.engine.observation import build_observation


def _decks():
    defs = load_card_defs('src/oldback_sim/cards/card_defs.yaml')
    return load_deck_list('decks/shining_raichu_v1.yaml', defs), load_deck_list('decks/opponent_stub.yaml', defs)


def test_init_seed_reproducibility_and_divergence():
    d1, d2 = _decks()
    s1 = init_game_state(d1, d2, seed=1)
    s2 = init_game_state(d1, d2, seed=1)
    s3 = init_game_state(d1, d2, seed=2)
    assert s1.players['self'].hand == s2.players['self'].hand
    assert s1.players['self'].prizes == s2.players['self'].prizes
    assert s1.players['self'].deck == s2.players['self'].deck
    assert s1.players['self'].deck != s3.players['self'].deck


def test_observation_no_private_leak():
    d1, d2 = _decks()
    s = init_game_state(d1, d2, seed=3)
    obs = build_observation(s, 'self')
    assert not hasattr(obs, 'deck_order')
    assert not hasattr(obs, 'prizes')
    assert obs.opponent_view.active == s.players['opponent'].active
    assert obs.opponent_view.bench == s.players['opponent'].bench
    assert obs.hand == s.players['self'].hand
