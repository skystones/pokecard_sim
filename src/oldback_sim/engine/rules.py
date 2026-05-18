from __future__ import annotations

from itertools import combinations

from oldback_sim.engine.actions import Action, ActionKind, PokemonTarget
from oldback_sim.engine.state import GameState
from oldback_sim.engine.zones import Zone

BASIC_POKEMON = {
    "shining_raichu", "shining_kabutops", "ditto_expansion_sheet", "voltorb_expansion_sheet",
    "rattata_team_rocket", "unown_e_pf2", "gastly_expansion_sheet",
}
TRAINERS = {
    "professor_oak", "bill", "kurumi", "bills_teleporter", "pokemon_scoop_up", "erika", "sabrinas_gaze",
    "sticky_gas", "miniskirt", "impostor_professor_oak", "team_rocket_announcement", "pokemon_trader",
    "etiquette", "recycle", "warp_point",
}
ENERGIES = {"water_energy", "full_heal_energy"}


def _base(card_instance: str) -> str:
    return card_instance.split("#", 1)[0]


def _is_status_blocked(p: str, ps) -> bool:
    return bool(ps.used_flags.get(f"status_sleep::{p}")) or bool(ps.used_flags.get(f"status_paralyzed::{p}"))


def legal_set_active_from_hand_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    if p.active is not None:
        return []
    return [Action(kind=ActionKind.SET_ACTIVE_FROM_HAND, actor_player_id=player_id, card_instance_id=c, card_id=_base(c), source_zone=Zone.HAND) for c in p.hand if _base(c) in BASIC_POKEMON]


def legal_bench_basic_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    if p.active is None or len(p.bench) >= 5:
        return []
    return [Action(kind=ActionKind.BENCH_BASIC_FROM_HAND, actor_player_id=player_id, card_instance_id=c, card_id=_base(c), source_zone=Zone.HAND) for c in p.hand if _base(c) in BASIC_POKEMON]


def legal_attach_energy_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    if p.used_flags.get("used_manual_energy_attachment_this_turn"):
        return []
    targets = ([p.active] if p.active else []) + list(p.bench)
    if not targets:
        return []
    actions = []
    for c in p.hand:
        if _base(c) not in ENERGIES:
            continue
        for i, tgt in enumerate(targets):
            zone, idx = ("active", None) if i == 0 and p.active else ("bench", i - (1 if p.active else 0))
            actions.append(Action(kind=ActionKind.ATTACH_ENERGY, actor_player_id=player_id, card_instance_id=c, card_id=_base(c), source_zone=Zone.HAND, target=PokemonTarget(player_id, zone, idx, tgt)))
    return actions


def legal_trainer_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    if p.trainer_lock_until_end_of_turn:
        return []
    actions = []
    for c in p.hand:
        b = _base(c)
        if b not in TRAINERS:
            continue
        if b == "etiquette" and any(_base(h) in BASIC_POKEMON for h in p.hand) :
            continue
        if b == "etiquette" and not any(_base(d) in BASIC_POKEMON for d in p.deck):
            continue
        if b == "pokemon_trader" and (not any(_base(h) in BASIC_POKEMON for h in p.hand if h != c) or not any(_base(d) in BASIC_POKEMON for d in p.deck)):
            continue
        if b == "recycle" and len(p.discard) == 0:
            continue
        actions.append(Action(kind=ActionKind.PLAY_TRAINER, actor_player_id=player_id, card_instance_id=c, card_id=b, source_zone=Zone.HAND))
    return actions


def legal_retreat_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    a = p.active
    if a is None or not p.bench or _is_status_blocked(a, p) or p.used_flags.get(f"retreat_failed_confusion::{a}"):
        return []
    retreat_cost = int(p.used_flags.get(f"retreat_cost::{a}", 0))
    attached = p.attached_cards.get(a, [])
    if retreat_cost > len(attached):
        return []
    costs = [()] if retreat_cost == 0 else list(combinations(attached, retreat_cost))
    out = []
    for bi, b in enumerate(p.bench):
        for discard_cards in costs:
            out.append(Action(kind=ActionKind.RETREAT, actor_player_id=player_id, card_instance_id=a, card_id=_base(a), source_zone=Zone.ACTIVE, target=PokemonTarget(player_id, "bench", bi, b), params={"energy_to_discard": list(discard_cards)}))
    return out


