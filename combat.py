import random
from data import ITEM_DATA
import skills
import ui
from art_loader import load_item_art


def _basic_damage(attacker_attack, defender_defense):
    raw = attacker_attack + random.randint(-2, 3)
    return max(1, raw - defender_defense // 2)


def _player_attack(player, enemy):
    damage = _basic_damage(player.attack, enemy.defense)
    critical = random.random() < player.crit
    if critical:
        damage = int(damage * 1.7)

    damage = max(1, int(damage * skills.basic_attack_multiplier(player, enemy)))
    enemy.hp -= damage
    return damage, critical


def _use_skill(player, enemy):
    if player.skill_cooldown > 0:
        return False, f"{player.skill_name} is on cooldown for {player.skill_cooldown} more turn(s)."

    base = _basic_damage(player.attack, enemy.defense)
    tree_mult = skills.skill_damage_multiplier(player)
    outgoing = skills.outgoing_multiplier(player, enemy)
    echo_note = ""

    if player.class_id == "warrior":
        damage = int((base * 1.9 + 2) * tree_mult * outgoing)
        enemy.hp -= damage
        player.skill_cooldown = skills.skill_cooldown(player, 3)
        return True, f"Power Strike deals {damage} damage."

    if player.class_id == "ranger":
        damage = int(base * 1.45 * tree_mult)
        aimed_crit = min(0.95, 0.55 + skills.skill_crit_bonus(player))
        if random.random() < aimed_crit:
            damage = int(damage * 1.7)
            note = " Critical hit!"
        else:
            note = ""
        damage = max(1, int(damage * outgoing))
        enemy.hp -= damage
        player.skill_cooldown = skills.skill_cooldown(player, 2)
        return True, f"Aimed Shot deals {damage} damage.{note}"

    if player.class_id == "wizard":
        damage = int((player.attack * 2 + random.randint(2, 7)) * tree_mult * outgoing)
        enemy.hp -= damage
        player.skill_cooldown = skills.skill_cooldown(player, 3)
        if random.random() < skills.wizard_echo_chance(player):
            player.skill_cooldown = 0
            echo_note = " Spell Echo resets the cooldown!"
        return True, f"Arcane Blast ignores armor and deals {damage} damage.{echo_note}"

    if player.class_id == "thief":
        damage = int(base * 1.65 * tree_mult)
        note = ""
        if random.random() < 0.45:
            damage += player.attack
            note += " Perfect opening!"
        if random.random() < skills.skill_crit_bonus(player):
            damage = int(damage * 1.7)
            note += " Assassinate critical!"
        damage = max(1, int(damage * outgoing))
        enemy.hp -= damage
        player.skill_cooldown = skills.skill_cooldown(player, 2)
        return True, f"Backstab deals {damage} damage.{note}"

    if player.class_id == "monk":
        first = max(1, int(base * 0.8))
        second = max(1, int(_basic_damage(player.attack, enemy.defense) * 0.8))
        damage = max(1, int((first + second) * tree_mult * outgoing))
        enemy.hp -= damage
        heal_ratio = skills.monk_flurry_heal_ratio(player)
        restored = player.heal(max(1, int(damage * heal_ratio)))
        player.skill_cooldown = skills.skill_cooldown(player, 3)
        return True, f"Flurry deals {damage} total damage and restores {restored} HP."

    return False, "No skill available."


def _combat_item_menu(player, enemy):
    usable = []
    for item in ("Small Potion", "Large Potion", "Bomb", "Smoke Bomb"):
        if player.has_item(item):
            usable.append(item)

    if not usable:
        return False, "You have no combat items.", None

    labels = [f"{name} x{player.inventory[name]} - {ITEM_DATA[name]['description']}" for name in usable]
    labels.append("Cancel")
    choice = ui.menu(labels, "Use item")

    if choice == len(labels):
        return False, "Cancelled.", None

    item = usable[choice - 1]

    if item in ("Small Potion", "Large Potion"):
        if player.hp >= player.max_hp:
            return False, "Your HP is already full.", None
        print()
        print(load_item_art(item))
        player.remove_item(item)
        restored = player.heal(ITEM_DATA[item]["value"])
        return True, f"You restore {restored} HP.", None

    if item == "Bomb":
        print()
        print(load_item_art(item))
        player.remove_item(item)
        damage = ITEM_DATA[item]["value"] + player.level * 2
        enemy.hp -= damage
        return True, f"The bomb deals {damage} damage.", None

    if item == "Smoke Bomb":
        if enemy.boss:
            return False, "Smoke Bombs do not work on bosses.", None
        print()
        print(load_item_art(item))
        player.remove_item(item)
        return True, "Smoke fills the room. You escape the fight.", "escaped"

    return False, "Nothing happens.", None


def run_combat(player, enemy):
    message = f"A {enemy.name} blocks the way."

    while player.hp > 0 and enemy.hp > 0:
        ui.combat_screen(player, enemy)
        print(message + "\n")

        choices = [
            "Attack",
            f"Skill: {player.skill_name}",
            "Use Item",
            "Inspect",
        ]
        action = ui.menu(choices, "Action")

        turn_used = False
        message = ""

        if action == 1:
            damage, critical = _player_attack(player, enemy)
            message = f"You deal {damage} damage."
            if critical:
                message += " CRITICAL!"
            turn_used = True

        elif action == 2:
            turn_used, message = _use_skill(player, enemy)

        elif action == 3:
            turn_used, message, special = _combat_item_menu(player, enemy)
            if special == "escaped":
                ui.combat_screen(player, enemy)
                print(message)
                ui.pause()
                return "escaped"

        elif action == 4:
            message = (
                f"{enemy.name}: ATK {enemy.attack}, DEF {enemy.defense}, "
                f"SPD {enemy.speed}, Reward {enemy.xp} XP."
            )

        if enemy.hp <= 0:
            break

        if not turn_used:
            continue

        if player.skill_cooldown > 0:
            player.skill_cooldown -= 1

        if random.random() < player.evade:
            message += f"\nYou evade {enemy.name}'s attack."
        else:
            damage = _basic_damage(enemy.attack, player.defense)
            damage = skills.incoming_damage(player, enemy, damage)
            player.hp -= damage

            if enemy.boss:
                shake_strength = "boss"
            elif damage >= max(10, player.max_hp // 5):
                shake_strength = "heavy"
            else:
                shake_strength = "light"

            ui.damage_shake(player, enemy, damage, shake_strength)
            message += f"\n{enemy.name} deals {damage} damage."

    if player.hp <= 0:
        return "dead"

    player.gold += enemy.gold
    levels = player.add_xp(enemy.xp)
    victory_heal = skills.victory_heal(player, enemy)
    restored = player.heal(victory_heal) if victory_heal else 0

    ui.combat_screen(player, enemy)
    print(f"{enemy.name} defeated.")
    print(f"Reward: {enemy.xp} XP and {enemy.gold} gold.")
    if restored:
        print(f"Second Wind restores {restored} HP.")
    if levels:
        print(f"LEVEL UP! You reached level {player.level}. HP fully restored.")
        print(f"Skill Points available: {player.skill_points}")
    ui.pause()
    return "victory"
