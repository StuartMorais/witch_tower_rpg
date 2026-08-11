# Class skill trees and combat modifiers.
# Exactly 10 skills per class, arranged across three tiers.

SKILL_TREES = {
    "warrior": [
        {
            "id": "iron_body",
            "name": "Iron Body",
            "tier": 1,
            "max_rank": 3,
            "description": "+6 Max HP per rank.",
            "requires": [],
            "stat": ("max_hp", 6),
        },
        {
            "id": "weapon_mastery",
            "name": "Weapon Mastery",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Attack per rank.",
            "requires": [],
            "stat": ("attack", 1),
        },
        {
            "id": "shield_training",
            "name": "Shield Training",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Defense per rank.",
            "requires": [],
            "stat": ("defense", 1),
        },
        {
            "id": "battle_fury",
            "name": "Battle Fury",
            "tier": 1,
            "max_rank": 2,
            "description": "+4% Critical Chance per rank.",
            "requires": [],
            "stat": ("crit", 0.04),
        },
        {
            "id": "brutal_force",
            "name": "Brutal Force",
            "tier": 2,
            "max_rank": 2,
            "description": "Power Strike deals +18% damage per rank.",
            "requires": [("weapon_mastery", 2)],
        },
        {
            "id": "second_wind",
            "name": "Second Wind",
            "tier": 2,
            "max_rank": 2,
            "description": "Restore 10% Max HP per rank after victory.",
            "requires": [("iron_body", 2)],
        },
        {
            "id": "heavy_hands",
            "name": "Heavy Hands",
            "tier": 2,
            "max_rank": 3,
            "description": "Basic attacks deal +8% damage per rank.",
            "requires": [("weapon_mastery", 1), ("battle_fury", 1)],
        },
        {
            "id": "juggernaut",
            "name": "Juggernaut",
            "tier": 3,
            "max_rank": 1,
            "description": "Take 18% less damage from bosses.",
            "requires": [("shield_training", 2), ("brutal_force", 1)],
        },
        {
            "id": "berserker",
            "name": "Berserker",
            "tier": 3,
            "max_rank": 1,
            "description": "Deal 25% more damage while below 40% HP.",
            "requires": [("battle_fury", 2), ("heavy_hands", 2)],
        },
        {
            "id": "indomitable",
            "name": "Indomitable",
            "tier": 3,
            "max_rank": 1,
            "description": "Take 10% less damage from every attack.",
            "requires": [("iron_body", 3), ("shield_training", 3)],
        },
    ],

    "ranger": [
        {
            "id": "keen_eye",
            "name": "Keen Eye",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Critical Chance per rank.",
            "requires": [],
            "stat": ("crit", 0.03),
        },
        {
            "id": "fleetfoot",
            "name": "Fleetfoot",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Evade Chance per rank.",
            "requires": [],
            "stat": ("evade", 0.03),
        },
        {
            "id": "hunter_training",
            "name": "Hunter Training",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Attack per rank.",
            "requires": [],
            "stat": ("attack", 1),
        },
        {
            "id": "survivalist",
            "name": "Survivalist",
            "tier": 1,
            "max_rank": 3,
            "description": "+5 Max HP per rank.",
            "requires": [],
            "stat": ("max_hp", 5),
        },
        {
            "id": "deadeye",
            "name": "Deadeye",
            "tier": 2,
            "max_rank": 2,
            "description": "Aimed Shot deals +15% damage per rank.",
            "requires": [("keen_eye", 2)],
        },
        {
            "id": "quickdraw",
            "name": "Quickdraw",
            "tier": 2,
            "max_rank": 1,
            "description": "Aimed Shot cooldown is reduced by 1 turn.",
            "requires": [("fleetfoot", 2)],
        },
        {
            "id": "longshot",
            "name": "Longshot",
            "tier": 2,
            "max_rank": 3,
            "description": "Basic attacks deal +7% damage per rank.",
            "requires": [("hunter_training", 2)],
        },
        {
            "id": "predator",
            "name": "Predator",
            "tier": 3,
            "max_rank": 1,
            "description": "Deal 20% more damage to bosses.",
            "requires": [("deadeye", 1), ("hunter_training", 2)],
        },
        {
            "id": "perfect_aim",
            "name": "Perfect Aim",
            "tier": 3,
            "max_rank": 1,
            "description": "Aimed Shot gains +25% critical chance.",
            "requires": [("keen_eye", 3), ("deadeye", 2)],
        },
        {
            "id": "field_medic",
            "name": "Field Medic",
            "tier": 3,
            "max_rank": 1,
            "description": "Restore 10% Max HP after each victory.",
            "requires": [("survivalist", 3), ("fleetfoot", 2)],
        },
    ],

    "wizard": [
        {
            "id": "arcane_power",
            "name": "Arcane Power",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Attack per rank.",
            "requires": [],
            "stat": ("attack", 1),
        },
        {
            "id": "warding",
            "name": "Warding",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Defense per rank.",
            "requires": [],
            "stat": ("defense", 1),
        },
        {
            "id": "vital_spark",
            "name": "Vital Spark",
            "tier": 1,
            "max_rank": 3,
            "description": "+5 Max HP per rank.",
            "requires": [],
            "stat": ("max_hp", 5),
        },
        {
            "id": "arcane_precision",
            "name": "Arcane Precision",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Critical Chance per rank.",
            "requires": [],
            "stat": ("crit", 0.03),
        },
        {
            "id": "overcharge",
            "name": "Overcharge",
            "tier": 2,
            "max_rank": 3,
            "description": "Arcane Blast deals +18% damage per rank.",
            "requires": [("arcane_power", 2)],
        },
        {
            "id": "arcane_flow",
            "name": "Arcane Flow",
            "tier": 2,
            "max_rank": 1,
            "description": "Arcane Blast cooldown is reduced by 1 turn.",
            "requires": [("warding", 2)],
        },
        {
            "id": "mana_shield",
            "name": "Mana Shield",
            "tier": 2,
            "max_rank": 2,
            "description": "Take 6% less damage per rank.",
            "requires": [("warding", 2), ("vital_spark", 1)],
        },
        {
            "id": "spell_echo",
            "name": "Spell Echo",
            "tier": 3,
            "max_rank": 1,
            "description": "22% chance Arcane Blast has no cooldown.",
            "requires": [("overcharge", 1), ("arcane_flow", 1)],
        },
        {
            "id": "glass_cannon",
            "name": "Glass Cannon",
            "tier": 3,
            "max_rank": 1,
            "description": "Deal 18% more damage while above 70% HP.",
            "requires": [("arcane_power", 3), ("arcane_precision", 2)],
        },
        {
            "id": "arcane_recovery",
            "name": "Arcane Recovery",
            "tier": 3,
            "max_rank": 1,
            "description": "Restore 12% Max HP after defeating a boss.",
            "requires": [("vital_spark", 3), ("mana_shield", 2)],
        },
    ],

    "thief": [
        {
            "id": "sharpened_blades",
            "name": "Sharpened Blades",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Attack per rank.",
            "requires": [],
            "stat": ("attack", 1),
        },
        {
            "id": "shadowstep",
            "name": "Shadowstep",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Evade Chance per rank.",
            "requires": [],
            "stat": ("evade", 0.03),
        },
        {
            "id": "killer_instinct",
            "name": "Killer Instinct",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Critical Chance per rank.",
            "requires": [],
            "stat": ("crit", 0.03),
        },
        {
            "id": "light_feet",
            "name": "Light Feet",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Speed per rank.",
            "requires": [],
            "stat": ("speed", 1),
        },
        {
            "id": "deep_cut",
            "name": "Deep Cut",
            "tier": 2,
            "max_rank": 3,
            "description": "Backstab deals +16% damage per rank.",
            "requires": [("sharpened_blades", 2)],
        },
        {
            "id": "vanish",
            "name": "Vanish",
            "tier": 2,
            "max_rank": 1,
            "description": "+8% permanent Evade Chance.",
            "requires": [("shadowstep", 2)],
            "stat": ("evade", 0.08),
        },
        {
            "id": "dirty_fighting",
            "name": "Dirty Fighting",
            "tier": 2,
            "max_rank": 3,
            "description": "Basic attacks deal +8% damage per rank.",
            "requires": [("killer_instinct", 1), ("light_feet", 1)],
        },
        {
            "id": "executioner",
            "name": "Executioner",
            "tier": 3,
            "max_rank": 1,
            "description": "Deal +30% damage to enemies below 35% HP.",
            "requires": [("killer_instinct", 2), ("deep_cut", 1)],
        },
        {
            "id": "assassinate",
            "name": "Assassinate",
            "tier": 3,
            "max_rank": 1,
            "description": "Backstab gains +25% critical chance.",
            "requires": [("deep_cut", 2), ("shadowstep", 2)],
        },
        {
            "id": "escape_artist",
            "name": "Escape Artist",
            "tier": 3,
            "max_rank": 1,
            "description": "Take 15% less damage from normal enemies.",
            "requires": [("vanish", 1), ("light_feet", 3)],
        },
    ],

    "monk": [
        {
            "id": "iron_breath",
            "name": "Iron Breath",
            "tier": 1,
            "max_rank": 3,
            "description": "+5 Max HP per rank.",
            "requires": [],
            "stat": ("max_hp", 5),
        },
        {
            "id": "centered_guard",
            "name": "Centered Guard",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Defense per rank.",
            "requires": [],
            "stat": ("defense", 1),
        },
        {
            "id": "swift_hands",
            "name": "Swift Hands",
            "tier": 1,
            "max_rank": 3,
            "description": "+1 Speed per rank.",
            "requires": [],
            "stat": ("speed", 1),
        },
        {
            "id": "focused_mind",
            "name": "Focused Mind",
            "tier": 1,
            "max_rank": 3,
            "description": "+3% Critical Chance per rank.",
            "requires": [],
            "stat": ("crit", 0.03),
        },
        {
            "id": "flowing_strikes",
            "name": "Flowing Strikes",
            "tier": 2,
            "max_rank": 3,
            "description": "Flurry deals +15% damage per rank.",
            "requires": [("swift_hands", 2)],
        },
        {
            "id": "inner_healing",
            "name": "Inner Healing",
            "tier": 2,
            "max_rank": 3,
            "description": "Flurry heals +6% of damage per rank.",
            "requires": [("iron_breath", 2)],
        },
        {
            "id": "pressure_points",
            "name": "Pressure Points",
            "tier": 2,
            "max_rank": 3,
            "description": "Basic attacks deal +7% damage per rank.",
            "requires": [("focused_mind", 1), ("swift_hands", 1)],
        },
        {
            "id": "serenity",
            "name": "Serenity",
            "tier": 3,
            "max_rank": 1,
            "description": "Take 12% less damage from all attacks.",
            "requires": [("centered_guard", 2), ("inner_healing", 1)],
        },
        {
            "id": "perfect_balance",
            "name": "Perfect Balance",
            "tier": 3,
            "max_rank": 1,
            "description": "+8% permanent Evade Chance.",
            "requires": [("swift_hands", 3), ("centered_guard", 2)],
            "stat": ("evade", 0.08),
        },
        {
            "id": "renewal",
            "name": "Renewal",
            "tier": 3,
            "max_rank": 1,
            "description": "Restore 10% Max HP after each victory.",
            "requires": [("iron_breath", 3), ("inner_healing", 2)],
        },
    ],
}


