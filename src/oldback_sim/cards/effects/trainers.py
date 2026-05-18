from __future__ import annotations

from oldback_sim.cards.effect_context import EffectContext


def apply_trainer_effect(effect_id: str, ctx: EffectContext) -> None:
    me = ctx.state.players[ctx.actor_player_id]
    opp = ctx.state.players[ctx.opponent_player_id]

    if effect_id == "professor_oak":
        discarded = list(me.hand)
        me.discard.extend(discarded)
        me.hand.clear()
        draw_n = min(7, len(me.deck))
        me.hand.extend(me.deck[:draw_n])
        me.deck = me.deck[draw_n:]
        ctx.event_log.add("trainer_played", {"card_id": "professor_oak", "discarded": discarded, "drawn": draw_n}, ctx.state.turn)
        return

    if effect_id == "imposter_professor_oak":
        cards = list(opp.hand)
        opp.deck.extend(cards)
        ctx.rng.shuffle(opp.deck)
        opp.hand.clear()
        draw_n = min(7, len(opp.deck))
        opp.hand.extend(opp.deck[:draw_n])
        opp.deck = opp.deck[draw_n:]
        ctx.event_log.add("trainer_played", {"card_id": "imposter_professor_oak", "opponent_new_hand": draw_n}, ctx.state.turn)
        return

    if effect_id == "lass":
        def split_trainers(hand):
            t = [c for c in hand if c in {"professor_oak", "bill", "kurumi", "bills_teleporter", "pokemon_scoop_up", "erika", "sabrinas_gaze", "sticky_gas", "miniskirt", "impostor_professor_oak", "team_rocket_announcement", "pokemon_trader", "etiquette", "recycle", "warp_point"}]
            o = [c for c in hand if c not in t]
            return t, o
        my_t, my_o = split_trainers(me.hand)
        op_t, op_o = split_trainers(opp.hand)
        me.hand = my_o
        opp.hand = op_o
        me.deck.extend(my_t); opp.deck.extend(op_t)
        ctx.rng.shuffle(me.deck); ctx.rng.shuffle(opp.deck)
        ctx.event_log.add("trainer_played", {"card_id": "miniskirt", "self_returned": len(my_t), "opp_returned": len(op_t)}, ctx.state.turn)
        return
