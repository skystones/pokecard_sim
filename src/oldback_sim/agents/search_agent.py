from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from oldback_sim.agents.base import Agent
from oldback_sim.agents.heuristic_agent import HeuristicAgent
from oldback_sim.agents.random_agent import RandomAgent
from oldback_sim.engine.actions import Action, ActionKind
from oldback_sim.engine.observation import Observation, build_observation
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.rng import RNG
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, evaluate_soft_score


@dataclass(slots=True)
class SearchAgentConfig:
    num_rollouts_per_action: int = 8
    max_depth: int = 4
    beam_width: int = 3
    epsilon_for_soft_tiebreak: float = 1e-9
    rollout_policy: str = "random"  # random | heuristic
    seed: int = 0


@dataclass(slots=True)
class ActionEvaluation:
    action: Action
    hard_success_probability: float
    soft_expected_score: float
    rollouts: int
    notes: str = ""


class SearchAgent(Agent):
    def __init__(self, config: SearchAgentConfig | None = None):
        self.config = config or SearchAgentConfig()
        self.rng = RNG(self.config.seed)

    def choose_action(self, observation: Observation, legal_actions_in: list[Action]) -> Action:
        _ = observation
        # backward-compatible path for Agent interface
        if not legal_actions_in:
            raise ValueError("legal_actions must not be empty")
        non_end = [a for a in legal_actions_in if a.kind != ActionKind.END_TURN]
        return non_end[0] if non_end else legal_actions_in[0]

    def act(self, observation: Observation, legal_actions_in: list[Action], simulator_factory: Callable[[], object]) -> Action:
        # TODO: belief sampling - determinize unknown deck/prize orders conditioned on observation.
        evals = [self._evaluate_action(a, simulator_factory) for a in legal_actions_in]
        evals.sort(key=lambda e: (e.hard_success_probability, e.soft_expected_score), reverse=True)
        best = evals[0]
        ties = [e for e in evals if abs(e.hard_success_probability - best.hard_success_probability) <= self.config.epsilon_for_soft_tiebreak]
        ties.sort(key=lambda e: e.soft_expected_score, reverse=True)
        chosen = ties[0]

        sim = simulator_factory()
        sim.log.add(
            "search_decision",
            {
                "chosen_action": chosen.action.kind,
                "chosen_card_id": chosen.action.card_id,
                "candidates": [
                    {
                        "action": str(e.action.kind),
                        "card_id": e.action.card_id,
                        "hard_success_probability": e.hard_success_probability,
                        "soft_expected_score": e.soft_expected_score,
                        "rollouts": e.rollouts,
                        "notes": e.notes,
                    }
                    for e in evals
                ],
            },
            sim.state.turn,
        )
        return chosen.action

    def _evaluate_action(self, action: Action, simulator_factory: Callable[[], object]) -> ActionEvaluation:
        hard_hits = 0
        soft_sum = 0.0
        for _ in range(self.config.num_rollouts_per_action):
            sim = simulator_factory()
            sim.step(action)
            self._rollout(sim)
            hard_hits += int(evaluate_hard_success(sim.state, sim.log))
            soft_sum += evaluate_soft_score(sim.state, sim.log)
        n = max(1, self.config.num_rollouts_per_action)
        return ActionEvaluation(action=action, hard_success_probability=hard_hits / n, soft_expected_score=soft_sum / n, rollouts=n, notes=f"policy={self.config.rollout_policy}")

    def _rollout(self, sim: object) -> None:
        for _ in range(self.config.max_depth):
            acts = legal_actions(sim.state, sim.state.active_player)
            if not acts:
                return
            if self.config.rollout_policy == "heuristic":
                chooser = HeuristicAgent()
            else:
                chooser = RandomAgent(self.rng)
            obs = build_observation(sim.state, sim.state.active_player)
            a = chooser.choose_action(obs, acts)
            sim.step(a)
