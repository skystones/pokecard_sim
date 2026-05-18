from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

CardId = str

@dataclass(slots=True)
class CardDef:
    id: CardId
    jp_name: str
    set_name: str
    category: str
    count_in_target_deck: int
    reviewed: bool = False
    guessed: bool = False
    source_urls: list[str] | None = None
    notes: str = ""
    implemented_effects: list[str] | None = None
    evolves_from: str = ""


def _parse_scalar(v: str):
    v = v.strip()
    if v == 'false':
        return False
    if v == 'true':
        return True
    if v == '[]':
        return []
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.isdigit():
        return int(v)
    return v


def load_card_defs(path: str | Path) -> dict[CardId, CardDef]:
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    rows = []
    current = None
    for line in lines:
        if not line.strip():
            continue
        if line.startswith('- '):
            if current:
                rows.append(current)
            current = {}
            key, val = line[2:].split(':', 1)
            current[key.strip()] = _parse_scalar(val)
        elif current is not None and ':' in line:
            key, val = line.strip().split(':', 1)
            current[key.strip()] = _parse_scalar(val)
    if current:
        rows.append(current)
    defs = {r['id']: CardDef(**r) for r in rows}
    return defs


def load_deck_list(path: str | Path, card_defs: dict[CardId, CardDef]) -> list[CardId]:
    lines = Path(path).read_text(encoding='utf-8').splitlines()
    in_cards = False
    counts: dict[str, int] = {}
    for line in lines:
        if line.strip() == 'cards:':
            in_cards = True
            continue
        if not in_cards or not line.startswith('  '):
            continue
        key, val = line.strip().split(':', 1)
        counts[key.strip()] = int(val.strip())

    deck: list[CardId] = []
    for card_id, n in counts.items():
        if card_id not in card_defs:
            raise ValueError(f"Unknown card id: {card_id}")
        deck.extend([card_id] * int(n))
    if len(deck) != 60:
        raise ValueError(f"Deck must contain 60 cards, got {len(deck)}")
    return deck
