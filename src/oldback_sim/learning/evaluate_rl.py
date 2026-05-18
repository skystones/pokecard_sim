from __future__ import annotations

import argparse

from oldback_sim.agents.rl_agent import RLAgent, RLAgentConfig
from oldback_sim.engine.observation import build_observation
from oldback_sim.engine.rules import legal_actions
from oldback_sim.engine.rng import RNG
from oldback_sim.engine.setup import init_game_state
from oldback_sim.engine.simulator import Simulator
from oldback_sim.cards.card_registry import load_card_defs, load_deck_list
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--opponent-deck", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--seed", type=int, default=10000)
    args = ap.parse_args()

    defs = load_card_defs("src/oldback_sim/cards/card_defs.yaml")
    self_deck = load_deck_list(args.deck, defs)
    opp_deck = load_deck_list(args.opponent_deck, defs)
    agent = RLAgent(RLAgentConfig(model_path=args.model))

    hard = 0
    for i in range(args.trials):
        s = args.seed + i
        sim = Simulator(init_game_state(self_deck, opp_deck, s), rng=RNG(s))
        for _ in range(200):
            pid = sim.state.active_player
            acts = legal_actions(sim.state, pid)
            if not acts:
                break
            obs = build_observation(sim.state, pid)
            if pid == "self":
                a = agent.choose_action(obs, acts)
            else:
                a = acts[0]
            sim.step(a)
            if sim.state.turn > 2:
                break
        hard += int(evaluate_hard_success(sim.state, sim.log))
    print({"trials": args.trials, "hard_success_rate": hard / max(1, args.trials), "seed": args.seed})


if __name__ == "__main__":
    main()
