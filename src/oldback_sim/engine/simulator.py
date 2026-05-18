from dataclasses import dataclass, field
from oldback_sim.cards.effect_context import EffectContext
from oldback_sim.cards.effects.trainers import apply_trainer_effect
from oldback_sim.engine.actions import Action
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
        if action.kind == "play_trainer":
            self._play_trainer(action)
        self.log.add(kind="action", payload={"kind": action.kind, "card_id": action.card_id}, turn=self.state.turn)
        return self.state

    def _play_trainer(self, action: Action) -> None:
        me = self.state.players[action.actor_player_id]
        trainer = action.card_instance_id
        if trainer is None or trainer not in me.hand:
            raise ValueError("trainer card must be in hand")
        me.hand.remove(trainer)
        ctx = EffectContext(
            state=self.state,
            rng=self.rng,
            event_log=self.log,
            actor_player_id=action.actor_player_id,
            opponent_player_id="opponent" if action.actor_player_id == "self" else "self",
            source_card=trainer,
            targets=dict(action.params or {}),
        )
        apply_trainer_effect(action.card_id or "", ctx)
        me.discard.append(trainer)
