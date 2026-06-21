class Player:

    def __init__(self, name):

        self.name = name

        self.max_hp = 30
        self.hp = 30

        self.max_mana = 10
        self.mana = 1

        self.max_gold = 1500
        self.gold = 145

        self.deck = []

        self.gods_blessing = False
        self.last_chance_timer = -1


# =========================
# КОЛОДА
# =========================

def create_deck():

    return [
        {"name": "Огненный маг", "damage": 5, "mana": 3},
        {"name": "Рыцарь", "damage": 4, "mana": 2},
        {"name": "Лучник", "damage": 3, "mana": 1},
        {"name": "Дракон", "damage": 12, "mana": 8},
        {"name": "Гоблин", "damage": 2, "mana": 1},
        {"name": "Тёмный паладин", "damage": 7, "mana": 5},
        {"name": "Ледяной воин", "damage": 5, "mana": 3},
        {"name": "Зелье здоровья", "heal": 5, "mana": 2},
        {"name": "Зелье маны", "mana_gain": 4, "mana": 2},
        {"name": "Шило на мыло", "effect": "trade", "mana": 3},
        {"name": "Признание богов", "effect": "gods", "mana": 4},
        {"name": "Последний шанс", "effect": "last_chance", "mana": 6},
    ]