from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from oldback_sim.engine.observation import Observation


KNOWN_CARDS = [
    "gastly_expansion_sheet",
    "voltorb_expansion_sheet",
    "ditto_expansion_sheet",
    "shining_raichu",
    "rattata_team_rocket",
    "unown_e_pf2",
    "water_energy",
    "full_heal_energy",
    "professor_oak",
    "bill",
    "kurumi",
    "bills_teleporter",
    "pokemon_scoop_up",
    "erika",
    "sabrinas_gaze",
    "sticky_gas",
    "miniskirt",
    "impostor_professor_oak",
    "team_rocket_announcement",
    "pokemon_trader",
    "etiquette",
    "recycle",
    "warp_point",
]


@dataclass(slots=True)
class ObservationEncoder:
    card_to_idx: dict[str, int]

    @classmethod
    def default(cls) -> "ObservationEncoder":
        return cls(card_to_idx={c: i for i, c in enumerate(KNOWN_CARDS)})

    def encode(self, obs: Observation) -> np.ndarray:
        hand_hist = np.zeros(len(self.card_to_idx), dtype=np.float32)
        for c in obs.hand:
            base = c.split("#", 1)[0]
            if base in self.card_to_idx:
                hand_hist[self.card_to_idx[base]] += 1.0

        subgoals = np.array([float(v) for _, v in sorted(obs.subgoal_progress.items())], dtype=np.float32)
        scalars = np.array(
            [
                float(obs.turn),
                float(obs.self_view.deck_count),
                float(obs.self_view.prizes_count),
                float(obs.opponent_view.deck_count),
                float(obs.opponent_view.prizes_count),
                float(len(obs.self_view.bench)),
                float(len(obs.opponent_view.bench)),
            ],
            dtype=np.float32,
        )
        return np.concatenate([scalars, hand_hist, subgoals], axis=0)
