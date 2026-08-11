from pathlib import Path

ART_DIR = Path(__file__).resolve().parent / "art"

def load_art(name):
    path = ART_DIR / f"{name}.txt"
    if not path.exists():
        return ""
    return path.read_text(encoding="ascii").rstrip("\n")


ITEM_ART_MAP = {
    "Small Potion": "items/small_potion",
    "Large Potion": "items/large_potion",
    "Bomb": "items/bomb",
    "Smoke Bomb": "items/smoke_bomb",
    "Whetstone": "items/whetstone",
    "Armor Patch": "items/armor_patch",
    "Vitality Herb": "items/vitality_herb",
    "Chest": "chest",
}


def item_art_name(item_name):
    return ITEM_ART_MAP.get(item_name)


def load_item_art(item_name):
    key = item_art_name(item_name)
    if not key:
        return ""
    return load_art(key)
