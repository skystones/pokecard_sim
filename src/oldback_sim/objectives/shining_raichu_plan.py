from dataclasses import dataclass
from oldback_sim.engine.state import GameState
from oldback_sim.logging_utils.event_log import EventLog

@dataclass(slots=True)
class SubgoalProgress:
    t1_h1: bool = False
    t1_h2: bool = False
    t1_h3: bool = False
    t1_hard_bonus: bool = False
    t2_h1: bool = False
    t2_h2: bool = False
    t2_h3: bool = False
    t2_h4: bool = False
    t2_h5: bool = False
    t2_h6: bool = False
    t2_h7: bool = True
    t2_h8: bool = False
    t2_h9: bool = False
    s1: bool = False
    s2: bool = False
    s3: bool = False
    s4: bool = False
    s5: bool = False


def progress_from_log(state: GameState, log: EventLog) -> SubgoalProgress:
    p = SubgoalProgress()
    complete_idx = None
    impostor_idx = None
    miniskirt_after = False
    erika_after = False
    transform_count = 0
    eneene_to_raichu_count = 0

    for ev in log.events:
        k = ev.kind
        pay = ev.payload

        if k == 'bench_added' and ev.turn == 1 and pay.get('card_id') == 'gastly_expansion_sheet':
            p.t1_h1 = True
        if k == 'bench_added' and ev.turn == 1 and pay.get('card_id') == 'voltorb_expansion_sheet':
            p.t1_h2 = True
        if k == 'attack_used' and ev.turn == 1 and pay.get('attacker') == 'gastly_expansion_sheet' and pay.get('attack') == 'こわがらせる':
            p.t1_h3 = True

        if k == 'transform_success' and pay.get('from') == 'ditto_expansion_sheet' and pay.get('to') == 'electrode_base':
            transform_count += 1
            if transform_count >= 1:
                p.t2_h1 = True
            if transform_count >= 2:
                p.t2_h3 = True
            if transform_count >= 3:
                p.s4 = True

        if k == 'eneene_attach' and pay.get('target') == 'shining_raichu' and pay.get('energy_value') == 2:
            eneene_to_raichu_count += 1
            if eneene_to_raichu_count >= 1:
                p.t2_h2 = True
            if eneene_to_raichu_count >= 2:
                p.t2_h4 = True
            if eneene_to_raichu_count >= 3:
                p.s5 = True

        if k == 'raichu_complete':
            p.t2_h5 = True
            complete_idx = ev.idx
        if k == 'trainer_played' and pay.get('card_id') == 'impostor_professor_oak':
            impostor_idx = ev.idx
        if k == 'trainer_played' and pay.get('card_id') == 'erika' and impostor_idx is not None and ev.idx > impostor_idx:
            erika_after = True
        if k == 'trainer_played' and pay.get('card_id') == 'miniskirt' and impostor_idx is not None and ev.idx > impostor_idx:
            miniskirt_after = True
        if k == 'attack_used' and pay.get('attacker') == 'shining_raichu' and pay.get('attack') == 'サンダースコール':
            p.t2_h9 = True
        if k == 'energy_attached' and pay.get('target') == 'shining_raichu' and pay.get('card_id') == 'water_energy':
            p.s1 = True
        if k == 'eneene_4th_success' and pay.get('water_on_raichu', 0) >= 6:
            p.s3 = True

    p.t1_hard_bonus = p.t1_h1 and p.t1_h2 and p.t1_h3
    if complete_idx is not None and impostor_idx is not None and complete_idx < impostor_idx:
        p.t2_h6 = True
    p.t2_h7 = not erika_after
    p.t2_h8 = miniskirt_after

    me = state.players['self']
    p.s2 = ('full_heal_energy' in me.deck) or ('full_heal_energy' in me.prizes) or ('full_heal_energy' in me.hand)
    p.s3 = p.s3 and state.turn >= 2
    p.s3 = p.s3 and (('miniskirt' in me.deck) or ('miniskirt' in me.prizes))
    return p


def evaluate_hard_success(state: GameState, log: EventLog) -> bool:
    p = progress_from_log(state, log)
    return all([
        p.t1_h1, p.t1_h2, p.t1_h3,
        p.t2_h1, p.t2_h2, p.t2_h3, p.t2_h4, p.t2_h5, p.t2_h6, p.t2_h7, p.t2_h8, p.t2_h9,
    ])


def evaluate_soft_score(state: GameState, log: EventLog) -> int:
    p = progress_from_log(state, log)
    return int(p.s1) + int(p.s2) + int(p.s3) + int(p.s4) + int(p.s5)


def compare_scores(a: tuple[float, float], b: tuple[float, float], epsilon: float = 1e-9) -> int:
    if abs(a[0] - b[0]) > epsilon:
        return 1 if a[0] > b[0] else -1
    if abs(a[1] - b[1]) <= epsilon:
        return 0
    return 1 if a[1] > b[1] else -1
