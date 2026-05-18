from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from oldback_sim.agents.heuristic_agent import HeuristicAgent
from oldback_sim.agents.random_agent import RandomAgent
from oldback_sim.agents.search_agent import SearchAgent, SearchAgentConfig
from oldback_sim.engine.observation import build_observation
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.setup import init_game_state
from oldback_sim.engine.simulator import Simulator
from oldback_sim.cards.card_registry import load_card_defs, load_deck_list
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, evaluate_soft_score, progress_from_log


def _agent(name: str, seed: int):
    if name == "random":
        return RandomAgent(RNG(seed))
    if name == "heuristic":
        return HeuristicAgent()
    if name == "search":
        return SearchAgent(SearchAgentConfig(seed=seed))
    if name == "noop":
        return None
    raise ValueError(f"unknown agent: {name}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--opponent-deck", required=True)
    ap.add_argument("--agent", default="random", choices=["random", "heuristic", "search"])
    ap.add_argument("--opponent-agent", default="noop", choices=["noop", "random", "heuristic"])
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--log", required=True)
    args = ap.parse_args()

    defs = load_card_defs("src/oldback_sim/cards/card_defs.yaml")
    self_deck = load_deck_list(args.deck, defs)
    opp_deck = load_deck_list(args.opponent_deck, defs)

    log_path = Path(args.log)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    t1_scare = t1_voltorb = t1_hard = t2_hard = 0
    soft_counts = {"s1": 0, "s2": 0, "s3": 0, "s4": 0}
    soft_sum = 0

    with log_path.open("w", encoding="utf-8") as f:
        for i in range(args.trials):
            seed = args.seed + i
            state = init_game_state(self_deck, opp_deck, seed)
            sim = Simulator(state=state, rng=RNG(seed))
            me_agent = _agent(args.agent, seed)
            opp_agent = _agent(args.opponent_agent, seed + 10_000)

            steps = 0
            while sim.state.turn <= 2 and steps < 200:
                pid = sim.state.active_player
                acts = legal_actions(sim.state, pid)
                if not acts:
                    break
                obs = build_observation(sim.state, pid)
                agent = me_agent if pid == "self" else opp_agent
                if agent is None:
                    action = next((a for a in acts if str(a.kind).endswith("end_turn")), acts[0])
                elif hasattr(agent, "act"):
                    action = agent.act(obs, acts, simulator_factory=lambda: Simulator(state=init_game_state(self_deck, opp_deck, seed), rng=RNG(seed)))
                    sim.log.add("heuristic_reason", {"agent": type(agent).__name__, "reason": "search evaluation"}, sim.state.turn)
                else:
                    action = agent.choose_action(obs, acts)
                    sim.log.add("heuristic_reason", {"agent": type(agent).__name__, "reason": "priority-based selection"}, sim.state.turn)
                sim.step(action)
                steps += 1

            p = progress_from_log(sim.state, sim.log)
            t1_scare += int(p.t1_h1)
            t1_voltorb += int(p.t1_h2)
            t1_hard += int(p.t1_h1 and p.t1_h2)
            t2_hard += int(evaluate_hard_success(sim.state, sim.log))
            for k in soft_counts:
                soft_counts[k] += int(getattr(p, k))
            soft_sum += evaluate_soft_score(sim.state, sim.log)

            rec = {
                "trial": i,
                "seed": seed,
                "hard_success": evaluate_hard_success(sim.state, sim.log),
                "soft_score": evaluate_soft_score(sim.state, sim.log),
                "progress": asdict(p),
                "events": [asdict(e) for e in sim.log.events],
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    n = max(1, args.trials)
    print(f"trials: {args.trials}")
    print(f"turn1_scare_rate: {t1_scare / n:.4f}")
    print(f"turn1_voltorb_bench_rate: {t1_voltorb / n:.4f}")
    print(f"turn1_hard_rate: {t1_hard / n:.4f}")
    print(f"turn2_hard_completion_rate: {t2_hard / n:.4f}")
    print("soft_condition_rates:", {k: round(v / n, 4) for k, v in soft_counts.items()})
    print(f"average_soft_score: {soft_sum / n:.4f}")
    print(f"seed: {args.seed}")


if __name__ == "__main__":
    main()