def legal_pokemon_power_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    if state.global_effects.get("sticky_gas_active"):
        return []
    out: list[Action] = []
    in_play = ([p.active] if p.active else []) + p.bench
    for poke in in_play:
        if poke is None or _is_status_blocked(poke, p) or p.used_flags.get(f"status_confused::{poke}"):
            continue
        eff = p.used_flags.get(f"transform_target::{poke}", _base(poke))
        if eff == "ditto_expansion_sheet" and poke == p.active and not p.used_flags.get(f"used_power::great_transform::{poke}"):
            candidates = [x for x in in_play if x] + ([state.players['opponent'].active] if state.players['opponent'].active else []) + state.players['opponent'].bench
            for c in candidates:
                out.append(Action(kind=ActionKind.USE_POKEMON_POWER, actor_player_id=player_id, card_instance_id=poke, card_id=eff, source_zone=Zone.ACTIVE, target=PokemonTarget(player_id, "active", None, c), params={"ability_id": "great_transform"}))
        if eff == "electrode_base" and not p.used_flags.get(f"used_power::eneene::{poke}"):
            types = ("grass", "fire", "water", "lightning", "psychic", "fighting", "dark", "metal")
            for tgt in in_play:
                if tgt:
                    for t in types:
                        out.append(Action(kind=ActionKind.USE_POKEMON_POWER, actor_player_id=player_id, card_instance_id=poke, card_id=eff, params={"ability_id": "eneene", "energy_type": t}, target=PokemonTarget(player_id, "active" if tgt == p.active else "bench", None, tgt)))
    return out


def _energy_counts(p, poke: str) -> dict[str, int]:
    counts = {"water": 0, "lightning": 0, "psychic": 0, "colorless": 0}
    for e in p.attached_cards.get(poke, []):
        if e.startswith("eneene::"):
            t = e.split("::")[2]
            counts[t] = counts.get(t, 0) + 2
            counts["colorless"] += 2
        elif _base(e) == "water_energy":
            counts["water"] += 1
            counts["colorless"] += 1
        elif _base(e) == "full_heal_energy":
            counts["colorless"] += 1
    return counts


def can_pay_attack_cost(state: GameState, player_id: str, poke: str, attack_id: str) -> bool:
    c = _energy_counts(state.players[player_id], poke)
    if attack_id == "thundersquall":
        return c["water"] >= 2 and c["lightning"] >= 2
    if attack_id == "scare":
        return c["psychic"] >= 1
    return c["colorless"] >= 1


def legal_attack_actions(state: GameState, player_id: str) -> list[Action]:
    p = state.players[player_id]
    a = p.active
    if a is None or _is_status_blocked(a, p) or p.used_flags.get("attack_used_this_turn"):
        return []
    eff = p.used_flags.get(f"transform_target::{a}", _base(a))
    attacks = ["thundersquall"] if eff == "shining_raichu" else (["scare"] if eff == "gastly_expansion_sheet" else ["tackle"])
    return [Action(kind=ActionKind.USE_ATTACK, actor_player_id=player_id, card_instance_id=a, card_id=eff, source_zone=Zone.ACTIVE, params={"attack_id": atk}) for atk in attacks if can_pay_attack_cost(state, player_id, a, atk)]


def legal_actions(state: GameState, player_id: str = "self", observation=None) -> list[Action]:
    if observation is not None:
        pass  # TODO: public-observation-safe search action generation
    if getattr(state, "is_terminal", False) or player_id not in state.players or state.active_player != player_id:
        return []
    if state.global_effects.get("pending_choice"):
        return []
    actions = []
    for fn in (legal_set_active_from_hand_actions, legal_bench_basic_actions, legal_attach_energy_actions, legal_trainer_actions, legal_retreat_actions, legal_pokemon_power_actions, legal_attack_actions):
        actions.extend(fn(state, player_id))
    actions.append(Action(kind=ActionKind.END_TURN, actor_player_id=player_id))
    return actions
