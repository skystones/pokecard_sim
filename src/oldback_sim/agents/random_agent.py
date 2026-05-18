from oldback_sim.agents.base import Agent
from oldback_sim.engine.actions import Action
from oldback_sim.engine.observation import Observation
from oldback_sim.engine.rng import RNG

class RandomAgent(Agent):
    def __init__(self, rng: RNG):
        self.rng = rng

    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        _ = observation
        return self.rng.choice(legal_actions)