def tree_for(player):
    return SKILL_TREES[player.class_id]


def get_node(player, skill_id):
    for node in tree_for(player):
        if node["id"] == skill_id:
            return node
    return None


def rank(player, skill_id):
    return player.skill_ranks.get(skill_id, 0)


def requirements_met(player, node):
    for required_id, required_rank in node.get("requires", []):
        if rank(player, required_id) < required_rank:
            return False
    return True


def requirement_text(player, node):
    if not node.get("requires"):
        return "None"

    parts = []
    for skill_id, required_rank in node["requires"]:
        required = get_node(player, skill_id)
        name = required["name"] if required else skill_id
        parts.append(f"{name} {required_rank}")
    return ", ".join(parts)


def status(player, node):
    current = rank(player, node["id"])
    if current >= node["max_rank"]:
        return "MAX"
    if not requirements_met(player, node):
        return "LOCKED"
    if player.skill_points <= 0:
        return "NO POINTS"
    return "OPEN"


def purchase(player, skill_id):
    node = get_node(player, skill_id)
    if not node:
        return False, "Unknown skill."

    current = rank(player, skill_id)
    if current >= node["max_rank"]:
        return False, f"{node['name']} is already at maximum rank."

    if player.skill_points <= 0:
        return False, "You have no skill points to spend."

    if not requirements_met(player, node):
        return False, "Requirements not met: " + requirement_text(player, node)

    player.skill_points -= 1
    player.skill_ranks[skill_id] = current + 1

    stat = node.get("stat")
    if stat:
        attr, amount = stat
        old_max_hp = player.max_hp
        setattr(player, attr, getattr(player, attr) + amount)

        if attr == "max_hp":
            player.hp += player.max_hp - old_max_hp
        elif attr == "crit":
            player.crit = min(0.60, player.crit)
        elif attr == "evade":
            player.evade = min(0.45, player.evade)

    return True, f"Learned {node['name']} rank {current + 1}/{node['max_rank']}."


