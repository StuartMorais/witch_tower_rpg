import random
from data import THEMES


class Tower:
    def __init__(self, seed):
        self.seed = seed

    def theme_for_floor(self, floor):
        block = (floor - 1) // 5
        rng = random.Random(self.seed + block * 10007)
        index = rng.randrange(len(THEMES))

        if block > 0:
            previous = self._theme_index(block - 1)
            if index == previous:
                index = (index + 1) % len(THEMES)

        return THEMES[index]

    def _theme_index(self, block):
        rng = random.Random(self.seed + block * 10007)
        index = rng.randrange(len(THEMES))
        if block > 0:
            previous = self._theme_index(block - 1)
            if index == previous:
                index = (index + 1) % len(THEMES)
        return index

    def is_boss_floor(self, floor):
        return floor % 5 == 0

    def room_for_floor(self, floor):
        if self.is_boss_floor(floor):
            return "boss"

        rng = random.Random(self.seed + floor * 7919)
        roll = rng.random()

        if roll < 0.55:
            return "enemy"
        if roll < 0.74:
            return "chest"
        if roll < 0.86:
            return "shrine"
        if roll < 0.96:
            return "trap"
        return "cache"
