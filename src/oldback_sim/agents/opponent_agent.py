from abc import ABC, abstractmethod
from oldback_sim.engine.actions import Action
from oldback_sim.engine.observation import Observation

class OpponentAgent(ABC):
    @abstractmethod
    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        raise NotImplementedError

class NoOpOpponentAgent(OpponentAgent):
    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        _ = observation
        return legal_actions[0]