def basic_attack_multiplier(player, enemy):
    multiplier = 1.0

    if player.class_id == "warrior":
        multiplier *= 1.0 + 0.08 * rank(player, "heavy_hands")
    elif player.class_id == "ranger":
        multiplier *= 1.0 + 0.07 * rank(player, "longshot")
    elif player.class_id == "thief":
        multiplier *= 1.0 + 0.08 * rank(player, "dirty_fighting")
    elif player.class_id == "monk":
        multiplier *= 1.0 + 0.07 * rank(player, "pressure_points")

    return multiplier * outgoing_multiplier(player, enemy)


def skill_damage_multiplier(player):
    if player.class_id == "warrior":
        return 1.0 + 0.18 * rank(player, "brutal_force")
    if player.class_id == "ranger":
        return 1.0 + 0.15 * rank(player, "deadeye")
    if player.class_id == "wizard":
        return 1.0 + 0.18 * rank(player, "overcharge")
    if player.class_id == "thief":
        return 1.0 + 0.16 * rank(player, "deep_cut")
    if player.class_id == "monk":
        return 1.0 + 0.15 * rank(player, "flowing_strikes")
    return 1.0


def outgoing_multiplier(player, enemy):
    multiplier = 1.0

    if player.class_id == "warrior" and rank(player, "berserker"):
        if player.hp <= max(1, int(player.max_hp * 0.40)):
            multiplier *= 1.25

    if player.class_id == "ranger" and enemy.boss and rank(player, "predator"):
        multiplier *= 1.20

    if player.class_id == "wizard" and rank(player, "glass_cannon"):
        if player.hp >= max(1, int(player.max_hp * 0.70)):
            multiplier *= 1.18

    if player.class_id == "thief" and rank(player, "executioner"):
        if enemy.hp <= max(1, int(enemy.max_hp * 0.35)):
            multiplier *= 1.30

    return multiplier


