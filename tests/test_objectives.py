from oldback_sim.engine.state import GameState, PlayerState
from oldback_sim.logging_utils.event_log import EventLog
from oldback_sim.objectives.shining_raichu_plan import evaluate_hard_success, evaluate_soft_score


def make_state():
    return GameState(players={
        'self': PlayerState(deck=['full_heal_energy', 'miniskirt'], prizes=[]),
        'opponent': PlayerState(),
    }, turn=2)


def make_good_log():
    log = EventLog()
    log.add('bench_added', {'card_id': 'gastly_expansion_sheet'}, 1)
    log.add('bench_added', {'card_id': 'voltorb_expansion_sheet'}, 1)
    log.add('attack_used', {'attacker': 'gastly_expansion_sheet', 'attack': 'こわがらせる'}, 1)
    log.add('transform_success', {'from': 'ditto_expansion_sheet', 'to': 'electrode_base'}, 2)
    log.add('eneene_attach', {'target': 'shining_raichu', 'energy_value': 2}, 2)
    log.add('transform_success', {'from': 'ditto_expansion_sheet', 'to': 'electrode_base'}, 2)
    log.add('eneene_attach', {'target': 'shining_raichu', 'energy_value': 2}, 2)
    log.add('raichu_complete', {}, 2)
    log.add('trainer_played', {'card_id': 'impostor_professor_oak'}, 2)
    log.add('trainer_played', {'card_id': 'miniskirt'}, 2)
    log.add('attack_used', {'attacker': 'shining_raichu', 'attack': 'サンダースコール'}, 2)
    log.add('energy_attached', {'target': 'shining_raichu', 'card_id': 'water_energy'}, 2)
    log.add('eneene_4th_success', {'water_on_raichu': 6}, 2)
    log.add('transform_success', {'from': 'ditto_expansion_sheet', 'to': 'electrode_base'}, 2)
    log.add('eneene_attach', {'target': 'shining_raichu', 'energy_value': 2}, 2)
    return log


def test_hard_success_true_with_valid_order():
    assert evaluate_hard_success(make_state(), make_good_log()) is True


def test_hard_failure_when_erika_after_impostor_oak():
    log = make_good_log()
    log.add('trainer_played', {'card_id': 'erika'}, 2)
    assert evaluate_hard_success(make_state(), log) is False


def test_hard_failure_when_impostor_before_complete():
    log = make_good_log()
    log = EventLog(events=[e for e in log.events if e.kind != 'raichu_complete'])
    log.add('trainer_played', {'card_id': 'impostor_professor_oak'}, 2)
    log.add('raichu_complete', {}, 2)
    assert evaluate_hard_success(make_state(), log) is False


def test_soft_score_adds_all():
    assert evaluate_soft_score(make_state(), make_good_log()) == 5
