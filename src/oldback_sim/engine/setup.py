from dataclasses import dataclass
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.rng import RNG

@dataclass(slots=True)
class SetupConfig:
    enforce_mulligan: bool = False


def is_basic_pokemon(card_id: str) -> bool:
    return card_id in {"gastly_expansion_sheet", "voltorb_expansion_sheet", "ditto_expansion_sheet", "rattata_team_rocket", "unown_e_pf2"}


def init_game_state(self_deck: list[str], opp_deck: list[str], seed: int, config: SetupConfig | None = None) -> GameState:
    config = config or SetupConfig()
    rng = RNG(seed)
    def setup(deck_cards: list[str]) -> PlayerState:
        cards = list(deck_cards)
        rng.shuffle(cards)
        hand = cards[:7]
        if config.enforce_mulligan and not any(is_basic_pokemon(c) for c in hand):
            raise NotImplementedError("TODO: mulligan handling")
        prizes = cards[7:13]
        deck = cards[13:]
        return PlayerState(hand=hand, prizes=prizes, deck=deck)
    return GameState(players={"self": setup(self_deck), "opponent": setup(opp_deck)})
