import os
import random
import sys
import time
from art_loader import load_art
import save_system

WIDTH = 62


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def line(char="-"):
    print("+" + char * WIDTH + "+")


def heart_hud():
    """ASCII life counter based on irreversible run deaths."""
    try:
        deaths = save_system.death_count()
        maximum = save_system.MAX_RUN_DEATHS
    except Exception:
        deaths = 0
        maximum = 5

    remaining = max(0, maximum - deaths)
    hearts = " ".join(["<3"] * remaining) if remaining else "--"
    return f"LIVES  {hearts}"


def show_heart_hud():
    print(heart_hud())


def _tint_ascii_art(art_text, ansi_color):
    """
    Apply ANSI color to visible lines while preserving blank spacing.

    This keeps the exact art silhouette from the source text file.
    """
    tinted = []
    for line in art_text.splitlines():
        if line.strip():
            tinted.append(f"{ansi_color}{line}{ANSI_RESET}")
        else:
            tinted.append(line)
    return "\n".join(tinted)


def box(lines, title=None, border="-"):
    line(border)
    if title:
        text = f" {title} "
        print("|" + text.center(WIDTH) + "|")
        line(border)
    for text in lines:
        text = str(text)
        if len(text) > WIDTH:
            text = text[:WIDTH]
        print("|" + text.ljust(WIDTH) + "|")
    line(border)


def center(text=""):
    print(text.center(WIDTH + 2))


def bar(value, maximum, size=24, fill="#", empty="."):
    maximum = max(1, maximum)
    ratio = max(0.0, min(1.0, value / maximum))
    filled = int(size * ratio)
    return "[" + fill * filled + empty * (size - filled) + "]"


def menu(options, prompt="Choose"):
    while True:
        for number, label in enumerate(options, 1):
            print(f"  {number}. {label}")
        raw = input(f"\n{prompt} > ").strip()
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= len(options):
                return choice
        print(f"\nEnter a number from 1 to {len(options)}.\n")


def boss_door_choice(current_multiplier):
    """
    Show the post-boss fork using the same door art in different colors.

    BLUE = keep the current difficulty.
    RED  = double the current difficulty.

    The choice screen itself is intentionally more subtle and atmospheric.
    """
    current_multiplier = max(1, int(current_multiplier))
    red_multiplier = current_multiplier * 2

    clear()
    show_heart_hud()
    print()

    door_art = load_art("door")
    blue_door = _tint_ascii_art(door_art, ANSI_BLUE)
    red_door = _tint_ascii_art(door_art, ANSI_RED)

    box([
        "Beyond the fallen guardian, two ancient gates stand in silence.",
        "",
        "From the blue-lit threshold comes a cool, refreshing wind.",
        "From the red-lit threshold seeps a dense and hostile miasma.",
        "",
        "One path feels steady. The other feels dangerous.",
    ], title="THE FORK BEYOND THE BOSS", border="=")

    print()
    print(ANSI_BLUE + "BLUE DOOR" + ANSI_RESET)
    print(blue_door)
    print()
    print("A refreshing wind brushes past your face.")
    print()

    print(ANSI_RED + "RED DOOR" + ANSI_RESET)
    print(red_door)
    print()
    print("A strong miasma rolls from the darkness beyond.")
    print()

    choice = menu([
        "Step through the blue door",
        "Step through the red door",
    ], "Choose a path")

    if choice == 1:
        return "blue", current_multiplier
    return "red", red_multiplier


def pause(message="Press ENTER to continue..."):
    input("\n" + message)


TOWER_ART = load_art("castle")


# ------------------------------------------------------------
# MAIN MENU RAIN
# ------------------------------------------------------------

RAIN_FRAMES = 22
RAIN_DELAY = 0.075
RAIN_DROPS = 46


def _make_rain_frame(art_lines, drops, width):
    """Overlay rain only on blank space so the tower art stays readable."""
    canvas = [list(line.ljust(width)) for line in art_lines]

    for x, y, speed in drops:
        if not (0 <= y < len(canvas) and 0 <= x < width):
            continue

        # Never overwrite the actual castle/title artwork.
        if canvas[y][x] != " ":
            continue

        # Faster drops look longer; slower drops look lighter/farther away.
        canvas[y][x] = "|" if speed > 1 else "'"

        # Small trailing streak for the closest drops.
        if speed > 1 and y > 0 and canvas[y - 1][x] == " ":
            canvas[y - 1][x] = "."

    return "\n".join("".join(row).rstrip() for row in canvas)


