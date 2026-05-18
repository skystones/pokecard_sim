from enum import StrEnum

class Zone(StrEnum):
    HAND = "hand"
    DECK = "deck"
    DISCARD = "discard"
    PRIZES = "prizes"
    ACTIVE = "active"
    BENCH = "bench"
