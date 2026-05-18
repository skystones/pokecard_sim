from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch

from oldback_sim.agents.base import Agent
from oldback_sim.engine.actions import Action
from oldback_sim.engine.observation import Observation
from oldback_sim.learning.action_encoder import ActionEncoder
from oldback_sim.learning.observation_encoder import ObservationEncoder
from oldback_sim.learning.train_rl import PolicyNet


@dataclass(slots=True)
class RLAgentConfig:
    model_path: str


class RLAgent(Agent):
    def __init__(self, config: RLAgentConfig, obs_encoder: ObservationEncoder | None = None, action_encoder: ActionEncoder | None = None):
        self.obs_encoder = obs_encoder or ObservationEncoder.default()
        self.action_encoder = action_encoder or ActionEncoder()
        ckpt = torch.load(config.model_path, map_location="cpu")
        self.model = PolicyNet(ckpt["obs_dim"], ckpt["act_dim"])
        self.model.load_state_dict(ckpt["model"])
        self.model.eval()

    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        self.action_encoder.ensure_registered(legal_actions)
        mask = self.action_encoder.make_action_mask(legal_actions)
        x = torch.from_numpy(self.obs_encoder.encode(observation)).float().unsqueeze(0)
        with torch.no_grad():
            logits = self.model(x).squeeze(0).numpy()
        masked = np.where(mask > 0.0, logits, -1e9)
        aid = int(masked.argmax())
        for a in legal_actions:
            if self.action_encoder.template_to_id[self.action_encoder.action_template(a)] == aid:
                return a
        return legal_actions[0]
