import os
import sys
import time

from art_loader import load_art
import save_system

WIDTH = 62

ANSI_RESET = "\033[0m"
ANSI_INVERT = "\033[7m"

# Global animation timing multiplier.
# 1.0 = original speed
# 1.5 = 50% slower
# 1.8 = current game setting
# 2.0 = twice as slow
ANIMATION_SPEED = 1.8


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def _sleep(seconds):
    time.sleep(max(0.0, seconds) * ANIMATION_SPEED)


def _tint_ascii_lines(lines, ansi_color):
    tinted = []
    for line in lines:
        if line.strip():
            tinted.append(f"{ansi_color}{line}{ANSI_RESET}")
        else:
            tinted.append(line)
    return tinted


def _life_line():
    try:
        deaths = save_system.death_count()
        maximum = save_system.MAX_RUN_DEATHS
    except Exception:
        deaths = 0
        maximum = 5

    remaining = max(0, maximum - deaths)
    hearts = " ".join(["<3"] * remaining) if remaining else "--"
    return f"LIVES  {hearts}"


def _draw(lines, flash=False, show_lives=True):
    clear()

    if isinstance(lines, str):
        lines = lines.splitlines()

    if show_lives:
        lines = [_life_line(), ""] + list(lines)

    if flash:
        sys.stdout.write(ANSI_INVERT)

    sys.stdout.write("\n".join(lines))
    sys.stdout.write("\n")

    if flash:
        sys.stdout.write(ANSI_RESET)

    sys.stdout.flush()


def _center_block(lines, width=64):
    return [line.center(width) for line in lines]


def _box(lines, title=""):
    rows = ["+" + "=" * WIDTH + "+"]
    if title:
        rows.append("|" + f" {title} ".center(WIDTH) + "|")
        rows.append("+" + "=" * WIDTH + "+")
    for line in lines:
        rows.append("|" + str(line)[:WIDTH].center(WIDTH) + "|")
    rows.append("+" + "=" * WIDTH + "+")
    return rows


def attack_slash(enemy_name="Enemy", damage=None):
    """Fast basic-attack slash used by the real combat loop."""
    result = "The strike lands."
    if damage is not None:
        result = f"{enemy_name} takes {damage} damage."

    frames = [
        [
            "",
            "",
            "                         /",
            "                        /",
            "                       /",
            "",
        ],
        [
            "",
            "                           //",
            "                         //",
            "                       //",
            "                     //",
            "",
        ],
        [
            "",
            "                    /////////////",
            "                 /////",
            "              ////",
            "",
            "",
        ],
        _box([
            "",
            "SLASH!",
            "",
            result,
            "",
        ], "ATTACK"),
    ]

    for i, frame in enumerate(frames):
        _draw(_center_block(frame) if i < 3 else frame, flash=(i == 2))
        _sleep(0.055 if i < 3 else 0.22)


def critical_hit(damage=None, enemy_name="Enemy"):
    """Impact flash for any real critical strike."""
    damage_line = "Massive damage!"
    if damage is not None:
        damage_line = f"{enemy_name}: -{damage} HP"

    frames = [
        _box(["", ".", "", ""], "IMPACT"),
        _box(["", ">>> * <<<", "", ""], "IMPACT"),
        _box(["", ">>> *** <<<", "", ""], "IMPACT"),
        _box([
            "",
            "CRITICAL HIT!",
            "",
            damage_line,
            "",
        ], "IMPACT"),
    ]

    for i, frame in enumerate(frames):
        _draw(frame, flash=(i in (2, 3)))
        _sleep(0.065 if i < 3 else 0.28)


def _split_door_frame(art_lines, gap):
    if not art_lines:
        return ["[door art missing]"]

    width = max(len(line) for line in art_lines)
    mid = width // 2
    result = []

    for line in art_lines:
        line = line.ljust(width)
        left = line[:mid]
        right = line[mid:]
        result.append(left + (" " * gap) + right)

    return result


