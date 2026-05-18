from __future__ import annotations

import json
from pathlib import Path


def build_dataset_from_jsonl(log_path: str, out_path: str) -> int:
    rows = []
    with Path(log_path).open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            events = rec.get("events", [])
            for ev in events:
                if ev.get("kind") != "search_decision":
                    continue
                p = ev.get("payload", {})
                chosen = p.get("chosen_action")
                candidates = p.get("candidates", [])
                rows.append(
                    {
                        "observation": {"turn": ev.get("turn", 0)},
                        "chosen_action": chosen,
                        "action_mask": [c.get("action") for c in candidates],
                        "action_value": {c.get("action"): c.get("hard_success_probability", 0.0) for c in candidates},
                    }
                )
    with Path(out_path).open("w", encoding="utf-8") as o:
        for r in rows:
            o.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(rows)
