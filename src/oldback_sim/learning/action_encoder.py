from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from oldback_sim.engine.actions import Action


@dataclass(slots=True)
class EncodedAction:
    action_id: int
    template: str


class ActionEncoder:
    """Maps variable-length legal action lists to fixed action IDs.

    IDs are built from action templates (`kind|card|ability|attack|target`) and kept stable
    per encoder instance. Unknown IDs decode to `None`.
    """

    def __init__(self) -> None:
        self.template_to_id: dict[str, int] = {}
        self.id_to_template: dict[int, str] = {}

    @staticmethod
    def action_template(action: Action) -> str:
        tgt = getattr(action.target, "pokemon_instance_id", None)
        return "|".join(
            [
                str(action.kind),
                action.card_id or "",
                str(action.params.get("ability_id", "")),
                str(action.params.get("attack_id", "")),
                str(tgt or ""),
            ]
        )

    def ensure_registered(self, actions: Iterable[Action]) -> None:
        for a in actions:
            t = self.action_template(a)
            if t not in self.template_to_id:
                idx = len(self.template_to_id)
                self.template_to_id[t] = idx
                self.id_to_template[idx] = t

    def encode_legal_actions(self, legal_actions: list[Action]) -> tuple[list[int], dict[int, Action]]:
        self.ensure_registered(legal_actions)
        encoded: list[int] = []
        decoder: dict[int, Action] = {}
        for a in legal_actions:
            aid = self.template_to_id[self.action_template(a)]
            encoded.append(aid)
            decoder[aid] = a
        return encoded, decoder

    def make_action_mask(self, legal_actions: list[Action]) -> np.ndarray:
        self.ensure_registered(legal_actions)
        mask = np.zeros(len(self.template_to_id), dtype=np.float32)
        for a in legal_actions:
            mask[self.template_to_id[self.action_template(a)]] = 1.0
        return mask

    def vocab_size(self) -> int:
        return len(self.template_to_id)
