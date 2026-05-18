from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from oldback_sim.experiments.analyze_failures import analyze
from oldback_sim.experiments.run_simulation import main as run_main


def _run_one(deck: str, opponent_deck: str, agent: str, trials: int, seed: int) -> dict:
    with tempfile.TemporaryDirectory() as td:
        log_path = Path(td) / "sim.jsonl"
        import sys

        old = sys.argv
        sys.argv = [
            "run_simulation",
            "--deck", deck,
            "--opponent-deck", opponent_deck,
            "--agent", agent,
            "--trials", str(trials),
            "--seed", str(seed),
            "--log", str(log_path),
        ]
        try:
            run_main()
        finally:
            sys.argv = old

        result = analyze(log_path)
        return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decks", nargs="+", required=True)
    ap.add_argument("--opponent-deck", default="decks/opponent_stub.yaml")
    ap.add_argument("--agent", default="search", choices=["random", "heuristic", "search"])
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--csv")
    args = ap.parse_args()

    rows = []
    for deck in args.decks:
        s = _run_one(deck, args.opponent_deck, args.agent, args.trials, args.seed)
        row = {
            "deck_name": Path(deck).stem,
            "trials": args.trials,
            "t1_frighten_success_rate": 0.0,
            "t1_voltorb_bench_success_rate": 0.0,
            "t1_hard_success_rate": 0.0,
            "t2_hard_success_rate": s["success_rate"],
            "soft_s1_rate": 0.0,
            "soft_s2_rate": 0.0,
            "soft_s3_rate": 0.0,
            "soft_s4_rate": 0.0,
            "mean_soft_score": None,
        }
        for i in range(1, 13):
            key = f"failure_F{i}_rate"
            row[key] = s["all_failure_reasons"].get(f"F{i}", {}).get("rate", 0.0)
        rows.append(row)

    cols = list(rows[0].keys()) if rows else []
    if rows:
        print("\t".join(cols))
        for r in rows:
            print("\t".join(str(r[c]) for c in cols))

    if args.csv and rows:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main()