def skill_crit_bonus(player):
    if player.class_id == "ranger" and rank(player, "perfect_aim"):
        return 0.25
    if player.class_id == "thief" and rank(player, "assassinate"):
        return 0.25
    return 0.0


def skill_cooldown(player, base_cooldown):
    reduction = 0
    if player.class_id == "ranger" and rank(player, "quickdraw"):
        reduction = 1
    if player.class_id == "wizard" and rank(player, "arcane_flow"):
        reduction = 1
    return max(1, base_cooldown - reduction)


def incoming_damage(player, enemy, damage):
    multiplier = 1.0

    if player.class_id == "warrior":
        if enemy.boss and rank(player, "juggernaut"):
            multiplier *= 0.82
        if rank(player, "indomitable"):
            multiplier *= 0.90

    if player.class_id == "wizard":
        multiplier *= max(0.65, 1.0 - 0.06 * rank(player, "mana_shield"))

    if player.class_id == "thief":
        if not enemy.boss and rank(player, "escape_artist"):
            multiplier *= 0.85

    if player.class_id == "monk" and rank(player, "serenity"):
        multiplier *= 0.88

    return max(1, int(round(damage * multiplier)))


def victory_heal(player, enemy):
    ratio = 0.0

    if player.class_id == "warrior":
        ratio += 0.10 * rank(player, "second_wind")

    if player.class_id == "ranger" and rank(player, "field_medic"):
        ratio += 0.10

    if player.class_id == "wizard" and enemy.boss and rank(player, "arcane_recovery"):
        ratio += 0.12

    if player.class_id == "monk" and rank(player, "renewal"):
        ratio += 0.10

    return max(0, int(player.max_hp * ratio))


def monk_flurry_heal_ratio(player):
    return 0.20 + 0.06 * rank(player, "inner_healing")


def wizard_echo_chance(player):
    if player.class_id == "wizard" and rank(player, "spell_echo"):
        return 0.22
    return 0.0
