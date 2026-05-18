import random

class RNG:
    def __init__(self, seed: int):
        self.seed = seed
        self._random = random.Random(seed)

    def shuffle(self, values):
        self._random.shuffle(values)

    def choice(self, seq):
        return self._random.choice(seq)
