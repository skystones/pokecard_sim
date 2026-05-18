from dataclasses import dataclass
from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.engine.rng import RNG

@dataclass(slots=True)
class SetupConfig:
    enforce_mulligan: bool = False


DEFAULT_ACTIVE_PRIORITY = [
    "gastly_expansion_sheet",
    "voltorb_expansion_sheet",
    "rattata_team_rocket",
    "ditto_expansion_sheet",
    "shining_raichu",
    "unown_e_pf2",
    "shining_kabutops",
]


def is_basic_pokemon(card_id: str) -> bool:
    return card_id in {"gastly_expansion_sheet", "voltorb_expansion_sheet", "ditto_expansion_sheet", "rattata_team_rocket", "unown_e_pf2"}


def _base(card_instance: str) -> str:
    return card_instance.split("#", 1)[0]


def _draw_opening_hand_with_mulligan(deck_cards: list[str], rng: RNG, enforce_mulligan: bool) -> tuple[list[str], list[str], int]:
    mulligan_count = 0
    cards = list(deck_cards)
    while True:
        rng.shuffle(cards)
        hand = cards[:7]
        remaining = cards[7:]
        if any(is_basic_pokemon(_base(c)) for c in hand):
            return hand, remaining, mulligan_count
        if not enforce_mulligan:
            raise NotImplementedError("TODO: mulligan handling")
        mulligan_count += 1


def _pick_active_from_hand(hand: list[str], priority: list[str]) -> str | None:
    basics = [c for c in hand if is_basic_pokemon(_base(c))]
    if not basics:
        return None
    order = {card_id: i for i, card_id in enumerate(priority)}
    return min(basics, key=lambda c: (order.get(_base(c), len(order)), hand.index(c)))


def init_game_state(self_deck: list[str], opp_deck: list[str], seed: int, config: SetupConfig | None = None) -> GameState:
    config = config or SetupConfig()
    rng = RNG(seed)

    self_hand, self_rest, self_mulligans = _draw_opening_hand_with_mulligan(self_deck, rng, config.enforce_mulligan)
    opp_hand, opp_rest, opp_mulligans = _draw_opening_hand_with_mulligan(opp_deck, rng, config.enforce_mulligan)

    if self_mulligans > 0 and opp_mulligans == 0:
        n = min(len(opp_rest), self_mulligans * 2)
        opp_hand.extend(opp_rest[:n])
        opp_rest = opp_rest[n:]
    if opp_mulligans > 0 and self_mulligans == 0:
        n = min(len(self_rest), opp_mulligans * 2)
        self_hand.extend(self_rest[:n])
        self_rest = self_rest[n:]

    self_prizes, self_deck = self_rest[:6], self_rest[6:]
    opp_prizes, opp_deck_cards = opp_rest[:6], opp_rest[6:]

    self_active = _pick_active_from_hand(self_hand, DEFAULT_ACTIVE_PRIORITY)
    if self_active is not None:
        self_hand.remove(self_active)
    opp_active = _pick_active_from_hand(opp_hand, DEFAULT_ACTIVE_PRIORITY)
    if opp_active is not None:
        opp_hand.remove(opp_active)

    return GameState(players={
        "self": PlayerState(hand=self_hand, prizes=self_prizes, deck=self_deck, active=self_active),
        "opponent": PlayerState(hand=opp_hand, prizes=opp_prizes, deck=opp_deck_cards, active=opp_active),
    })
