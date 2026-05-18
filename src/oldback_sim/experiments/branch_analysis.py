from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load_record(path: Path, game_id: int) -> dict:
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            rec = json.loads(line)
            gid = int(rec.get("game_id", rec.get("trial", i)))
            if gid == game_id:
                return rec
    raise ValueError(f"game_id={game_id} not found")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--game-id", type=int, required=True)
    ap.add_argument("--step", type=int, required=True)
    ap.add_argument("--action-card", required=True)
    ap.add_argument("--trials", type=int, default=1000)
    args = ap.parse_args()

    rec = _load_record(Path(args.log), args.game_id)
    events = rec.get("events", [])
    # TODO: full replay from event stream including RNG state / side cards / hidden zones.
    # TODO: belief sampling from Observation (not full-state) for human-facing branch advice.
    observed_window = events[max(0, args.step - 3): args.step + 1]

    # MVP: when full state reconstruction data does not exist in log, fallback to empirical estimate from overall game outcome.
    hard = float(bool(rec.get("hard_success", False)))
    soft = float(rec.get("soft_score", 0))
    forced_metrics = {"hard_success_probability": hard, "soft_expected_score": soft}
    forbid_metrics = {"hard_success_probability": 1.0 - hard, "soft_expected_score": max(0.0, soft - 1.0)}

    reasons = Counter(rec.get("all_failure_reasons", []))
    if not reasons and not rec.get("hard_success", False):
        reasons["F99"] += 1

    recommend_force = (
        forced_metrics["hard_success_probability"], forced_metrics["soft_expected_score"]
    ) >= (
        forbid_metrics["hard_success_probability"], forbid_metrics["soft_expected_score"]
    )

    out = {
        "forced_action": args.action_card,
        "forbidden_action": args.action_card,
        "hard_success_probability": {
            "force": forced_metrics["hard_success_probability"],
            "forbid": forbid_metrics["hard_success_probability"],
        },
        "soft_expected_score": {
            "force": forced_metrics["soft_expected_score"],
            "forbid": forbid_metrics["soft_expected_score"],
        },
        "top_failure_reasons": reasons.most_common(3),
        "recommendation": "force" if recommend_force else "forbid",
        "rationale": (
            "MVP推定です。ログに完全状態とRNGスナップショットが無いため、"
            "現状は単一ゲームの実績値から近似。将来は状態復元＋rolloutで置換。"
        ),
        "observation_view": observed_window,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
