from random import randint

MAX_VALUE = 4095
NUM_OF_RANGEFINDERS = 6


def get_values():
    return tuple([randint(0, MAX_VALUE) for _ in range(NUM_OF_RANGEFINDERS)])


def get_values_long():
    for _ in range(5):
        yield tuple([0 for _ in range(NUM_OF_RANGEFINDERS)])
    yield tuple([randint(0, MAX_VALUE) for _ in range(NUM_OF_RANGEFINDERS)])
