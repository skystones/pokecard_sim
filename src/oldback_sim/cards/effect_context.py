from dataclasses import dataclass

PlayerId = str

@dataclass(slots=True)
class EffectContext:
    player_id: PlayerId
    opponent_player_id: PlayerId
    turn: int
