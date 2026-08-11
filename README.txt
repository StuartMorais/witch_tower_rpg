THE WITCH TOWER - TERMINAL RPG
==============================

A modular, text-based Python roguelike.

FEATURES
--------
- Camp at the tower entrance
- Infinite randomly themed tower
- One theme per 5-floor zone
- Boss every 5th floor
- Recovery room after every boss
- Permanent Safe Haven checkpoint every 20 floors
- Inventory and consumable items
- Permanent stat-up items
- XP and level-up system
- Class-specific skill trees with skill points
- Five classes:
  Warrior
  Ranger
  Wizard
  Thief
  Monk
- ASCII-only terminal UI
- JSON checkpoint saves

RUN
---
Open a terminal in this folder and run:

    python main.py

FILES
-----
main.py         Entry point
game.py         Main game loop and floor events
player.py       Player stats, inventory, levels
combat.py       Combat and class skills
enemy.py        Enemy generation
tower.py        Infinite floor/theme generation
items.py        Loot logic
data.py         Classes, themes, item definitions
ui.py           ASCII interface
art_loader.py   Loads external ASCII scene files
art/            Environmental ASCII scene files
save_system.py  JSON save/load system

SAVE / PERMADEATH
----------------
The game uses a Safe Haven checkpoint system.

- Bosses still appear every 5 floors.
- Recovery rooms after Floors 5, 10, 15, etc. heal you but DO NOT save.
- Floors 20, 40, 60, 80... create permanent Safe Haven checkpoints.
- Dying before the first Safe Haven permanently ends the run.
- Dying after a Safe Haven restores the exact saved character snapshot.

Example:
    Clear Floor 20 -> Safe Haven -> checkpoint resumes on Floor 21.
    Die on Floor 37 -> return to the Floor 20 Safe Haven snapshot.
    Clear Floor 40 -> new checkpoint replaces the Floor 20 checkpoint.

Checkpoint file:

    saves/safe_haven.json

Starting a new run erases the previous Safe Haven checkpoint.

SKILL TREES
-----------
You begin with 1 skill point and gain 1 more every time you level up.
Skill points can be spent at the beginning of a new run, from the
Manage Hunter option at camp, or inside save rooms.

Each class has ten skills across three tiers:

Warrior - durability, Power Strike, boss resistance
Ranger  - crit, evade, Aimed Shot, boss damage
Wizard  - Arcane Blast power, cooldown, spell echo
Thief   - crit, evade, Backstab, execution damage
Monk    - defense, Flurry damage/healing, damage reduction

ART DIRECTION
-------------
The title screen and Thornwatch Camp use the legacy tower artwork
selected for this project.

Environmental art is kept in separate text files so scenes can be
changed without editing Python code.

    art/castle.txt    Main tower / camp artwork
    art/cave.txt      Crystal Caves theme
    art/chest.txt     Loot chest
    art/door.txt      Floor ascent door

CHEST ART
---------
The chest room now uses a dedicated ASCII chest stored in:

    art/chest.txt


ITEM ART
--------
The following item arts are now included as separate files:

    art/items/small_potion.txt
    art/items/large_potion.txt
    art/items/bomb.txt
    art/items/smoke_bomb.txt
    art/items/whetstone.txt
    art/items/armor_patch.txt
    art/items/vitality_herb.txt

These are shown when loot is found and when consumables are used.


DOOR ART
--------
A dedicated ascent-door scene is now used between normal floors.

    art/door.txt

It appears when the player advances to the next floor.


SAFE HAVEN ART
--------------
The Safe Haven checkpoint room now uses dedicated ASCII art stored in:

    art/safe_haven.txt


MAIN MENU RAIN
--------------
The very first Witch Tower title screen now plays a short ASCII rain
animation immediately when the game launches.

The rain is intentionally limited to the main menu. The experimental
attack, critical, chest, boss, door, Safe Haven, level-up, and healing
animations are not included.

Existing combat shake and flash feedback remain unchanged.


DUAL SAVE SYSTEM
----------------
The game uses two separate save files:

    saves/savegame.json
        Normal autosave. Updated after every cleared floor.
        This is used by Continue Saved Climb.

    saves/safe_haven.json
        Protected death checkpoint. Updated only after Floors
        20, 40, 60, 80, ...