def rain_tower_intro():
    """
    Play a short ambient rain animation over the Witch Tower.

    The animation runs only when the main camp menu opens. It deliberately
    finishes before input() begins so terminal input remains reliable.
    """
    art_lines = TOWER_ART.splitlines()
    if not art_lines:
        return TOWER_ART

    height = len(art_lines)
    width = max(max(len(line) for line in art_lines), WIDTH + 2)

    rng = random.Random()
    drops = []
    for _ in range(RAIN_DROPS):
        drops.append([
            rng.randrange(0, width),
            rng.randrange(-height, height),
            rng.choice((1, 1, 1, 2)),
        ])

    final_frame = TOWER_ART

    for _ in range(RAIN_FRAMES):
        clear()
        show_heart_hud()
        print()
        final_frame = _make_rain_frame(art_lines, drops, width)
        print(final_frame)
        sys.stdout.flush()
        time.sleep(RAIN_DELAY)

        for drop in drops:
            drop[1] += drop[2]

            if drop[1] >= height:
                drop[0] = rng.randrange(0, width)
                drop[1] = rng.randrange(-6, 0)
                drop[2] = rng.choice((1, 1, 1, 2))

    return final_frame




# ------------------------------------------------------------
# TERMINAL EFFECTS
# ------------------------------------------------------------

ANSI_RESET = "\033[0m"
ANSI_INVERT = "\033[7m"
ANSI_BLUE = "\033[94m"
ANSI_RED = "\033[91m"


def _render_shifted(lines, x=0, y=0, flash=False):
    """Redraw a list of ASCII lines with a temporary screen offset."""
    clear()
    if flash:
        sys.stdout.write(ANSI_INVERT)

    if y > 0:
        sys.stdout.write("\n" * y)

    pad = " " * max(0, x)
    for row in lines:
        sys.stdout.write(pad + row + "\n")

    if flash:
        sys.stdout.write(ANSI_RESET)

    sys.stdout.flush()


def combat_frame_lines(player, enemy, damage_text=None):
    """Return the combat panel as plain ASCII lines for animation."""
    rows = [heart_hud(), ""]
    rows.append("+" + "=" * WIDTH + "+")
    rows.append("|" + " COMBAT ".center(WIDTH) + "|")
    rows.append("+" + "=" * WIDTH + "+")
    rows.append("|" + f"Enemy : {enemy.name}".ljust(WIDTH) + "|")
    rows.append("|" + f"HP    : {bar(enemy.hp, enemy.max_hp)} {max(0, enemy.hp)}/{enemy.max_hp}".ljust(WIDTH) + "|")
    rows.append("|" + "".ljust(WIDTH) + "|")
    rows.append("|" + f"{player.name} - Lv.{player.level} {player.class_name}".ljust(WIDTH) + "|")
    rows.append("|" + f"HP    : {bar(player.hp, player.max_hp)} {max(0, player.hp)}/{player.max_hp}".ljust(WIDTH) + "|")
    rows.append("|" + f"Skill : {player.skill_name}".ljust(WIDTH) + "|")
    rows.append("|" + f"CD    : {player.skill_cooldown}".ljust(WIDTH) + "|")
    rows.append("+" + "=" * WIDTH + "+")

    if damage_text:
        rows.append("")
        rows.append(("<<< " + damage_text + " >>>").center(WIDTH + 2))

    return rows


SHAKE_PROFILES = {
    # (horizontal offset, vertical offset, flash)
    "light": [
        (2, 0, True),
        (5, 0, False),
        (1, 0, False),
        (3, 0, False),
    ],
    "heavy": [
        (3, 0, True),
        (7, 1, True),
        (0, 0, False),
        (6, 1, False),
        (1, 0, False),
        (5, 0, False),
        (2, 0, False),
    ],
    "boss": [
        (4, 0, True),
        (8, 1, True),
        (0, 1, False),
        (7, 0, True),
        (1, 1, False),
        (6, 0, False),
        (0, 0, False),
        (4, 0, False),
        (2, 0, False),
    ],
}


