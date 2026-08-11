# Static game data. ASCII only.

CLASS_DATA = {
    "warrior": {
        "name": "Warrior",
        "description": "High HP and defense. Heavy single-hit skill.",
        "max_hp": 42,
        "attack": 8,
        "defense": 5,
        "speed": 4,
        "crit": 0.08,
        "evade": 0.04,
        "skill": "Power Strike",
    },
    "ranger": {
        "name": "Ranger",
        "description": "Fast and accurate. Strong critical hits.",
        "max_hp": 32,
        "attack": 7,
        "defense": 3,
        "speed": 8,
        "crit": 0.18,
        "evade": 0.10,
        "skill": "Aimed Shot",
    },
    "wizard": {
        "name": "Wizard",
        "description": "Fragile, but Arcane Blast ignores most defense.",
        "max_hp": 27,
        "attack": 10,
        "defense": 2,
        "speed": 5,
        "crit": 0.10,
        "evade": 0.05,
        "skill": "Arcane Blast",
    },
    "thief": {
        "name": "Thief",
        "description": "Very fast. High evade and burst damage.",
        "max_hp": 30,
        "attack": 7,
        "defense": 3,
        "speed": 10,
        "crit": 0.22,
        "evade": 0.16,
        "skill": "Backstab",
    },
    "monk": {
        "name": "Monk",
        "description": "Balanced fighter. Flurry also restores HP.",
        "max_hp": 36,
        "attack": 7,
        "defense": 4,
        "speed": 7,
        "crit": 0.12,
        "evade": 0.10,
        "skill": "Flurry",
    },
}


THEMES = [
    {
        "id": "cave",
        "name": "Crystal Caves",
        "tagline": "Cold stone, glowing crystals, and things below.",
        "enemies": ["Cave Rat", "Stone Crawler", "Blind Hunter", "Crystal Slime"],
        "bosses": ["Crystal Golem", "Deep Maw"],
    },
    {
        "id": "forest",
        "name": "Twisted Forest",
        "tagline": "Roots crack the floor and branches block the sky.",
        "enemies": ["Thorn Wolf", "Rot Stag", "Sporeling", "Briar Witch"],
        "bosses": ["Ancient Treant", "Thorn Queen"],
    },
    {
        "id": "ruins",
        "name": "Sunken Ruins",
        "tagline": "Broken halls remember a kingdom without a name.",
        "enemies": ["Ruined Guard", "Dust Shade", "Stone Imp", "Lost Squire"],
        "bosses": ["Fallen King", "Iron Colossus"],
    },
    {
        "id": "crypt",
        "name": "Black Crypt",
        "tagline": "The dead do not sleep this high above the earth.",
        "enemies": ["Skeleton", "Grave Hound", "Wraith", "Bone Priest"],
        "bosses": ["Bone Matron", "Crypt Lord"],
    },
    {
        "id": "swamp",
        "name": "Tower Swamp",
        "tagline": "Black water fills halls that should be dry.",
        "enemies": ["Bog Lurker", "Leech Mass", "Mire Witch", "Swamp Ghoul"],
        "bosses": ["Bog Hydra", "Mire Mother"],
    },
    {
        "id": "frost",
        "name": "Frozen Keep",
        "tagline": "Ice grows across doors, armor, and old bones.",
        "enemies": ["Frost Wolf", "Ice Wisp", "Frozen Guard", "Snow Hag"],
        "bosses": ["Ice Giant", "Winter Warden"],
    },
    {
        "id": "inferno",
        "name": "Ash Furnace",
        "tagline": "The tower burns without ever turning to ash.",
        "enemies": ["Ash Hound", "Cinder Imp", "Burned Knight", "Flame Cultist"],
        "bosses": ["Furnace Beast", "Ash Tyrant"],
    },
    {
        "id": "clockwork",
        "name": "Clockwork Halls",
        "tagline": "Gears turn behind the walls with no one to wind them.",
        "enemies": ["Gear Spider", "Brass Soldier", "Spark Drone", "Clock Hound"],
        "bosses": ["Grand Automaton", "Clockwork Warden"],
    },
]


ITEM_DATA = {
    "Small Potion": {
        "type": "heal",
        "value": 18,
        "description": "Restore 18 HP.",
    },
    "Large Potion": {
        "type": "heal",
        "value": 40,
        "description": "Restore 40 HP.",
    },
    "Bomb": {
        "type": "combat",
        "value": 22,
        "description": "Deal heavy damage in combat.",
    },
    "Smoke Bomb": {
        "type": "combat",
        "value": 0,
        "description": "Escape a normal enemy fight.",
    },
    "Whetstone": {
        "type": "upgrade_attack",
        "value": 1,
        "description": "Permanently gain +1 Attack.",
    },
    "Armor Patch": {
        "type": "upgrade_defense",
        "value": 1,
        "description": "Permanently gain +1 Defense.",
    },
    "Vitality Herb": {
        "type": "upgrade_hp",
        "value": 5,
        "description": "Permanently gain +5 Max HP.",
    },
}
