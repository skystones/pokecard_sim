from __future__ import annotations

from oldback_sim.cards.effect_context import EffectContext

TRAINERS = {"professor_oak", "bill", "kurumi", "bills_teleporter", "pokemon_scoop_up", "erika", "sabrinas_gaze", "sticky_gas", "miniskirt", "impostor_professor_oak", "team_rocket_announcement", "pokemon_trader", "etiquette", "recycle", "warp_point"}


def _draw(p, n: int):
    n = min(n, len(p.deck))
    p.hand.extend(p.deck[:n])
    p.deck = p.deck[n:]
    return n


def apply_trainer_effect(effect_id: str, ctx: EffectContext) -> None:
    me = ctx.state.players[ctx.actor_player_id]
    opp = ctx.state.players[ctx.opponent_player_id]

    if effect_id == "professor_oak":
        discarded = list(me.hand); me.discard.extend(discarded); me.hand.clear(); drawn = _draw(me, 7)
        ctx.event_log.add("trainer_played", {"card_id": "professor_oak", "discarded": discarded, "drawn": drawn}, ctx.state.turn); return
    if effect_id == "bill":
        ctx.event_log.add("trainer_played", {"card_id": "bill", "drawn": _draw(me, 2)}, ctx.state.turn); return
    if effect_id == "kurumi":
        _draw(me, 2)
        ret = list(ctx.targets.get("return_cards", me.hand[:2]))[:2]
        for c in ret:
            if c in me.hand: me.hand.remove(c); me.deck.append(c)
        ctx.rng.shuffle(me.deck)
        ctx.event_log.add("trainer_played", {"card_id": "kurumi", "returned": ret}, ctx.state.turn); return
    if effect_id == "bills_teleporter":
        ok = ctx.rng.choice([True, False])
        d = _draw(me, 4) if ok else 0
        ctx.event_log.add("trainer_played", {"card_id": "bills_teleporter", "success": ok, "drawn": d}, ctx.state.turn); return
    if effect_id == "pokemon_scoop_up":
        t = ctx.targets["target"]
        if me.active == t:
            me.active = None
            if me.bench: me.active = me.bench.pop(0)
        elif t in me.bench:
            me.bench.remove(t)
        me.hand.append(t)
        me.discard.extend(me.attached_cards.pop(t, []))
        ctx.event_log.add("trainer_played", {"card_id": "pokemon_scoop_up", "target": t}, ctx.state.turn); return
    if effect_id == "erika":
        s = int(ctx.targets.get("self_draw", 3)); o = int(ctx.targets.get("opp_draw", 3))
        ctx.event_log.add("trainer_played", {"card_id": "erika", "self_drawn": _draw(me, s), "opp_drawn": _draw(opp, o)}, ctx.state.turn); return
    if effect_id == "sabrinas_gaze":
        sh, oh = len(me.hand), len(opp.hand)
        me.deck.extend(me.hand); me.hand.clear(); opp.deck.extend(opp.hand); opp.hand.clear(); ctx.rng.shuffle(me.deck); ctx.rng.shuffle(opp.deck)
        _draw(me, sh); _draw(opp, oh)
        ctx.event_log.add("trainer_played", {"card_id": "sabrinas_gaze", "self": sh, "opp": oh}, ctx.state.turn); return
    if effect_id == "sticky_gas":
        ctx.state.global_effects["goop_gas_active"] = True
        ctx.event_log.add("trainer_played", {"card_id": "sticky_gas"}, ctx.state.turn); return
    if effect_id == "miniskirt":
        my_t, my_o = [c for c in me.hand if c in TRAINERS], [c for c in me.hand if c not in TRAINERS]
        op_t, op_o = [c for c in opp.hand if c in TRAINERS], [c for c in opp.hand if c not in TRAINERS]
        me.hand, opp.hand = my_o, op_o; me.deck.extend(my_t); opp.deck.extend(op_t); ctx.rng.shuffle(me.deck); ctx.rng.shuffle(opp.deck)
        ctx.event_log.add("trainer_played", {"card_id": "miniskirt", "self_returned": len(my_t), "opp_returned": len(op_t)}, ctx.state.turn); return
    if effect_id == "impostor_professor_oak":
        opp.deck.extend(opp.hand); opp.hand.clear(); ctx.rng.shuffle(opp.deck); d = _draw(opp, 7)
        ctx.event_log.add("trainer_played", {"card_id": "impostor_professor_oak", "opponent_new_hand": d}, ctx.state.turn); return
    if effect_id == "team_rocket_announcement":
        me.known_prizes = set(range(len(me.prizes))); opp.known_prizes = set(range(len(opp.prizes)))
        ctx.event_log.add("trainer_played", {"card_id": "team_rocket_announcement"}, ctx.state.turn); return
    if effect_id == "pokemon_trader":
        back = ctx.targets["return_pokemon"]; take = ctx.targets["take_pokemon"]
        if back in me.hand: me.hand.remove(back); me.deck.append(back)
        if take in me.deck: me.deck.remove(take); me.hand.append(take)
        ctx.rng.shuffle(me.deck)
        ctx.event_log.add("trainer_played", {"card_id": "pokemon_trader", "returned": back, "taken": take}, ctx.state.turn); return
    if effect_id == "etiquette":
        take = ctx.targets["take_basic"]
        if take in me.deck: me.deck.remove(take); me.hand.append(take)
        ctx.rng.shuffle(me.deck)
        ctx.event_log.add("trainer_played", {"card_id": "etiquette", "taken": take}, ctx.state.turn); return
    if effect_id == "recycle":
        ok = ctx.rng.choice([True, False])
        card = None
        if ok and me.discard:
            card = ctx.targets.get("target", me.discard[0])
            if card in me.discard: me.discard.remove(card); me.deck.insert(0, card)
        ctx.event_log.add("trainer_played", {"card_id": "recycle", "success": ok, "target": card}, ctx.state.turn); return
    if effect_id == "warp_point":
        if opp.bench:
            i = int(ctx.targets.get("opp_switch_index", 0)); opp.active, opp.bench[i] = opp.bench[i], opp.active
        if me.bench:
            i = int(ctx.targets.get("self_switch_index", 0)); me.active, me.bench[i] = me.bench[i], me.active
        ctx.event_log.add("trainer_played", {"card_id": "warp_point"}, ctx.state.turn); return
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
