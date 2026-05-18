from oldback_sim.cards.effects.pokemon import apply_pokemon_effect
from oldback_sim.cards.effects.trainers import apply_trainer_effect
from oldback_sim.cards.effects.energy import apply_energy_effect

ENERGY_COLORS = {"grass", "fire", "water", "lightning", "psychic", "fighting", "darkness", "metal"}


def count_effective_energy(attached_cards: list[str], energy_type: str) -> int:
    total = 0
    for token in attached_cards:
        parts = token.split("::")
        if len(parts) < 3:
            continue
        if parts[0] == "eneene":
            chosen = parts[2]
            amount = int(parts[3])
            if chosen == energy_type:
                total += amount
        elif parts[0] == "water_energy" and energy_type == "water":
            total += 1
    return total
