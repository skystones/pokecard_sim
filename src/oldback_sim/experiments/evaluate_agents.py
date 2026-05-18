from __future__ import annotations

import argparse
import csv
import time
from dataclasses import asdict
from pathlib import Path

from oldback_sim.agents.heuristic_agent import HeuristicAgent
from oldback_sim.agents.random_agent import RandomAgent
from oldback_sim.agents.rl_agent import RLAgent, RLAgentConfig
from oldback_sim.agents.search_agent import SearchAgent, SearchAgentConfig
from oldback_sim.cards.card_registry import load_card_defs, load_deck_list
from oldback_sim.engine.observation import build_observation
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.setup import init_game_state
from oldback_sim.engine.simulator import Simulator
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, evaluate_soft_score, progress_from_log


def make_agent(name: str, seed: int, rl_model: str | None):
    if name == "random": return RandomAgent(RNG(seed))
    if name == "heuristic": return HeuristicAgent()
    if name == "search": return SearchAgent(SearchAgentConfig(seed=seed))
    if name == "rl":
        if not rl_model:
            raise ValueError("RLAgent requested but --rl-model missing")
        return RLAgent(RLAgentConfig(model_path=rl_model))
    raise ValueError(name)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--opponent-deck", required=True)
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--rl-model", default="")
    args = ap.parse_args()

    defs = load_card_defs("src/oldback_sim/cards/card_defs.yaml")
    self_deck = load_deck_list(args.deck, defs)
    opp_deck = load_deck_list(args.opponent_deck, defs)

    rows = []
    for agent_name in ["random", "heuristic", "search", "rl"]:
        t0 = time.time()
        hard = t1h = t2h = soft_sum = ep_len = 0
        soft_each = {"s1": 0, "s2": 0, "s3": 0, "s4": 0}
        fail = {"objective_violation": 0, "incomplete": 0}
        agent = make_agent(agent_name, args.seed, args.rl_model or None)
        for i in range(args.trials):
            s = args.seed + i
            sim = Simulator(init_game_state(self_deck, opp_deck, s), rng=RNG(s))
            steps = 0
            while sim.state.turn <= 2 and steps < 200:
                pid = sim.state.active_player
                acts = legal_actions(sim.state, pid)
                if not acts:
                    break
                obs = build_observation(sim.state, pid)
                a = agent.choose_action(obs, acts) if pid == "self" else acts[0]
                sim.step(a)
                steps += 1
            p = progress_from_log(sim.state, sim.log)
            hs = evaluate_hard_success(sim.state, sim.log)
            hard += int(hs)
            t1h += int(p.t1_h1 and p.t1_h2)
            t2h += int(hs)
            soft_sum += evaluate_soft_score(sim.state, sim.log)
            ep_len += steps
            for k in soft_each:
                soft_each[k] += int(getattr(p, k))
            if not p.t2_h5:
                fail["objective_violation"] += 1
            if not hs:
                fail["incomplete"] += 1
        n = max(1, args.trials)
        row = {
            "agent_name": agent_name,
            "trials": args.trials,
            "hard_success_rate": hard / n,
            "t1_hard_success_rate": t1h / n,
            "t2_hard_success_rate": t2h / n,
            "mean_soft_score": soft_sum / n,
            "failure_reason_rate": fail,
            "average_episode_length": ep_len / n,
            "wall_clock_time": time.time() - t0,
            "seed": args.seed,
            "rl_required": agent_name == "rl",
        }
        row.update({f"soft_{k}_rate": v / n for k, v in soft_each.items()})
        rows.append(row)

    if any(r["agent_name"] == "rl" for r in rows):
        sr = next(r for r in rows if r["agent_name"] == "search")["hard_success_rate"]
        rr = next(r for r in rows if r["agent_name"] == "rl")["hard_success_rate"]
        print({"rl_vs_search_hard_success_delta": rr - sr})

    out = Path(args.out_csv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
