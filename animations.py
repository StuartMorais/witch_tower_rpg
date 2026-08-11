import os
import sys
import time

from art_loader import load_art

WIDTH = 62

ANSI_RESET = "\033[0m"
ANSI_INVERT = "\033[7m"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def _sleep(seconds):
    time.sleep(max(0.0, seconds))


def _draw(lines, flash=False):
    clear()

    if isinstance(lines, str):
        lines = lines.splitlines()

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


def attack_slash():
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
            "Tower Guardian takes 14 damage.",
            "",
        ], "ATTACK"),
    ]

    for i, frame in enumerate(frames):
        _draw(_center_block(frame) if i < 3 else frame, flash=(i == 2))
        _sleep(0.07 if i < 3 else 0.45)


def critical_hit():
    frames = [
        _box(["", ".", "", ""], "IMPACT"),
        _box(["", ">>> * <<<", "", ""], "IMPACT"),
        _box(["", ">>> *** <<<", "", ""], "IMPACT"),
        _box([
            "",
            "CRITICAL HIT!",
            "",
            "-27 HP",
            "",
        ], "IMPACT"),
    ]

    for i, frame in enumerate(frames):
        _draw(frame, flash=(i in (2, 3)))
        _sleep(0.08 if i < 3 else 0.55)


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


def door_open():
    art = load_art("door")
    lines = art.splitlines()

    if not lines:
        _draw(_box(["Door art is missing."], "DOOR TEST"))
        _sleep(0.6)
        return

    for pad in (0, 2, 0, 1):
        shifted = [(" " * pad) + line for line in lines]
        _draw(shifted, flash=(pad == 2))
        _sleep(0.07)

    for gap in (2, 5, 9, 14):
        frame = _split_door_frame(lines, gap)
        width = max(len(x) for x in frame)
        frame += ["", "THE WAY OPENS".center(width)]
        _draw(frame)
        _sleep(0.13)

    _sleep(0.45)


def safe_haven_reveal():
    art = load_art("safe_haven")
    lines = art.splitlines()

    if not lines:
        _draw(_box(["Safe Haven art is missing."], "SAFE HAVEN"))
        _sleep(0.6)
        return

    step = max(1, len(lines) // 7)
    shown = step
    while shown < len(lines):
        frame = lines[:shown]
        frame += ["", " " * 20 + "The darkness begins to lift..."]
        _draw(frame)
        _sleep(0.13)
        shown += step

    _draw(lines, flash=True)
    _sleep(0.16)

    final = list(lines)
    final += [
        "",
        "+" + "=" * WIDTH + "+",
        "|" + " SAFE HAVEN FOUND ".center(WIDTH) + "|",
        "+" + "=" * WIDTH + "+",
        "|" + " CHECKPOINT ESTABLISHED ".center(WIDTH) + "|",
        "+" + "=" * WIDTH + "+",
    ]
    _draw(final)
    _sleep(0.75)


def _bar(value, maximum, size=24):
    maximum = max(1, maximum)
    ratio = max(0.0, min(1.0, value / maximum))
    filled = int(size * ratio)
    return "[" + "#" * filled + "." * (size - filled) + "]"


def level_up():
    old_level = 7
    new_level = 8
    maximum = 70

    for xp in (48, 53, 58, 63, 67, 70):
        _draw(_box([
            "",
            f"Level {old_level}",
            "",
            f"XP {_bar(xp, maximum)} {xp}/{maximum}",
            "",
        ], "EXPERIENCE"))
        _sleep(0.10)

    _draw(_box([
        "",
        "LEVEL UP!",
        "",
        f"LEVEL {old_level}  ->  LEVEL {new_level}",
        "",
        "+1 SKILL POINT",
        "",
    ], "HUNTER ASCENDS"), flash=True)
    _sleep(0.75)


def healing():
    current = 31
    maximum = 80

    for hp in (31, 34, 37, 40, 43, 46, 49):
        gain = hp - current
        _draw(_box([
            "",
            f"HP {_bar(hp, maximum)} {hp}/{maximum}",
            "",
            f"+{gain} HP" if gain else "Potion uncorked...",
            "",
        ], "HEALING"))
        _sleep(0.10)

    _sleep(0.35)


def run_showcase():
    attack_slash()
    critical_hit()
    door_open()
    safe_haven_reveal()
    level_up()
    healing()
