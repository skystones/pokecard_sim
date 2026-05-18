from oldback_sim.engine.rng import RNG


def test_rng_shuffle_reproducibility():
    a = list(range(20))
    b = list(range(20))
    RNG(123).shuffle(a)
    RNG(123).shuffle(b)
    assert a == b
