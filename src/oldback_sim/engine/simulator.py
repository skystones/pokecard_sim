from __future__ import annotations

from dataclasses import dataclass, field

from oldback_sim.cards.effect_context import EffectContext
from oldback_sim.cards.effects.energy import apply_energy_effect
from oldback_sim.cards.effects.pokemon import apply_pokemon_effect
from oldback_sim.cards.effects.trainers import apply_trainer_effect
from oldback_sim.engine.actions import Action, ActionKind
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.state import GameState
from oldback_sim.logging_utils.event_log import EventLog


@dataclass
class Simulator:
    state: GameState
    log: EventLog = field(default_factory=EventLog)
    rng: RNG = field(default_factory=lambda: RNG(0))

    def step(self, action: Action) -> GameState:
        legal = legal_actions(self.state, self.state.active_player)
        if action not in legal:
            raise ValueError("illegal action")
        if action.kind == ActionKind.PLAY_TRAINER:
            self._play_trainer(action)
        elif action.kind == ActionKind.SET_ACTIVE_FROM_HAND:
            self._set_active(action)
        elif action.kind == ActionKind.BENCH_BASIC_FROM_HAND:
            self._bench(action)
        elif action.kind == ActionKind.ATTACH_ENERGY:
            self._attach_energy(action)
        elif action.kind == ActionKind.USE_POKEMON_POWER:
            self._use_pokemon_power(action)
        elif action.kind == ActionKind.USE_ATTACK:
            self._use_attack(action)
        elif action.kind == ActionKind.END_TURN:
            self._end_turn()
        self.log.add(kind="action", payload={"kind": str(action.kind), "card_id": action.card_id}, turn=self.state.turn)
        return self.state

    def _ctx(self, action: Action, source: str | None, targets: dict) -> EffectContext:
        return EffectContext(
            state=self.state,
            rng=self.rng,
            event_log=self.log,
            actor_player_id=action.actor_player_id,
            opponent_player_id="opponent" if action.actor_player_id == "self" else "self",
            source_card=source,
            targets=targets,
        )

    def _set_active(self, action: Action) -> None:
        me = self.state.players[action.actor_player_id]
        c = action.card_instance_id
        if c is None or c not in me.hand:
            raise ValueError("active card must be in hand")
        me.hand.remove(c)
        me.active = c

    def _bench(self, action: Action) -> None:
        me = self.state.players[action.actor_player_id]
        c = action.card_instance_id
        if c is None or c not in me.hand:
            raise ValueError("bench card must be in hand")
        me.hand.remove(c)
        me.bench.append(c)
        self.log.add("bench_added", {"card_id": action.card_id}, self.state.turn)

    def _attach_energy(self, action: Action) -> None:
        me = self.state.players[action.actor_player_id]
        c = action.card_instance_id
        if c is None or c not in me.hand:
            raise ValueError("energy must be in hand")
        me.hand.remove(c)
        tgt = getattr(action.target, "pokemon_instance_id", None)
        apply_energy_effect(action.card_id or "", self._ctx(action, c, {"attach_target": tgt}))
        me.used_flags["used_manual_energy_attachment_this_turn"] = True

    def _play_trainer(self, action: Action) -> None:
        me = self.state.players[action.actor_player_id]
        trainer = action.card_instance_id
        if trainer is None or trainer not in me.hand:
            raise ValueError("trainer card must be in hand")
        me.hand.remove(trainer)
        params = dict(action.params or {})
        me = self.state.players[action.actor_player_id]
        if action.card_id == "pokemon_scoop_up":
            params.setdefault("target", me.active or (me.bench[0] if me.bench else None))
        elif action.card_id == "pokemon_trader":
            hand_basics = [c for c in me.hand if c.split("#",1)[0] in {"gastly_expansion_sheet","voltorb_expansion_sheet","ditto_expansion_sheet","rattata_team_rocket","unown_e_pf2","shining_raichu"}]
            deck_basics = [c for c in me.deck if c.split("#",1)[0] in {"gastly_expansion_sheet","voltorb_expansion_sheet","ditto_expansion_sheet","rattata_team_rocket","unown_e_pf2","shining_raichu"}]
            if hand_basics and deck_basics:
                params.setdefault("return_pokemon", hand_basics[0])
                params.setdefault("take_pokemon", deck_basics[0])
        elif action.card_id == "etiquette":
            deck_basics = [c for c in me.deck if c.split("#",1)[0] in {"gastly_expansion_sheet","voltorb_expansion_sheet","ditto_expansion_sheet","rattata_team_rocket","unown_e_pf2","shining_raichu"}]
            if deck_basics:
                params.setdefault("take_basic", deck_basics[0])
        elif action.card_id == "recycle":
            if me.discard:
                params.setdefault("target", me.discard[0])
        apply_trainer_effect(action.card_id or "", self._ctx(action, trainer, params))
        me.discard.append(trainer)

    def _use_pokemon_power(self, action: Action) -> None:
        params = dict(action.params or {})
        tgt = getattr(action.target, "pokemon_instance_id", None)
        if action.params.get("ability_id") == "engage":
            # Simulation policy: opponent never chooses ENGAGE redraw.
            params["opp_return_hand"] = False
        if tgt and "attach_target" not in params:
            params["attach_target"] = tgt
        if action.params.get("ability_id") == "great_transform" and tgt:
            params.setdefault("transform_to", tgt.split("#", 1)[0])
        apply_pokemon_effect(action.params.get("ability_id", ""), self._ctx(action, action.card_instance_id, params))

    def _use_attack(self, action: Action) -> None:
        attack = action.params.get("attack_id")
        mapping = {"scare": "scare", "thundersquall": "thunder_squall", "tackle": "bite"}
        apply_pokemon_effect(mapping.get(attack, ""), self._ctx(action, action.card_instance_id, dict(action.params or {})))
        me = self.state.players[action.actor_player_id]
        me.used_flags["attack_used_this_turn"] = True

    def _end_turn(self) -> None:
        cur = self.state.active_player
        self.state.active_player = "opponent" if cur == "self" else "self"
        # Draw 1 card at the start of the next player's turn.
        next_player = self.state.players[self.state.active_player]
        if next_player.deck:
            next_player.hand.append(next_player.deck.pop(0))
        if self.state.active_player == "self":
            self.state.turn += 1
        for p in self.state.players.values():
            p.used_flags.pop("used_manual_energy_attachment_this_turn", None)
            p.used_flags.pop("attack_used_this_turn", None)
            p.trainer_lock_until_end_of_turn = False
