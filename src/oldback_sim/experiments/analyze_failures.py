from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success

FAILURE_LABELS = [f"F{i}" for i in range(1, 13)] + ["F99"]


@dataclass
class GameSummary:
    game_id: int
    hard_success: bool
    soft_score: int
    primary_failure_reason: str | None
    all_failure_reasons: list[str]
    pre_failure_snapshot: dict[str, Any]


def _normalize_failure_reason(reason: Any) -> str:
    s = str(reason or "F99").strip().upper()
    return s if s in FAILURE_LABELS else "F99"


def _extract_failure_reasons(rec: dict[str, Any]) -> tuple[str | None, list[str], int | None]:
    primary = rec.get("primary_failure_reason")
    if primary is not None:
        primary = _normalize_failure_reason(primary)

    raw = rec.get("all_failure_reasons", [])
    if isinstance(raw, str):
        raw = [raw]
    all_reasons = sorted({_normalize_failure_reason(r) for r in raw})

    first_failure_idx = None
    for ev in rec.get("events", []):
        if ev.get("kind") == "failure_reason":
            rr = _normalize_failure_reason(ev.get("payload", {}).get("reason"))
            if rr not in all_reasons:
                all_reasons.append(rr)
            if primary is None:
                primary = rr
            first_failure_idx = ev.get("idx")
            break

    if primary is None and all_reasons:
        primary = all_reasons[0]

    return primary, sorted(set(all_reasons)), first_failure_idx


def _snapshot_from_event_context(event: dict[str, Any]) -> dict[str, Any]:
    p = event.get("payload", {})
    return {
        "hand": p.get("hand_summary") or p.get("hand"),
        "board": p.get("board_summary") or {"active": p.get("active"), "bench": p.get("bench")},
        "trash": p.get("trash_summary") or p.get("discard"),
    }


def _extract_pre_failure_snapshot(rec: dict[str, Any], first_failure_idx: int | None) -> dict[str, Any]:
    events = rec.get("events", [])
    if first_failure_idx is not None:
        prev = [e for e in events if e.get("idx", -1) <= first_failure_idx]
    else:
        prev = events

    for ev in reversed(prev):
        if ev.get("kind") in {"state_snapshot", "decision_point", "action"}:
            snap = _snapshot_from_event_context(ev)
            if any(v is not None for v in snap.values()):
                return snap
    return {"hand": None, "board": None, "trash": None}


def analyze(path: Path) -> dict[str, Any]:
    summaries: list[GameSummary] = []
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            rec = json.loads(line)
            game_id = int(rec.get("game_id", rec.get("trial", i)))
            hard_success = bool(rec.get("hard_success", False))
            soft_score = int(rec.get("soft_score", 0))
            primary, all_reasons, first_failure_idx = _extract_failure_reasons(rec)
            if (not hard_success) and not all_reasons:
                all_reasons = ["F99"]
                primary = primary or "F99"
            summaries.append(
                GameSummary(
                    game_id=game_id,
                    hard_success=hard_success,
                    soft_score=soft_score,
                    primary_failure_reason=primary,
                    all_failure_reasons=all_reasons,
                    pre_failure_snapshot=_extract_pre_failure_snapshot(rec, first_failure_idx),
                )
            )

    n = max(1, len(summaries))
    success_count = sum(int(s.hard_success) for s in summaries)
    soft_condition_rate = sum(int(s.soft_score > 0) for s in summaries) / n

    primary_counts = Counter(s.primary_failure_reason for s in summaries if not s.hard_success and s.primary_failure_reason)
    all_counts = Counter()
    for s in summaries:
        if s.hard_success:
            continue
        all_counts.update(s.all_failure_reasons)

    representative = defaultdict(list)
    for s in summaries:
        if s.hard_success:
            continue
        for r in s.all_failure_reasons:
            if len(representative[r]) < 3:
                representative[r].append({
                    "game_id": s.game_id,
                    "pre_failure_snapshot": s.pre_failure_snapshot,
                })

    return {
        "games": len(summaries),
        "success_rate": success_count / n,
        "soft_condition_rate": soft_condition_rate,
        "primary_failure_reason": {
            k: {"count": v, "rate": v / n} for k, v in sorted(primary_counts.items())
        },
        "all_failure_reasons": {
            k: {"count": v, "rate": v / n} for k, v in sorted(all_counts.items())
        },
        "representative_failures": dict(representative),
    }


def _write_csv(summary: dict[str, Any], csv_path: Path) -> None:
    rows = []
    for label in FAILURE_LABELS:
        p = summary["primary_failure_reason"].get(label, {"count": 0, "rate": 0.0})
        a = summary["all_failure_reasons"].get(label, {"count": 0, "rate": 0.0})
        rows.append({
            "failure_reason": label,
            "primary_count": p["count"],
            "primary_rate": p["rate"],
            "all_count": a["count"],
            "all_rate": a["rate"],
        })
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--csv")
    args = ap.parse_args()

    summary = analyze(Path(args.log))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if args.csv:
        _write_csv(summary, Path(args.csv))


if __name__ == "__main__":
    main()
