from __future__ import annotations

from dataclasses import asdict

import numpy as np

from oldback_sim.cards.card_registry import load_card_defs, load_deck_list
from oldback_sim.engine.observation import build_observation
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.setup import init_game_state
from oldback_sim.engine.simulator import Simulator
from oldback_sim.learning.action_encoder import ActionEncoder
from oldback_sim.learning.observation_encoder import ObservationEncoder
from oldback_sim.learning.reward import RewardFunction
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, progress_from_log


class RLEnv:
    def __init__(self, deck_path: str, opponent_deck_path: str, card_defs_path: str = "src/oldback_sim/cards/card_defs.yaml", max_steps: int = 200):
        defs = load_card_defs(card_defs_path)
        self.self_deck = load_deck_list(deck_path, defs)
        self.opp_deck = load_deck_list(opponent_deck_path, defs)
        self.max_steps = max_steps
        self.obs_encoder = ObservationEncoder.default()
        self.action_encoder = ActionEncoder()
        self.reward_fn = RewardFunction()
        self.seed = 0
        self.sim: Simulator | None = None
        self.steps = 0
        self._decoder: dict[int, object] = {}

    def reset(self, seed: int | None = None):
        self.seed = self.seed if seed is None else seed
        state = init_game_state(self.self_deck, self.opp_deck, self.seed)
        self.sim = Simulator(state=state, rng=RNG(self.seed))
        self.steps = 0
        obs = build_observation(self.sim.state, "self", asdict(progress_from_log(self.sim.state, self.sim.log)))
        return self.encode_observation(obs), {"seed": self.seed}

    def get_action_mask(self) -> np.ndarray:
        assert self.sim is not None
        legal = legal_actions(self.sim.state, "self") if self.sim.state.active_player == "self" else []
        _, self._decoder = self.action_encoder.encode_legal_actions(legal)
        return self.action_encoder.make_action_mask(legal)

    def decode_action(self, action_id: int):
        return self._decoder.get(action_id)

    def encode_observation(self, observation):
        return self.obs_encoder.encode(observation)

    def _opponent_policy(self):
        legal = legal_actions(self.sim.state, "opponent")
        if not legal:
            return None
        return legal[0]

    def step(self, action_id: int):
        assert self.sim is not None
        self.steps += 1
        prev = progress_from_log(self.sim.state, self.sim.log)
        action = self.decode_action(action_id)
        if action is None:
            obs = build_observation(self.sim.state, "self", asdict(prev))
            return self.encode_observation(obs), self.reward_fn.cfg.illegal_action, True, False, {"illegal_action": True}

        self.sim.step(action)
        while self.sim.state.active_player != "self" and self.steps < self.max_steps:
            opp_action = self._opponent_policy()
            if opp_action is None:
                break
            self.sim.step(opp_action)

        cur = progress_from_log(self.sim.state, self.sim.log)
        terminated = self.steps >= self.max_steps or self.sim.state.turn > 2
        truncated = self.steps >= self.max_steps
        reward = self.reward_fn.dense_from_progress_delta(prev, cur)
        hard = evaluate_hard_success(self.sim.state, self.sim.log)
        if terminated:
            reward += self.reward_fn.terminal_bonus(hard)

        obs = build_observation(self.sim.state, "self", asdict(cur))
        info = {"hard_success": hard, "soft_score": int(cur.s1) + int(cur.s2) + int(cur.s3) + int(cur.s4), "event_count": len(self.sim.log.events)}
        return self.encode_observation(obs), reward, terminated, truncated, info