def door_open(next_floor=None, safe_haven=False, door_color=None, difficulty=1):
    """Animate the boss gate after Floors 5, 10, 15, 20, etc."""
    art = load_art("door")
    lines = art.splitlines()

    if not lines:
        _draw(_box(["Door art is missing."], "BOSS GATE"))
        _sleep(0.4)
        return

    color = None
    if door_color == "blue":
        color = "\033[94m"
    elif door_color == "red":
        color = "\033[91m"

    for pad in (0, 2, 0, 1):
        shifted = [(" " * pad) + line for line in lines]
        if color:
            shifted = _tint_ascii_lines(shifted, color)
        _draw(shifted, flash=(pad == 2))
        _sleep(0.055)

    gate_name = ""
    if door_color:
        gate_name = f"{door_color.upper()} GATE - "

    if safe_haven:
        label = f"{gate_name}SAFE HAVEN AHEAD - DIFFICULTY x{difficulty}"
    elif next_floor is not None:
        label = (
            f"{gate_name}FLOOR {next_floor} OPENS - "
            f"DIFFICULTY x{difficulty}"
        )
    else:
        label = f"{gate_name}THE WAY OPENS"

    for gap in (2, 5, 9, 14):
        raw_frame = _split_door_frame(lines, gap)
        width = max(len(x) for x in raw_frame)
        frame = raw_frame + ["", label.center(width)]
        if color:
            colored_part = _tint_ascii_lines(raw_frame, color)
            frame = colored_part + ["", label.center(width)]
        _draw(frame)
        _sleep(0.10)

    _sleep(0.22)


def safe_haven_reveal(completed_floor=None):
    """Reveal the Safe Haven once when a 20-floor milestone is reached."""
    art = load_art("safe_haven")
    lines = art.splitlines()

    if not lines:
        _draw(_box(["Safe Haven art is missing."], "SAFE HAVEN"))
        _sleep(0.4)
        return

    step = max(1, len(lines) // 7)
    shown = step
    while shown < len(lines):
        frame = lines[:shown]
        frame += ["", " " * 20 + "The darkness begins to lift..."]
        _draw(frame)
        _sleep(0.10)
        shown += step

    _draw(lines, flash=True)
    _sleep(0.12)

    checkpoint_text = "CHECKPOINT ESTABLISHED"
    if completed_floor is not None:
        checkpoint_text = f"DEATH CHECKPOINT: FLOOR {completed_floor}"

    final = list(lines)
    final += [
        "",
        "+" + "=" * WIDTH + "+",
        "|" + " SAFE HAVEN FOUND ".center(WIDTH) + "|",
        "+" + "=" * WIDTH + "+",
        "|" + f" {checkpoint_text} ".center(WIDTH) + "|",
        "+" + "=" * WIDTH + "+",
    ]
    _draw(final)
    _sleep(0.48)


def _bar(value, maximum, size=24):
    maximum = max(1, maximum)
    ratio = max(0.0, min(1.0, value / maximum))
    filled = int(size * ratio)
    return "[" + "#" * filled + "." * (size - filled) + "]"


def level_up(old_level=1, new_level=2, skill_points=None):
    """Level-up flash using the player's real level values."""
    if new_level <= old_level:
        return

    # A short fill is deliberately symbolic; actual XP is shown again
    # immediately by the normal player panel after the animation.
    maximum = 20
    for xp in (4, 8, 12, 16, 20):
        _draw(_box([
            "",
            f"Level {old_level}",
            "",
            f"XP {_bar(xp, maximum)}",
            "",
        ], "EXPERIENCE"))
        _sleep(0.07)

    point_text = "+1 SKILL POINT"
    gained = new_level - old_level
    if gained > 1:
        point_text = f"+{gained} SKILL POINTS"
    if skill_points is not None:
        point_text += f"  |  AVAILABLE: {skill_points}"

    _draw(_box([
        "",
        "LEVEL UP!",
        "",
        f"LEVEL {old_level}  ->  LEVEL {new_level}",
        "",
        point_text,
        "",
    ], "HUNTER ASCENDS"), flash=True)
    _sleep(0.48)


def healing(start_hp=31, end_hp=49, max_hp=80, label="HEALING"):
    """Animate an actual HP increase."""
    start_hp = max(0, min(max_hp, int(start_hp)))
    end_hp = max(0, min(max_hp, int(end_hp)))

    if end_hp <= start_hp:
        return

    distance = end_hp - start_hp
    steps = min(6, max(2, distance))
    values = []

    for step in range(steps + 1):
        value = start_hp + round(distance * step / steps)
        if not values or value != values[-1]:
            values.append(value)

    for hp in values:
        gain = hp - start_hp
        _draw(_box([
            "",
            f"HP {_bar(hp, max_hp)} {hp}/{max_hp}",
            "",
            f"+{gain} HP" if gain else "Restoring health...",
            "",
        ], label))
        _sleep(0.07)

    _sleep(0.18)


def run_showcase():
    attack_slash("Tower Guardian", 14)
    critical_hit(27, "Tower Guardian")
    door_open(21, safe_haven=True, door_color="red", difficulty=2)
    safe_haven_reveal(20)
    level_up(7, 8, 1)
    healing(31, 49, 80)
