from abc import ABC, abstractmethod
from oldback_sim.engine.actions import Action
from oldback_sim.engine.observation import Observation

class Agent(ABC):
    @abstractmethod
    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        raise NotImplementedError
