from __future__ import annotations

from dataclasses import dataclass

from oldback_sim.objectives.shining_raichu_plan import SubgoalProgress


@dataclass(slots=True)
class RewardConfig:
    hard_success: float = 80.0
    t1_h1: float = 5.0
    t1_h2: float = 3.0
    t1_h3: float = 2.0
    t1_hard_bonus: float = 5.0
    t2_h1: float = 4.0
    t2_h2: float = 4.0
    t2_h3: float = 4.0
    t2_h4: float = 4.0
    t2_h5: float = 5.0
    t2_h6: float = 5.0
    t2_h8: float = 5.0
    t2_h9: float = 1.0
    s1: float = 1.0
    s2: float = 1.0
    s3: float = 1.0
    s4: float = 2.0
    s5: float = 1.0
    objective_violation: float = -40.0
    t1_incomplete_penalty: float = -120.0
    illegal_action: float = -100.0
    step_penalty: float = -0.1


class RewardFunction:
    def __init__(self, cfg: RewardConfig | None = None) -> None:
        self.cfg = cfg or RewardConfig()

    def dense_from_progress_delta(self, prev: SubgoalProgress, cur: SubgoalProgress) -> float:
        r = self.cfg.step_penalty
        for k in ("t1_h1", "t1_h2", "t1_h3", "t1_hard_bonus", "t2_h1", "t2_h2", "t2_h3", "t2_h4", "t2_h5", "t2_h6", "t2_h8", "t2_h9"):
            if not getattr(prev, k) and getattr(cur, k):
                r += getattr(self.cfg, k)
        for k in ("s1", "s2", "s3", "s4", "s5"):
            if not getattr(prev, k) and getattr(cur, k):
                r += getattr(self.cfg, k)
        if prev.t2_h7 and not cur.t2_h7:
            r += self.cfg.objective_violation
        return r

    def terminal_bonus(self, hard_success: bool) -> float:
        return self.cfg.hard_success if hard_success else 0.0
