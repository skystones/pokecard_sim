from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim

from oldback_sim.learning.env import RLEnv


class PolicyNet(nn.Module):
    def __init__(self, obs_dim: int, act_dim: int):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(obs_dim, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, act_dim))

    def forward(self, x):
        return self.net(x)


def train(args) -> None:
    env = RLEnv(args.deck, args.opponent_deck)
    obs, _ = env.reset(seed=args.seed)
    obs_dim = int(obs.shape[0])
    _ = env.get_action_mask()
    act_dim = max(1, env.action_encoder.vocab_size())
    model = PolicyNet(obs_dim, act_dim)
    if args.init_model and Path(args.init_model).exists():
        ckpt = torch.load(args.init_model, map_location="cpu")
        if ckpt.get("obs_dim") == obs_dim and ckpt.get("act_dim") == act_dim:
            model.load_state_dict(ckpt["model"])

    opt = optim.Adam(model.parameters(), lr=args.lr)
    logs = []
    hard_success_count = 0
    total_invalid_actions = 0

    for ep in range(args.episodes):
        obs, _ = env.reset(seed=args.seed + ep)
        done = False
        ep_reward = 0.0
        while not done:
            mask = env.get_action_mask()
            x = torch.from_numpy(obs).float().unsqueeze(0)
            logits = model(x).squeeze(0)
            masked_logits = logits + torch.tensor((mask - 1.0) * 1e9, dtype=logits.dtype)
            dist = torch.distributions.Categorical(logits=masked_logits)
            action = dist.sample()
            obs2, reward, terminated, truncated, info = env.step(int(action.item()))
            done = terminated or truncated
            loss = -dist.log_prob(action) * reward
            opt.zero_grad()
            loss.backward()
            opt.step()
            obs = obs2
            ep_reward += reward
        hard_success = bool(info.get("hard_success", False))
        hard_success_count += int(hard_success)
        total_invalid_actions += int(info.get("invalid_action_count", 0))
        logs.append(
            {
                "episode": ep,
                "reward": ep_reward,
                "hard_success": hard_success,
                "invalid_action_count": int(info.get("invalid_action_count", 0)),
            }
        )

    logs.append(
        {
            "summary": True,
            "episodes": args.episodes,
            "hard_success_rate": hard_success_count / max(1, args.episodes),
            "invalid_action_rate_per_episode": total_invalid_actions / max(1, args.episodes),
            "seed": args.seed,
        }
    )

    Path(args.out_model).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "obs_dim": obs_dim, "act_dim": act_dim}, args.out_model)
    Path(args.out_log).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_log).write_text("\n".join(json.dumps(x) for x in logs), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--opponent-deck", required=True)
    ap.add_argument("--episodes", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--out-model", default="artifacts/rl_model.pt")
    ap.add_argument("--out-log", default="artifacts/rl_train_log.jsonl")
    ap.add_argument("--init-model", default="")
    train(ap.parse_args())


if __name__ == "__main__":
    main()
