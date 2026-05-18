from dataclasses import dataclass, field
from oldback_sim.engine.actions import Action
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.state import GameState
from oldback_sim.logging_utils.event_log import EventLog

@dataclass
class Simulator:
    state: GameState
    log: EventLog = field(default_factory=EventLog)

    def step(self, action: Action) -> GameState:
        if action.kind not in {a.kind for a in legal_actions(self.state)}:
            raise ValueError("illegal action")
        self.log.add(kind="action", payload={"kind": action.kind, "card_id": action.card_id}, turn=self.state.turn)
        return self.state
