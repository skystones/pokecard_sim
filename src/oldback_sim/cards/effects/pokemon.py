from __future__ import annotations

from oldback_sim.cards.effect_context import EffectContext


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
            ctx.event_log.add("bench_damage", {"target": t, "amount": water_count * 10}, ctx.state.turn)
        return

    if effect_id == "eneene":
        source = ctx.source_card or me.active
        if not source:
            return
        _knock_out(ctx, ctx.actor_player_id, source)
        if opp.prizes:
            drawn = opp.prizes.pop(0)
            opp.hand.append(drawn)
        attach_target = ctx.targets["attach_target"]
        chosen_type = ctx.targets["energy_type"]
        me.attached_cards.setdefault(attach_target, []).append(f"eneene::{source}::{chosen_type}::2")
        ctx.event_log.add("eneene_attach", {"source": source, "target": attach_target, "energy_type": chosen_type, "energy_value": 2}, ctx.state.turn)
        return

    if effect_id == "great_transform":
        coin = bool(ctx.targets.get("coin_result", False))
        if coin:
            to_card = ctx.targets["transform_to"]
            me.used_flags[f"transform::{ctx.source_card}"] = True
            me.used_flags[f"transform_target::{ctx.source_card}"] = to_card
            ctx.event_log.add("transform_success", {"from": ctx.source_card, "to": to_card}, ctx.state.turn)
        else:
            me.used_flags.pop(f"transform_target::{ctx.source_card}", None)
            ctx.event_log.add("transform_fail", {"from": ctx.source_card}, ctx.state.turn)
        return
