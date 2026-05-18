from __future__ import annotations

from oldback_sim.agents.base import Agent
from oldback_sim.engine.actions import Action, ActionKind
from oldback_sim.engine.observation import Observation


class HeuristicAgent(Agent):
    """Simple rule-based policy that prioritizes early combo progress."""

    def choose_action(self, observation: Observation, legal_actions: list[Action]) -> Action:
        if not legal_actions:
            raise ValueError("legal_actions must not be empty")

        # 1) turn1 active Gastly
        a = self._find(legal_actions, ActionKind.SET_ACTIVE_FROM_HAND, card_id="gastly_expansion_sheet")
        if a:
            return a

        # 2) turn1 bench Voltorb
        a = self._find(legal_actions, ActionKind.BENCH_BASIC_FROM_HAND, card_id="voltorb_expansion_sheet")
        if a:
            return a

        # 3) put required basics on board
        for card in ("ditto_expansion_sheet", "shining_raichu", "voltorb_expansion_sheet", "gastly_expansion_sheet"):
            for kind in (ActionKind.SET_ACTIVE_FROM_HAND, ActionKind.BENCH_BASIC_FROM_HAND):
                a = self._find(legal_actions, kind, card_id=card)
                if a:
                    return a

        # 4) draw trainers
        for trainer in ("professor_oak", "bill", "kurumi", "bills_teleporter", "erika"):
            a = self._find(legal_actions, ActionKind.PLAY_TRAINER, card_id=trainer)
            if a:
                return a

        # 5) put shining raichu in play if possible
        for kind in (ActionKind.SET_ACTIVE_FROM_HAND, ActionKind.BENCH_BASIC_FROM_HAND):
            a = self._find(legal_actions, kind, card_id="shining_raichu")
            if a:
                return a

        # 6/7) prepare Ditto and use Great Transform
        a = self._find(legal_actions, ActionKind.USE_POKEMON_POWER, ability_id="great_transform")
        if a:
            return a

        # 8) eneene towards shining raichu
        a = self._find(legal_actions, ActionKind.USE_POKEMON_POWER, ability_id="eneene", target_contains="shining_raichu")
        if a:
            return a

        # 9-11) trainer ordering then attack
        for trainer in ("impostor_professor_oak", "miniskirt"):
            a = self._find(legal_actions, ActionKind.PLAY_TRAINER, card_id=trainer)
            if a:
                return a

        a = self._find(legal_actions, ActionKind.USE_ATTACK, attack_id="thundersquall")
        if a:
            return a

        # attach useful energy before ending
        a = self._find(legal_actions, ActionKind.ATTACH_ENERGY, card_id="water_energy", target_contains="shining_raichu")
        if a:
            return a

        # fallback: avoid immediate end_turn if there are actions
        non_end = [x for x in legal_actions if x.kind != ActionKind.END_TURN]
        return non_end[0] if non_end else legal_actions[0]

    @staticmethod
    def _find(actions: list[Action], kind: ActionKind, card_id: str | None = None, ability_id: str | None = None, attack_id: str | None = None, target_contains: str | None = None) -> Action | None:
        for a in actions:
            if a.kind != kind:
                continue
            if card_id is not None and a.card_id != card_id:
                continue
            if ability_id is not None and a.params.get("ability_id") != ability_id:
                continue
            if attack_id is not None and a.params.get("attack_id") != attack_id:
                continue
            if target_contains is not None:
                tgt = getattr(a.target, "pokemon_instance_id", None)
                if not isinstance(tgt, str) or target_contains not in tgt:
                    continue
            return a
        return None
