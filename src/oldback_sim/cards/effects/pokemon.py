from __future__ import annotations

from oldback_sim.cards.effect_context import EffectContext


ENERGY_COLORS = {"grass", "fire", "water", "lightning", "psychic", "fighting", "darkness", "metal"}


def _coin(ctx: EffectContext, label: str) -> bool:
    v = ctx.rng.choice([True, False])
    ctx.event_log.add("coin_flip", {"label": label, "heads": v}, ctx.state.turn)
    return v


def _find_in_play(player_state, instance_id: str):
    if player_state.active == instance_id:
        return "active"
    for i, c in enumerate(player_state.bench):
        if c == instance_id:
            return ("bench", i)
    return None


def _knock_out(ctx: EffectContext, player_id: str, instance_id: str):
    p = ctx.state.players[player_id]
    loc = _find_in_play(p, instance_id)
    if loc == "active":
        p.active = None
    elif isinstance(loc, tuple):
        _, idx = loc
        p.bench.pop(idx)
    p.discard.append(instance_id)


def apply_pokemon_effect(effect_id: str, ctx: EffectContext) -> None:
    me = ctx.state.players[ctx.actor_player_id]
    opp = ctx.state.players[ctx.opponent_player_id]

    if effect_id == "thunder_squall":
        ctx.event_log.add("attack_used", {"attacker": me.active, "attack": "サンダースコール"}, ctx.state.turn)
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 40}, ctx.state.turn)
        if opp.bench:
            t = ctx.targets.get("opponent_bench_target", opp.bench[0])
            water_count = int(ctx.targets.get("water_energy_count", 0))
            ctx.event_log.add("bench_damage", {"target": t, "amount": water_count * 10, "ignore_wr": True}, ctx.state.turn)
        return

    if effect_id == "lightning_slash":
        heads = _coin(ctx, "lightning_slash")
        base = 40 if heads else 30
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": base}, ctx.state.turn)
        if heads:
            for b in opp.bench:
                ctx.event_log.add("bench_damage", {"target": b, "amount": 10, "ignore_wr": True}, ctx.state.turn)
        else:
            if me.active:
                ctx.event_log.add("self_damage", {"target": me.active, "amount": 10, "ignore_wr": True}, ctx.state.turn)
        return

    if effect_id == "water_slash":
        bonus = int(ctx.targets.get("extra_water", 0)) * 10
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 50 + bonus, "ignore_resistance": True}, ctx.state.turn)
        return

    if effect_id == "great_transform":
        coin = bool(ctx.targets.get("coin_result", _coin(ctx, "great_transform")))
        if coin:
            me.used_flags[f"transform::{ctx.source_card}"] = True
            me.used_flags[f"transform_target::{ctx.source_card}"] = str(ctx.targets.get("transform_to", ""))
            ctx.event_log.add("transform_success", {"from": ctx.source_card, "to": ctx.targets.get("transform_to")}, ctx.state.turn)
        else:
            me.used_flags.pop(f"transform_target::{ctx.source_card}", None)
            ctx.event_log.add("transform_fail", {"from": ctx.source_card}, ctx.state.turn)
        return

    if effect_id == "eneene":
        source = ctx.source_card or me.active
        if not source:
            return
        _knock_out(ctx, ctx.actor_player_id, source)
        if opp.prizes:
            opp.hand.append(opp.prizes.pop(0))
        attach_target = ctx.targets["attach_target"]
        chosen_type = ctx.targets["energy_type"]
        if chosen_type not in ENERGY_COLORS:
            raise ValueError("invalid eneene color")
            drawn = opp.prizes.pop(0)
            opp.hand.append(drawn)
        attach_target = ctx.targets["attach_target"]
        chosen_type = ctx.targets["energy_type"]
        me.attached_cards.setdefault(attach_target, []).append(f"eneene::{source}::{chosen_type}::2")
        ctx.event_log.add("eneene_attach", {"source": source, "target": attach_target, "energy_type": chosen_type, "energy_value": 2}, ctx.state.turn)
        return

    if effect_id == "electric_shock":
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 10}, ctx.state.turn)
        if _coin(ctx, "electric_shock") and opp.active:
            ctx.event_log.add("special_condition", {"target": opp.active, "condition": "paralyzed"}, ctx.state.turn)
        return

    if effect_id == "group_spark":
        count = sum(1 for c in [me.active, *me.bench, opp.active, *opp.bench] if c and "voltorb" in c)
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 20 + 10 * count}, ctx.state.turn)
        return

    if effect_id == "mischief":
        if not me.deck or not me.prizes:
            return
        idx = int(ctx.targets.get("prize_index", 0))
        me.prizes[idx], me.deck[0] = me.deck[0], me.prizes[idx]
        me.known_prize_slots.pop(idx, None)
        me.known_prizes = {i for i in me.known_prize_slots if 0 <= i < len(me.prizes)}
        ctx.event_log.add("prize_swap", {"prize_index": idx, "new_deck_top": me.deck[0]}, ctx.state.turn)
        return

    if effect_id == "bite":
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 20}, ctx.state.turn)
        return

    if effect_id == "engage":
        if bool(ctx.targets.get("self_return_hand", False)):
            returned = len(me.hand)
            me.deck.extend(me.hand); me.hand.clear(); ctx.rng.shuffle(me.deck)
            n = min(4, len(me.deck)); me.hand.extend(me.deck[:n]); me.deck = me.deck[n:]
            ctx.event_log.add("engage_draw", {"player": ctx.actor_player_id, "returned": returned, "drawn": n}, ctx.state.turn)
        if bool(ctx.targets.get("opp_return_hand", False)):
            returned = len(opp.hand)
            opp.deck.extend(opp.hand); opp.hand.clear(); ctx.rng.shuffle(opp.deck)
            n = min(4, len(opp.deck)); opp.hand.extend(opp.deck[:n]); opp.deck = opp.deck[n:]
            ctx.event_log.add("engage_draw", {"player": ctx.opponent_player_id, "returned": returned, "drawn": n}, ctx.state.turn)
        return

    if effect_id == "hidden_power":
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 10}, ctx.state.turn)
        return

    if effect_id == "scare":
        opp.trainer_lock_until_end_of_turn = True
        ctx.event_log.add("trainer_lock", {"target": ctx.opponent_player_id}, ctx.state.turn)
        return

    if effect_id == "darkness":
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 10}, ctx.state.turn)
        if _coin(ctx, "darkness") and opp.active:
            ctx.event_log.add("special_condition", {"target": opp.active, "condition": "confused"}, ctx.state.turn)
        return

    if effect_id == "electricity":
        if opp.active:
            ctx.event_log.add("damage", {"target": opp.active, "amount": 50}, ctx.state.turn)
        if not _coin(ctx, "electricity") and me.active:
            ctx.event_log.add("self_damage", {"target": me.active, "amount": 10}, ctx.state.turn)
        return
