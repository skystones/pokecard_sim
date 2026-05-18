from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from oldback_sim.learning.train_rl import PolicyNet


def train_bc(dataset_path: str, out_model_path: str, epochs: int = 10, lr: float = 1e-3) -> None:
    xs: list[list[float]] = []
    ys: list[int] = []
    with Path(dataset_path).open("r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            turn = float(r.get("observation", {}).get("turn", 0))
            mask = r.get("action_mask", [])
            if not mask:
                continue
            chosen = r.get("chosen_action")
            if chosen not in mask:
                continue
            xs.append([turn])
            ys.append(mask.index(chosen))

    if not xs:
        raise ValueError("empty dataset")

    x = torch.tensor(xs, dtype=torch.float32)
    y = torch.tensor(ys, dtype=torch.long)
    act_dim = int(max(ys) + 1)
    model = PolicyNet(obs_dim=1, act_dim=act_dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    for _ in range(epochs):
        logits = model(x)
        loss = torch.nn.functional.cross_entropy(logits, y)
        opt.zero_grad()
        loss.backward()
        opt.step()

    Path(out_model_path).parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model": model.state_dict(), "obs_dim": 1, "act_dim": act_dim}, out_model_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=10)
    args = ap.parse_args()
    train_bc(args.dataset, args.out, args.epochs)


if __name__ == "__main__":
    main()