def damage_shake(player, enemy, damage, strength="light"):
    """
    Flash and shake the combat UI after the player takes damage.
    strength: light, heavy, boss
    """
    profile = SHAKE_PROFILES.get(strength, SHAKE_PROFILES["light"])
    delay = {
        "light": 0.028,
        "heavy": 0.038,
        "boss": 0.046,
    }.get(strength, 0.03)

    lines = combat_frame_lines(player, enemy, f"-{damage} HP")

    # Give the animation a small left/right baseline.
    for x, y, flash in profile:
        _render_shifted(lines, x=x, y=y, flash=flash)
        time.sleep(delay)

    _render_shifted(lines, x=2, y=0, flash=False)
    time.sleep(0.06)


def flash_message(message, duration=0.08):
    """Quick full-terminal inverse flash with a centered ASCII message."""
    width = WIDTH + 2
    lines = [
        "+" + "=" * WIDTH + "+",
        "|" + "".center(WIDTH) + "|",
        "|" + message.center(WIDTH) + "|",
        "|" + "".center(WIDTH) + "|",
        "+" + "=" * WIDTH + "+",
    ]
    _render_shifted(lines, x=2, y=1, flash=True)
    time.sleep(duration)
    clear()


def effect_demo():
    """Standalone lab for tuning terminal effects and preview animations."""
    import animations

    class DemoPlayer:
        name = "Sarah"
        class_name = "Warrior"
        level = 7
        hp = 63
        max_hp = 80
        skill_name = "Power Strike"
        skill_cooldown = 0

    class DemoEnemy:
        name = "Tower Guardian"
        hp = 91
        max_hp = 120

    player = DemoPlayer()
    enemy = DemoEnemy()

    while True:
        clear()
        box([
            "Preview effects and animations without changing gameplay.",
            "",
            "IMPACT EFFECTS",
            "Existing shake / flash effects.",
            "",
            "ANIMATION TESTS",
            "Experimental ASCII sequences for important game moments.",
        ], title="EFFECT + ANIMATION LAB", border="=")
        print()

        choice = menu([
            "Light damage shake",
            "Heavy damage shake",
            "Boss damage shake",
            "Flash only",
            "Attack slash animation",
            "Critical hit animation",
            "Boss door opening animation",
            "Safe Haven reveal animation",
            "Level-up animation",
            "Healing animation",
            "Run animation showcase",
            "Return",
        ], "Effect")

        if choice == 1:
            damage_shake(player, enemy, 6, "light")
            pause()
        elif choice == 2:
            damage_shake(player, enemy, 15, "heavy")
            pause()
        elif choice == 3:
            damage_shake(player, enemy, 28, "boss")
            pause()
        elif choice == 4:
            flash_message("*** IMPACT ***", 0.12)
            pause()
        elif choice == 5:
            animations.attack_slash()
            pause()
        elif choice == 6:
            animations.critical_hit()
            pause()
        elif choice == 7:
            animations.door_open()
            pause()
        elif choice == 8:
            animations.safe_haven_reveal()
            pause()
        elif choice == 9:
            animations.level_up()
            pause()
        elif choice == 10:
            animations.healing()
            pause()
        elif choice == 11:
            animations.run_showcase()
            pause()
        else:
            return


def title_screen():
    # Play the ambient rain immediately when the game first opens.
    rainy_tower = rain_tower_intro()

    clear()
    show_heart_hud()
    print()
    print(rainy_tower)
    box([
        "An endless tower rises beyond Thornwatch Camp.",
        "Every five floors change theme.",
        "Every fifth floor holds a boss.",
        "Every twentieth floor hides a permanent Safe Haven.",
    ], title="THE WITCH TOWER", border="=")


def camp_screen(has_save, has_checkpoint=False):
    clear()
    show_heart_hud()
    print()
    print(TOWER_ART)
    box([
        "THORNWATCH CAMP - TOWER ENTRANCE",
        "",
        "A small campfire burns beneath the shadow of the tower.",
        "Hunters sharpen weapons, sort supplies, and prepare to climb.",
        "",
        "The tower has no known final floor.",
    ], border="=")
    if has_save:
        print("\n  [AUTOSAVE] A saved climb is available.")
        if has_checkpoint:
            print("  [SAFE HAVEN] A protected death checkpoint is active.\n")
        else:
            print("  [PERMADEATH] Reach Floor 20 to create a death checkpoint.\n")
    else:
        print("\n  No saved climb. Death before Floor 20 ends the run.\n")

