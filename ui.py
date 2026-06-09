def show_menu():

    print("\n==============================")
    print("         CARD GAME")
    print("==============================")
    print("1. Играть")
    print("2. Выход")

    return input("\nВыберите действие: ")


# ======================
# СОСТОЯНИЕ ИГРЫ
# ======================

def show_status(player, enemy):

    print("\n===== СОСТОЯНИЕ =====")

    print(f"{player.name}: {player.hp}/{player.max_hp} HP | Мана: {player.mana}/{player.max_mana}")
    print(f"{enemy.name}: {enemy.hp}/{enemy.max_hp} HP | Мана: {enemy.mana}/{enemy.max_mana}")