import random
from data import ITEM_DATA


def roll_loot(floor, boss=False):
    if boss:
        choices = [
            "Large Potion",
            "Whetstone",
            "Armor Patch",
            "Vitality Herb",
        ]
        return random.choice(choices), 1

    roll = random.random()

    if roll < 0.35:
        return "Small Potion", 1
    if roll < 0.50:
        return "Bomb", 1
    if roll < 0.60:
        return "Smoke Bomb", 1
    if roll < 0.68:
        return "Whetstone", 1
    if roll < 0.76:
        return "Armor Patch", 1
    if roll < 0.82:
        return "Vitality Herb", 1
    if roll < 0.88 and floor >= 8:
        return "Large Potion", 1

    return None, 0


def item_description(name):
    data = ITEM_DATA.get(name)
    if not data:
        return "Unknown item."
    return data["description"]