def player_panel(player, show_hearts=True):
    if show_hearts:
        show_heart_hud()
        print()

    box([
        f"Name : {player.name:<18} Class : {player.class_name}",
        f"Level: {player.level:<10} Skill Points: {player.skill_points:<5} Floor: {player.floor}",
        f"HP   : {bar(player.hp, player.max_hp)} {player.hp}/{player.max_hp}",
        f"XP   : {bar(player.xp, player.xp_to_next())} {player.xp}/{player.xp_to_next()}",
        f"ATK  : {player.attack:<5} DEF: {player.defense:<5} SPD: {player.speed:<5}",
        f"Crit : {int(player.crit * 100)}%    Evade: {int(player.evade * 100)}%    Gold: {player.gold}",
        f"Difficulty: x{player.difficulty_multiplier}",
    ], title="HUNTER")


def floor_screen(player, theme, room_name, boss=False):
    clear()
    show_heart_hud()
    print()
    block_start = ((player.floor - 1) // 5) * 5 + 1
    block_end = block_start + 4
    label = "BOSS FLOOR" if boss else "TOWER FLOOR"
    box([
        f"{label}: {player.floor}",
        f"Theme      : {theme['name']}",
        f"Zone       : Floors {block_start}-{block_end}",
        f"Room       : {room_name}",
        "",
        theme["tagline"],
    ], title="THE WITCH TOWER", border="=")
    print()
    player_panel(player, show_hearts=False)
    print()


def combat_screen(player, enemy):
    _render_shifted(combat_frame_lines(player, enemy), x=2, y=0, flash=False)


def recovery_room_screen(player, completed_floor):
    clear()
    show_heart_hud()
    print()
    print(r"""
+==============================================================+
|                       RECOVERY ROOM                          |
|                                                              |
|                        ______                                |
|                       / ____ \                               |
|                      / /    \ \                              |
|                     | | FIRE | |                             |
|                      \ \____/ /                              |
|                       \______/                               |
|                                                              |
|                The guardian cannot enter here.               |
+==============================================================+
""")
    box([
        f"Boss Floor {completed_floor} cleared.",
        "Your wounds are restored and current progress is autosaved.",
        "This does NOT move your protected death checkpoint.",
    ], title="REST - AUTOSAVE", border="-")
    print()
    player_panel(player, show_hearts=False)


def safe_haven_screen(player, completed_floor):
    clear()
    show_heart_hud()
    print()
    print(load_art("safe_haven"))
    print()
    box([
        f"Floor {completed_floor} milestone reached.",
        f"Protected death checkpoint: after Floor {completed_floor}.",
        f"Death will return you here and resume at Floor {completed_floor + 1}.",
    ], title="CHECKPOINT SAVED", border="=")
    print()
    player_panel(player, show_hearts=False)


def death_rewind_screen(
    name,
    death_floor,
    safe_floor=None,
    death_number=None,
    max_deaths=5,
):
    clear()
    show_heart_hud()
    print()

    count_line = ""
    if death_number is not None:
        count_line = f"Run deaths: {death_number}/{max_deaths}"

    if safe_floor is None:
        lines = [
            f"{name} fell on Floor {death_floor}.",
            "",
            "No Safe Haven was reached.",
            "This run is permanently lost.",
            "A new hunter must begin again from Floor 1.",
        ]
        if count_line:
            lines.insert(2, count_line)

        box(lines, title="PERMADEATH", border="=")
        return

    remaining = max(0, max_deaths - (death_number or 0))
    lines = [
        f"{name} fell on Floor {death_floor}.",
        "",
        count_line,
        f"Deaths remaining before permanent death: {remaining}",
        "",
        f"Safe Haven after Floor {safe_floor} answers the death.",
        f"Everything gained after that checkpoint is lost.",
        f"You return to the saved state and resume at Floor {safe_floor + 1}.",
    ]
    box(lines, title="DEATH - CHECKPOINT REWIND", border="=")


def final_permadeath_screen(name, death_floor, death_number, max_deaths=5):
    clear()
    show_heart_hud()
    print()
    box([
        f"{name} fell on Floor {death_floor}.",
        "",
        f"Run deaths: {death_number}/{max_deaths}",
        "",
        "The final death has been spent.",
        "No Safe Haven can call this hunter back.",
        "",
        "The entire run is permanently erased.",
        "A new hunter must begin again from Floor 1.",
    ], title="FINAL PERMADEATH", border="=")
