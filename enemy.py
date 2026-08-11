from dataclasses import dataclass
import random


@dataclass
class Enemy:
    name: str
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    xp: int
    gold: int
    boss: bool = False


def make_enemy(theme, floor, boss=False):
    depth = max(1, floor)

    if boss:
        name = random.choice(theme["bosses"])
        hp = 35 + depth * 7
        attack = 6 + depth // 2
        defense = 3 + depth // 4
        speed = 4 + depth // 8
        xp = 30 + depth * 8
        gold = 15 + depth * 3
    else:
        name = random.choice(theme["enemies"])
        hp = 14 + depth * 4 + random.randint(-3, 5)
        attack = 4 + depth // 3
        defense = 1 + depth // 5
        speed = 3 + depth // 7 + random.randint(0, 2)
        xp = 10 + depth * 4
        gold = random.randint(3, 7) + depth

    return Enemy(
        name=name,
        hp=hp,
        max_hp=hp,
        attack=attack,
        defense=defense,
        speed=speed,
        xp=xp,
        gold=gold,
        boss=boss,
    )
