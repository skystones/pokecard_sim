from __future__ import annotations

from oldback_sim.cards.effect_context import EffectContext


def apply_energy_effect(effect_id: str, ctx: EffectContext) -> None:
    me = ctx.state.players[ctx.actor_player_id]
    target = ctx.targets.get("attach_target")
    if not target:
        return
    if effect_id == "water_energy":
        me.attached_cards.setdefault(target, []).append("water_energy::water::1")
        ctx.event_log.add("energy_attached", {"target": target, "card_id": "water_energy"}, ctx.state.turn)
    elif effect_id == "full_heal_energy":
        me.attached_cards.setdefault(target, []).append("full_heal_energy::colorless::1")
        ctx.event_log.add("energy_attached", {"target": target, "card_id": "full_heal_energy"}, ctx.state.turn)
