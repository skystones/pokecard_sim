import pytest
from oldback_sim.cards.card_registry import load_card_defs, load_deck_list


def test_load_target_and_opponent_decks():
    defs = load_card_defs('src/oldback_sim/cards/card_defs.yaml')
    assert len(load_deck_list('decks/shining_raichu_v1.yaml', defs)) == 60
    assert len(load_deck_list('decks/opponent_stub.yaml', defs)) == 60


def test_unknown_card_raises(tmp_path):
    defs = load_card_defs('src/oldback_sim/cards/card_defs.yaml')
    p = tmp_path / 'bad.yaml'
    p.write_text('cards:\n  not_exists: 60\n', encoding='utf-8')
    with pytest.raises(ValueError):
        load_deck_list(p, defs)
