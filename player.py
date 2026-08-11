from dataclasses import dataclass, field
from data import CLASS_DATA, ITEM_DATA


@dataclass
class Player:
    name: str
    class_id: str
    level: int
    xp: int
    floor: int
    hp: int
    max_hp: int
    attack: int
    defense: int
    speed: int
    crit: float
    evade: float
    gold: int = 0
    skill_cooldown: int = 0
    inventory: dict = field(default_factory=dict)
    skill_points: int = 0
    skill_ranks: dict = field(default_factory=dict)

    @classmethod
    def create(cls, name, class_id):
        data = CLASS_DATA[class_id]
        return cls(
            name=name,
            class_id=class_id,
            level=1,
            xp=0,
            floor=1,
            hp=data["max_hp"],
            max_hp=data["max_hp"],
            attack=data["attack"],
            defense=data["defense"],
            speed=data["speed"],
            crit=data["crit"],
            evade=data["evade"],
            gold=0,
            skill_cooldown=0,
            inventory={"Small Potion": 2},
            skill_points=1,
            skill_ranks={},
        )

    @property
    def class_name(self):
        return CLASS_DATA[self.class_id]["name"]

    @property
    def skill_name(self):
        return CLASS_DATA[self.class_id]["skill"]

    def xp_to_next(self):
        return 35 + (self.level - 1) * 25

    def add_xp(self, amount):
        self.xp += amount
        levels = 0
        while self.xp >= self.xp_to_next():
            needed = self.xp_to_next()
            self.xp -= needed
            self.level_up()
            levels += 1
        return levels

    def level_up(self):
        self.level += 1
        self.skill_points += 1
        growth = CLASS_DATA[self.class_id]

        hp_gain = 5
        atk_gain = 1
        def_gain = 1

        if self.class_id == "warrior":
            hp_gain = 8
            if self.level % 2 == 0:
                atk_gain += 1
        elif self.class_id == "ranger":
            hp_gain = 5
            self.crit = min(0.40, self.crit + 0.01)
        elif self.class_id == "wizard":
            hp_gain = 4
            atk_gain = 2
        elif self.class_id == "thief":
            hp_gain = 5
            self.evade = min(0.35, self.evade + 0.01)
            if self.level % 3 == 0:
                atk_gain += 1
        elif self.class_id == "monk":
            hp_gain = 6
            if self.level % 2 == 0:
                def_gain += 1

        self.max_hp += hp_gain
        self.attack += atk_gain
        self.defense += def_gain
        self.speed += 1 if self.level % 3 == 0 else 0
        self.hp = self.max_hp

    def add_item(self, item, count=1):
        self.inventory[item] = self.inventory.get(item, 0) + count

    def remove_item(self, item, count=1):
        current = self.inventory.get(item, 0)
        if current < count:
            return False
        current -= count
        if current <= 0:
            self.inventory.pop(item, None)
        else:
            self.inventory[item] = current
        return True

    def has_item(self, item):
        return self.inventory.get(item, 0) > 0

    def heal(self, amount):
        old = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old

    def full_heal(self):
        self.hp = self.max_hp
        self.skill_cooldown = 0

    def use_field_item(self, item):
        if item not in ITEM_DATA or not self.has_item(item):
            return "You cannot use that item."

        data = ITEM_DATA[item]
        kind = data["type"]

        if kind == "heal":
            if self.hp >= self.max_hp:
                return "Your HP is already full."
            self.remove_item(item)
            restored = self.heal(data["value"])
            return f"You restore {restored} HP."

        if kind == "upgrade_attack":
            self.remove_item(item)
            self.attack += data["value"]
            return f"Attack permanently increased by {data['value']}."

        if kind == "upgrade_defense":
            self.remove_item(item)
            self.defense += data["value"]
            return f"Defense permanently increased by {data['value']}."

        if kind == "upgrade_hp":
            self.remove_item(item)
            self.max_hp += data["value"]
            self.hp += data["value"]
            return f"Max HP permanently increased by {data['value']}."

        return "That item can only be used during combat."

    def to_dict(self):
        return {
            "name": self.name,
            "class_id": self.class_id,
            "level": self.level,
            "xp": self.xp,
            "floor": self.floor,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "speed": self.speed,
            "crit": self.crit,
            "evade": self.evade,
            "gold": self.gold,
            "skill_cooldown": self.skill_cooldown,
            "inventory": self.inventory,
            "skill_points": self.skill_points,
            "skill_ranks": self.skill_ranks,
        }

    @classmethod
    def from_dict(cls, data):
        # Backward compatibility with saves made before the skill tree existed.
        data = dict(data)
        data.setdefault("skill_points", max(1, data.get("level", 1)))
        data.setdefault("skill_ranks", {})
        return cls(**data)
