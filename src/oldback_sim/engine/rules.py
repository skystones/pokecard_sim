from oldback_sim.engine.actions import Action
from oldback_sim.engine.state import GameState

def legal_actions(_state: GameState) -> list[Action]:
    return [Action(kind="pass")]
