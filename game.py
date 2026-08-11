import random

from data import CLASS_DATA
from player import Player
from tower import Tower
from enemy import make_enemy
from items import roll_loot, item_description
from combat import run_combat
import skills
import save_system
import ui
from art_loader import load_art, load_item_art


class Game:
    def __init__(self):
        self.player = None
        self.tower_seed = None
        self.tower = None

    def run(self):
        while True:
            ui.camp_screen(save_system.has_save(), save_system.has_checkpoint())

            options = []
            if save_system.has_save():
                options.append(("continue", "Continue saved climb"))
                options.append(("manage", "Manage saved hunter"))
            options.extend([
                ("new", "Start a new climb"),
                ("effects", "Open Effect Lab"),
                ("help", "How to play"),
                ("quit", "Leave camp"),
            ])

            choice = ui.menu([label for _, label in options], "Camp")
            action = options[choice - 1][0]

            if action == "continue":
                self.load()
                self.tower_loop()

            elif action == "new":
                if self.new_game():
                    self.tower_loop()

            elif action == "manage":
                self.load()
                self.camp_manage_menu()

            elif action == "effects":
                ui.effect_demo()

            elif action == "help":
                self.help_screen()

            elif action == "quit":
                ui.clear()
                print("The campfire fades behind you.")
                return

    def new_game(self):
        if save_system.has_save():
            ui.clear()
            saved_floor = save_system.current_floor()
            safe_floor = save_system.checkpoint_floor()

            warning_lines = [
                f"A saved climb currently resumes on Floor {saved_floor}.",
            ]
            if safe_floor is not None:
                warning_lines.append(
                    f"Death checkpoint: Safe Haven after Floor {safe_floor}."
                )
            else:
                warning_lines.append(
                    "No death checkpoint has been reached yet."
                )

            warning_lines.extend([
                "",
                "Starting a NEW climb permanently erases this run.",
            ])

            ui.box(warning_lines, title="NEW RUN WARNING", border="=")
            print()
            confirm = ui.menu([
                "Erase saved climb and start a new run",
                "Cancel",
            ], "New run")
            if confirm == 2:
                return False

        ui.clear()
        ui.box([
            "Five classes enter the tower in different ways.",
            "There is no final floor. Climb as high as you can.",
            "",
            "PERMADEATH RULE:",
            "No checkpoint exists until you clear Floor 20.",
        ], title="CHOOSE A CLASS", border="=")
        print()

        class_ids = list(CLASS_DATA.keys())
        labels = []
        for cid in class_ids:
            data = CLASS_DATA[cid]
            labels.append(
                f"{data['name']}: {data['description']} "
                f"[HP {data['max_hp']} ATK {data['attack']} DEF {data['defense']}]"
            )

        choice = ui.menu(labels, "Class")
        class_id = class_ids[choice - 1]

        name = input("\nHunter name [Sarah] > ").strip() or "Sarah"

        # A new run replaces the old character/checkpoint.
        save_system.delete_save()

        self.player = Player.create(name, class_id)
        self.tower_seed = random.randint(100000, 999999999)
        self.tower = Tower(self.tower_seed)

        ui.clear()
        ui.box([
            f"{self.player.name}, the {self.player.class_name}, stands at the tower entrance.",
            "",
            "Every five floors share one theme and end with a boss.",
            "Boss floors: 5, 10, 15, 20, 25, 30...",
            "Recovery rooms appear after every boss.",
            "Progress autosaves after every cleared floor.",
            "Floors 20, 40, 60... also create death checkpoints.",
            "",
            "Die before Floor 20 and this run is gone.",
        ], title="THE CLIMB BEGINS", border="=")
        ui.pause()

        # A new climb can be continued immediately from Floor 1.
        save_system.save_game(self.player, self.tower_seed)

        self.skill_tree_menu()
        save_system.save_game(self.player, self.tower_seed)
        return True

    def load(self):
        self.player, self.tower_seed = save_system.load_game()
        self.tower = Tower(self.tower_seed)

    def tower_loop(self):
        while self.player and self.player.hp > 0:
            floor = self.player.floor
            theme = self.tower.theme_for_floor(floor)
            boss = self.tower.is_boss_floor(floor)

            if boss:
                result = self.boss_floor(theme)
            else:
                room = self.tower.room_for_floor(floor)
                result = self.normal_floor(theme, room)

            if result == "dead":
                if self.handle_death():
                    # Safe Haven snapshot restored. Continue immediately.
                    continue
                return

            if result == "camp":
                return

            if result == "cleared":
                completed_floor = self.player.floor

                if boss:
                    is_safe_haven = completed_floor % 20 == 0
                    self.ascend_transition(
                        completed_floor + 1,
                        safe_haven=is_safe_haven,
                    )

                self.player.floor += 1

                if boss:
                    if completed_floor % 20 == 0:
                        action = self.safe_haven(completed_floor)
                    else:
                        action = self.recovery_room(completed_floor)

                    if action == "camp":
                        return
                else:
                    # Every cleared normal floor becomes the latest Continue point.
                    save_system.save_game(self.player, self.tower_seed)

    def ascend_transition(self, next_floor, safe_haven=False):
        ui.clear()
        print(load_art("door"))
        print()

        if safe_haven:
            destination = "A permanent Safe Haven waits beyond the ancient door."
            title = "SAFE HAVEN GATE"
        else:
            destination = "A recovery chamber waits beyond the ancient door."
            title = "BOSS GATE"

        ui.box([
            f"The path to Floor {next_floor} is now open.",
            "",
            "The guardian is dead. Ancient stone doors part.",
            destination,
        ], title=title, border="=")
        ui.pause()

    def normal_floor(self, theme, room):
        room_names = {
            "enemy": "Hostile Chamber",
            "chest": "Forgotten Cache",
            "shrine": "Strange Shrine",
            "trap": "Broken Passage",
            "cache": "Abandoned Hunter Camp",
        }
        ui.floor_screen(self.player, theme, room_names[room])

        if theme["id"] == "cave":
            print(load_art("cave"))
            print()

        if room == "enemy":
            enemy = make_enemy(theme, self.player.floor, boss=False)
            result = run_combat(self.player, enemy)
            if result == "dead":
                return "dead"
            if result == "escaped":
                print("You find another staircase and leave the room behind.")
                ui.pause()
            else:
                self.random_drop(boss=False)
            return "cleared"

        if room == "chest":
            print(load_item_art("Chest"))
            print()
            print("A locked chest sits beneath a layer of dust.")
            ui.pause("Press ENTER to open it...")
            item, count = roll_loot(self.player.floor)
            gold = random.randint(5, 12) + self.player.floor
            self.player.gold += gold
            if item:
                self.player.add_item(item, count)
                art = load_item_art(item)
                if art:
                    print(art)
                    print()
                print(f"You found: {item} x{count}")
                print(item_description(item))
            print(f"You also found {gold} gold.")
            ui.pause()
            return "cleared"

        if room == "shrine":
            print("A quiet stone shrine hums with warm light.\n")
            choice = ui.menu([
                "Restore 35% HP",
                "Gain +1 Attack for this run",
                "Gain +1 Defense for this run",
            ], "Shrine")

            if choice == 1:
                restored = self.player.heal(max(1, self.player.max_hp * 35 // 100))
                print(f"You restore {restored} HP.")
            elif choice == 2:
                self.player.attack += 1
                print("Attack increased by 1.")
            else:
                self.player.defense += 1
                print("Defense increased by 1.")
            ui.pause()
            return "cleared"

        if room == "trap":
            print("The floor clicks beneath your boot.")
            chance = min(0.75, 0.25 + self.player.speed * 0.04)
            if random.random() < chance:
                print("You react in time and avoid the trap.")
            else:
                damage = max(2, 5 + self.player.floor // 2 - self.player.defense // 3)
                self.player.hp -= damage
                ui.flash_message(f"TRAP  -{damage} HP", 0.10)
                print(f"A hidden mechanism hits you for {damage} damage.")
                if self.player.hp <= 0:
                    ui.pause()
                    return "dead"
            ui.pause()
            return "cleared"

        # Hunter cache
        print("Someone camped here long ago. A few supplies remain.")
        self.player.add_item("Small Potion", 1)
        print(load_item_art("Small Potion"))
        print()
        if random.random() < 0.45:
            self.player.add_item("Bomb", 1)
            print(load_item_art("Bomb"))
            print()
            print("Found: Small Potion x1 and Bomb x1")
        else:
            print("Found: Small Potion x1")
        ui.pause()
        return "cleared"

    def boss_floor(self, theme):
        ui.floor_screen(self.player, theme, "Guardian Arena", boss=True)

        if theme["id"] == "cave":
            print(load_art("cave"))
            print()

        print("The staircase locks behind you.")
        print("Something massive moves in the dark.")
        ui.pause()

        enemy = make_enemy(theme, self.player.floor, boss=True)
        result = run_combat(self.player, enemy)

        if result == "dead":
            return "dead"

        self.random_drop(boss=True)
        return "cleared"

    def random_drop(self, boss=False):
        item, count = roll_loot(self.player.floor, boss=boss)
        if item:
            self.player.add_item(item, count)
            art = load_item_art(item)
            if art:
                print()
                print(art)
            print(f"\nLoot: {item} x{count}")
            print(item_description(item))
            ui.pause()

    def recovery_room(self, completed_floor):
        """
        Boss rest room after Floors 5, 10, 15, 25, 30, 35...

        Current progress is autosaved here, but the protected death
        checkpoint remains the most recent 20-floor Safe Haven.
        """
        self.player.full_heal()
        save_system.save_game(self.player, self.tower_seed)

        while True:
            ui.recovery_room_screen(self.player, completed_floor)
            print(
                "\nHP restored. Current progress autosaved.\n"
                "Death still returns to the last 20-floor Safe Haven.\n"
            )

            choices = [
                "Continue climbing",
                "Open inventory",
                f"Open skill tree ({self.player.skill_points} points)",
                "Return to Thornwatch Camp",
            ]
            choice = ui.menu(choices, "Recovery room")

            if choice == 1:
                save_system.save_game(self.player, self.tower_seed)
                return "continue"
            if choice == 2:
                self.inventory_menu()
                save_system.save_game(self.player, self.tower_seed)
            if choice == 3:
                self.skill_tree_menu()
                save_system.save_game(self.player, self.tower_seed)
            if choice == 4:
                save_system.save_game(self.player, self.tower_seed)
                return "camp"

    def safe_haven(self, completed_floor):
        """
        Protected death checkpoint after Floors 20, 40, 60...

        Normal progress continues to autosave on every floor. This separate
        snapshot is used only when the player dies.
        """
        self.player.full_heal()
        save_system.save_game(self.player, self.tower_seed)
        save_system.save_checkpoint(
            self.player,
            self.tower_seed,
            safe_haven_floor=completed_floor,
        )

        while True:
            ui.safe_haven_screen(self.player, completed_floor)
            print(
                "\nHP restored. Current progress autosaved.\n"
                "DEATH CHECKPOINT UPDATED.\n"
            )

            choice = ui.menu([
                "Continue climbing",
                "Open inventory",
                f"Open skill tree ({self.player.skill_points} points)",
                "Return to Thornwatch Camp",
            ], "Safe Haven")

            if choice == 1:
                save_system.save_game(self.player, self.tower_seed)
                save_system.save_checkpoint(
                    self.player, self.tower_seed, completed_floor
                )
                return "continue"
            if choice == 2:
                self.inventory_menu()
                save_system.save_game(self.player, self.tower_seed)
                save_system.save_checkpoint(
                    self.player, self.tower_seed, completed_floor
                )
            if choice == 3:
                self.skill_tree_menu()
                save_system.save_game(self.player, self.tower_seed)
                save_system.save_checkpoint(
                    self.player, self.tower_seed, completed_floor
                )
            if choice == 4:
                save_system.save_game(self.player, self.tower_seed)
                save_system.save_checkpoint(
                    self.player, self.tower_seed, completed_floor
                )
                return "camp"

    def inventory_menu(self):
        while True:
            ui.clear()
            ui.player_panel(self.player)
            print("\nINVENTORY\n")

            items = sorted(self.player.inventory.items())
            if not items:
                print("  Empty")
                ui.pause()
                return

            labels = []
            for name, count in items:
                labels.append(f"{name} x{count} - {item_description(name)}")
            labels.append("Back")

            choice = ui.menu(labels, "Inventory")
            if choice == len(labels):
                return

            item = items[choice - 1][0]
            art = load_item_art(item)
            if art:
                print()
                print(art)
            message = self.player.use_field_item(item)
            print("\n" + message)
            ui.pause()

    def skill_tree_menu(self):
        while True:
            nodes = skills.tree_for(self.player)
            ui.clear()
            ui.box([
                f"Hunter       : {self.player.name}",
                f"Class        : {self.player.class_name}",
                f"Skill Points : {self.player.skill_points}",
                "",
                "Spend 1 point to increase an available skill by one rank.",
            ], title="SKILL TREE", border="=")
            print()

            for tier in (1, 2, 3):
                print("+" + "-" * ui.WIDTH + "+")
                print("|" + f" TIER {tier} ".center(ui.WIDTH) + "|")
                print("+" + "-" * ui.WIDTH + "+")
                for node in nodes:
                    if node["tier"] != tier:
                        continue
                    current = skills.rank(self.player, node["id"])
                    state = skills.status(self.player, node)
                    print(f"  {node['name']} [{current}/{node['max_rank']}] - {state}")
                    print(f"      {node['description']}")
                    if node["requires"]:
                        print(f"      Requires: {skills.requirement_text(self.player, node)}")
                print()

            labels = []
            node_ids = []
            for node in nodes:
                current = skills.rank(self.player, node["id"])
                state = skills.status(self.player, node)
                labels.append(
                    f"{node['name']} [{current}/{node['max_rank']}] - {state}"
                )
                node_ids.append(node["id"])
            labels.append("Back")

            choice = ui.menu(labels, "Skill")
            if choice == len(labels):
                return

            success, message = skills.purchase(self.player, node_ids[choice - 1])
            print("\n" + message)
            ui.pause()

    def camp_manage_menu(self):
        while True:
            ui.clear()
            ui.player_panel(self.player)
            print()
            choice = ui.menu([
                "Open inventory",
                f"Open skill tree ({self.player.skill_points} points)",
                "Save changes and return to camp",
            ], "Hunter")

            if choice == 1:
                self.inventory_menu()
            elif choice == 2:
                self.skill_tree_menu()
            else:
                save_system.save_game(self.player, self.tower_seed)
                return

    def handle_death(self):
        death_name = self.player.name
        death_floor = self.player.floor

        # Regular floor autosaves are NOT resurrection points.
        if not save_system.has_checkpoint():
            ui.death_rewind_screen(death_name, death_floor, safe_floor=None)
            save_system.delete_save()
            self.player = None
            self.tower = None
            self.tower_seed = None
            ui.pause()
            return False

        safe_floor = save_system.checkpoint_floor()
        ui.death_rewind_screen(death_name, death_floor, safe_floor=safe_floor)
        ui.pause("Press ENTER to return to the Safe Haven...")

        # Deliberately ignore savegame.json and load the protected 20-floor
        # checkpoint. Then make that rollback the new normal autosave.
        self.player, self.tower_seed = save_system.restore_checkpoint_to_current()
        self.tower = Tower(self.tower_seed)

        ui.safe_haven_screen(self.player, safe_floor)
        print(
            f"\nDeath rollback complete. You resume at Floor {self.player.floor}.\n"
            f"Autosaved progress after the Floor {safe_floor} Safe Haven was lost."
        )
        ui.pause()
        return True

    def help_screen(self):
        ui.clear()
        ui.box([
            "THE TOWER",
            "Each group of five floors has one randomly selected theme.",
            "Floors 5, 10, 15, 20, etc. are boss floors.",
            "A recovery room appears after each boss.",
            "",
            "SAFE HAVENS",
            "Every cleared floor creates a normal autosave.",
            "Floors 20, 40, 60, 80... create protected death checkpoints.",
            "Normal autosaves are only for Continue, never resurrection.",
            "",
            "PERMADEATH",
            "Before Floor 20: death permanently ends the run.",
            "After a Safe Haven: death rewinds to the previous 20-floor checkpoint.",
            "Example: dying on Floor 37 returns to the Floor 20 checkpoint.",
            "",
            "COMBAT",
            "Attack, use your class skill, or spend inventory items.",
            "Skills use cooldowns instead of mana.",
            "",
            "LEVELS + SKILL TREE",
            "Enemies award XP. Every level grants 1 skill point.",
            "Each class has 10 skills across three tiers.",
        ], title="HOW TO PLAY", border="=")
        ui.pause()

