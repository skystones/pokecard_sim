from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal

from oldback_sim.engine.state import PlayerId
from oldback_sim.engine.zones import Zone


class ActionKind(str, Enum):
    END_TURN = "end_turn"
    SET_ACTIVE_FROM_HAND = "set_active_from_hand"
    BENCH_BASIC_FROM_HAND = "bench_basic_from_hand"
    EVOLVE_FROM_HAND = "evolve_from_hand"
    PLAY_TRAINER = "play_trainer"
    ATTACH_ENERGY = "attach_energy"
    RETREAT = "retreat"
    SWITCH_BY_EFFECT = "switch_by_effect"
    USE_POKEMON_POWER = "use_pokemon_power"
    USE_ATTACK = "use_attack"
    CHOOSE_CARD_FROM_HAND = "choose_card_from_hand"
    CHOOSE_CARD_FROM_DECK = "choose_card_from_deck"
    CHOOSE_CARD_FROM_DISCARD = "choose_card_from_discard"
    CHOOSE_POKEMON_IN_PLAY = "choose_pokemon_in_play"
    CHOOSE_PRIZE = "choose_prize"
    CHOOSE_ENERGY_TO_DISCARD = "choose_energy_to_discard"
    CHOOSE_ENERGY_TYPE = "choose_energy_type"


@dataclass(frozen=True, slots=True)
class PokemonTarget:
    player_id: PlayerId
    zone: Literal["active", "bench"]
    index: int | None = None
    pokemon_instance_id: str | None = None


@dataclass(frozen=True, slots=True)
class CardTarget:
    player_id: PlayerId
    zone: Zone
    card_instance_id: str


@dataclass(frozen=True, slots=True)
class CompositeTarget:
    items: tuple[Any, ...]


ActionTarget = PokemonTarget | CardTarget | CompositeTarget | dict[str, Any]


@dataclass(frozen=True, slots=True)
class Action:
    kind: ActionKind | str
    actor_player_id: PlayerId = "self"
    action_id: str = ""
    card_instance_id: str | None = None
    card_id: str | None = None
    source_zone: Zone | None = None
    target: ActionTarget | None = None
    params: dict[str, Any] = field(default_factory=dict)
    priority_hint: float = 0.0