Example:
    Clear Floor 20 -> Safe Haven checkpoint created.
    Continue through Floors 21-37 -> savegame.json keeps updating.
    Quit on Floor 37 -> Continue resumes from the latest autosave.
    Die on Floor 37 -> safe_haven.json is loaded instead.
    The run returns to the Floor 20 Safe Haven snapshot and resumes on 21.

Before reaching Floor 20, death permanently ends the run.


ANIMATION LAB
-------------
Run:

    python effects_test.py

Available preview animations:
- attack slash
- critical hit
- boss door opening
- Safe Haven reveal
- level-up
- healing
- full showcase

The chest animation is intentionally NOT included.

The rain animation remains on the first title screen when the game launches.


WINDOWS EXE BUILD
-----------------
A GitHub Actions + PyInstaller build is included.

See:

    GITHUB_BUILD_WINDOWS.txt

The workflow creates a standalone 64-bit Windows console executable:

    WitchTower.exe

In the packaged build, saves are stored beside WitchTower.exe so autosaves
and Safe Haven death checkpoints persist normally.


FIVE-DEATH PERMADEATH RULE
--------------------------
Each run has a maximum of 5 total deaths.

- Before Floor 20, the original permadeath rule still applies:
  the first death ends the run because no Safe Haven exists yet.
- After reaching a Safe Haven, deaths 1 through 4 rewind the character
  to the latest 20-floor death checkpoint.
- Death #5 permanently erases the entire run, even if the player has
  reached one or more Safe Havens.
- The death counter never rewinds when loading a Safe Haven.
- Quitting and reopening the game does not reset the counter.
- Starting a completely new run resets the counter to 0.

Run-wide death history is stored in:

    saves/run_meta.json

In the Windows EXE build it is stored beside WitchTower.exe with the
other save files.


HEART / LIFE HUD
----------------
The top-left corner shows the run's remaining death limit using ASCII hearts:

    LIVES  <3 <3 <3 <3 <3

Each recorded death removes one permanently:

    Deaths 0 -> <3 <3 <3 <3 <3
    Deaths 1 -> <3 <3 <3 <3
    Deaths 2 -> <3 <3 <3
    Deaths 3 -> <3 <3
    Deaths 4 -> <3
    Deaths 5 -> --  FINAL PERMADEATH

The display reads saves/run_meta.json, so Safe Haven rewinds cannot restore
a lost heart.

Important: the original pre-Floor-20 permadeath rule still applies. The
five-heart limit becomes useful once a Safe Haven has been reached.


LIVE GAMEPLAY ANIMATIONS
------------------------
The approved animation set is now wired into normal gameplay:

- Basic Attack -> slash animation
- Critical basic/skill hit -> critical impact animation
- Healing potion -> animated HP recovery
- Second Wind -> animated HP recovery
- Recovery Room heal -> animated HP recovery
- Boss gate -> animated door opening
- Floor 20/40/60... -> Safe Haven reveal
- Level-up after combat -> level-up animation
- First launch -> rain animation

Still intentionally excluded:
- chest opening animation
- boss entrance animation
- boss death animation

The Effect Lab remains available for preview/testing.


ANIMATION SPEED
---------------
Gameplay animations were slowed down for readability.

The main timing control is in:

    animations.py

Change:

    ANIMATION_SPEED = 1.8

Examples:

    1.0 = original fast speed
    1.5 = moderately slower
    1.8 = current setting
    2.0 = twice as slow

The title-screen rain uses separate RAIN_FRAMES and RAIN_DELAY values
inside ui.py.


BLUE / RED BOSS DOORS
---------------------
After every boss, the player chooses one of two paths:

    BLUE DOOR
        Keep the current difficulty multiplier.

    RED DOOR
        Double the current difficulty multiplier.

The system is cumulative:

    Start      x1
    RED        x2
    RED again  x4
    RED again  x8
    BLUE       keeps the current value

Difficulty currently scales:
- Enemy HP
- Enemy Attack

It intentionally does NOT scale enemy Defense, XP, or Gold. Scaling defense
at the same time as HP would make a 2x choice much harsher than an actual
2x increase because player damage would also drop.

The selected multiplier is part of Player save data, so it persists through
autosaves and is restored correctly by 20-floor Safe Haven death checkpoints.
