import tkinter as tk
from tkinter import messagebox
import random
import time

from cards import Player, create_deck


# =========================
# ИГРА
# =========================

class CardGame:

    def __init__(self, root):

        self.root = root

        self.window_width = 1200
        self.window_height = 820

        self.root.title("DARK FANTASY CARD GAME")
        self.root.geometry(
            f"{self.window_width}x{self.window_height}"
        )

        self.root.configure(bg="#050505")

        self.player = Player("Игрок")
        self.enemy = Player("Компьютер")

        self.round_count = 1

        self.setup_game()

        if not self.root.winfo_exists():
            return

        self.create_ui()

        self.update_ui()

    # =========================
    # СЛОЖНОСТЬ
    # =========================

    def setup_game(self):

        start_game = messagebox.askyesno(
            "Запуск игры",
            "Начать игру?"
        )

        if not start_game:

            self.root.destroy()
            return

        difficulty = tk.Toplevel(self.root)

        difficulty.title("Выбор сложности")
        difficulty.geometry("350x320")
        difficulty.configure(bg="#0a0a0a")

        tk.Label(
            difficulty,
            text="ВЫБЕРИ СВОЮ СУДЬБУ",
            font=("Times New Roman", 18, "bold"),
            bg="#0a0a0a",
            fg="white"
        ).pack(pady=25)

        def set_difficulty(level):

            # ЛЁГКИЙ
            if level == 1:

                self.player.max_hp = 35
                self.player.hp = 35

                self.enemy.max_hp = 15
                self.enemy.hp = 15

            # СРЕДНИЙ
            elif level == 2:

                self.player.max_hp = 30
                self.player.hp = 30

                self.enemy.max_hp = 30
                self.enemy.hp = 30

            # ИСПЫТАНИЕ
            elif level == 3:

                self.player.max_hp = 25
                self.player.hp = 25

                self.enemy.max_hp = 40
                self.enemy.hp = 40

            difficulty.destroy()

        button_style = {
            "width": 20,
            "height": 2,
            "bg": "#111",
            "fg": "white",
            "font": ("Arial", 12, "bold"),
            "relief": "flat",
            "activebackground": "#222",
            "activeforeground": "white",
            "bd": 0
        }

        tk.Button(
            difficulty,
            text="ЛЁГКИЙ",
            command=lambda: set_difficulty(1),
            **button_style
        ).pack(pady=8)

        tk.Button(
            difficulty,
            text="СРЕДНИЙ",
            command=lambda: set_difficulty(2),
            **button_style
        ).pack(pady=8)

        tk.Button(
            difficulty,
            text="ИСПЫТАНИЕ",
            command=lambda: set_difficulty(3),
            **button_style
        ).pack(pady=8)

        self.root.wait_window(difficulty)

        # КОЛОДЫ

        all_cards = create_deck()

    # =========================
    # КАРТЫ ПО ТИПАМ
    # =========================

        green_cards = [
        card for card in all_cards
        if "damage" in card
    ]

        red_cards = [
        card for card in all_cards
        if (
                "heal" in card
                or card.get("effect") == "gods"
                or card.get("effect") == "last_chance"
        )
    ]

        blue_cards = [
        card for card in all_cards
        if (
                "mana_gain" in card
                or card.get("effect") == "trade"
        )
    ]

    # =========================
    # СТАРТОВЫЕ КОЛОДЫ
    # =========================

        self.player.deck = (
            random.sample(green_cards, 3)
            + random.sample(red_cards, 1)
            + random.sample(blue_cards, 1)
    )

        self.enemy.deck = (
                 random.sample(green_cards, 3)
                + random.sample(red_cards, 1)
                + random.sample(blue_cards, 1)
        )

        random.shuffle(self.player.deck)
        random.shuffle(self.enemy.deck)

    # =========================
    # ИНТЕРФЕЙС
    # =========================

    def create_ui(self):

        # =========================
        # АНИМИРОВАННЫЙ ФОН
        # =========================

        self.bg_canvas = tk.Canvas(
            self.root,
            bg="#050505",
            highlightthickness=0
        )

        self.bg_canvas.place(
            relwidth=1,
            relheight=1
        )

        self.fog_particles = []

        for i in range(50):

            x = random.randint(0, 1600)
            y = random.randint(0, 900)

            size = random.randint(60, 140)

            particle = self.bg_canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill="#111111",
                outline=""
            )

            self.fog_particles.append(particle)

        self.animate_background()

        # =========================
        # TITLE
        # =========================

        title = tk.Label(
            self.root,
            text="DARK FANTASY",
            font=("Times New Roman", 34, "bold"),
            bg="#050505",
            fg="white"
        )

        title.pack(pady=15)

        # =========================
        # КНОПКА МАГАЗИНА
        # =========================

        shop_button = tk.Button(
            self.root,
            text="МАГАЗИН",
            font=("Arial", 12, "bold"),
            bg="#222",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#444",
            activeforeground="white",
            command=self.open_shop
        )

        shop_button.place(
            x=self.window_width - 140,
            y=20,
            width=120,
            height=40
        )

        # =========================
        # ПАНЕЛЬ ИГРОКА
        # =========================

        self.player_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 16, "bold"),
            bg="#101010",
            fg="#dddddd",
            padx=20,
            pady=10
        )

        self.player_label.pack(pady=5)

        self.enemy_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 16, "bold"),
            bg="#101010",
            fg="#dddddd",
            padx=20,
            pady=10
        )

        self.enemy_label.pack(pady=5)

        self.round_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 15, "bold"),
            bg="#101010",
            fg="white",
            padx=20,
            pady=10
        )

        self.round_label.pack(pady=10)

        # =========================
        # ЛОГ
        # =========================

        self.log_text = tk.Text(
            self.root,
            width=90,
            height=12,
            bg="#0a0a0a",
            fg="#cccccc",
            insertbackground="white",
            relief="flat",
            font=("Consolas", 11)
        )

        self.log_text.pack(pady=10)

        # =========================
        # КОНТЕЙНЕР КАРТ
        # =========================

        cards_container = tk.Frame(
            self.root,
            bg="#050505"
        )

        cards_container.pack(fill="x", pady=20)

        # КНОПКА ВЛЕВО

        left_button = tk.Button(
            cards_container,
            text="⬅",
            font=("Arial", 18, "bold"),
            width=3,
            bg="#111",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#333",
            command=lambda:
            self.canvas.xview_scroll(-3, "units")
        )

        left_button.pack(side=tk.LEFT, padx=10)

        # CANVAS

        self.canvas = tk.Canvas(
            cards_container,
            bg="#050505",
            height=260,
            highlightthickness=0
        )

        self.canvas.pack(
            side=tk.LEFT,
            fill="x",
            expand=True
        )

        # КНОПКА ВПРАВО

        right_button = tk.Button(
            cards_container,
            text="➡",
            font=("Arial", 18, "bold"),
            width=3,
            bg="#111",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#333",
            command=lambda:
            self.canvas.xview_scroll(3, "units")
        )

        right_button.pack(side=tk.LEFT, padx=10)

        # FRAME КАРТ

        self.cards_frame = tk.Frame(
            self.canvas,
            bg="#050505"
        )

        self.canvas.create_window(
            (0, 0),
            window=self.cards_frame,
            anchor="nw"
        )

        # SCROLL

        def configure_scroll(event):

            self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )

        self.cards_frame.bind(
            "<Configure>",
            configure_scroll
        )

        # КОЛЕСО МЫШКИ

        def mouse_scroll(event):

            self.canvas.xview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        self.canvas.bind_all(
            "<MouseWheel>",
            mouse_scroll
        )
        # =========================
        # КНОПКА ПРОПУСКА ХОДА
        # =========================

        skip_button = tk.Button(
            self.root,
            text="ПРОПУСТИТЬ ХОД",
            font=("Arial", 14, "bold"),
            bg="#222",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#444",
            activeforeground="white",
            padx=20,
            pady=10,
            command=self.skip_turn
        )

        skip_button.pack(pady=15)

    # =========================
    # АНИМАЦИЯ ФОНА
    # =========================

    def animate_background(self):

        for particle in self.fog_particles:

            self.bg_canvas.move(particle, 1, 0)

            coords = self.bg_canvas.coords(particle)

            if coords[0] > 1500:

                y = random.randint(0, 900)

                self.bg_canvas.coords(
                    particle,
                    -150,
                    y,
                    -20,
                    y + 120
                )

        self.root.after(
            60,
            self.animate_background
        )

    # =========================
    # ВСПЫШКА УРОНА
    # =========================

    def damage_flash(self):

        old = self.root["bg"]

        self.root.configure(bg="#220000")

        self.root.after(
            120,
            lambda:
            self.root.configure(bg=old)
        )

    # =========================
    # ТРЯСКА ЭКРАНА
    # =========================

    def shake_screen(self):

        x = self.root.winfo_x()
        y = self.root.winfo_y()

        for i in range(8):

            dx = random.randint(-10, 10)
            dy = random.randint(-10, 10)

            self.root.geometry(
                f"{self.window_width}x{self.window_height}+{x+dx}+{y+dy}"
            )

            self.root.update()

            time.sleep(0.02)

        self.root.geometry(
            f"{self.window_width}x{self.window_height}+{x}+{y}"
        )

    # =========================
    # ЧАСТИЦЫ
    # =========================

    def create_particles(self, color):

        particles = []

        for i in range(15):

            x = random.randint(450, 750)
            y = random.randint(150, 350)

            p = self.bg_canvas.create_oval(
                x,
                y,
                x + 8,
                y + 8,
                fill=color,
                outline=""
            )

            particles.append(p)

        def animate(step=0):

            if step > 20:

                for p in particles:

                    try:
                        self.bg_canvas.delete(p)
                    except:
                        pass

                return

            for p in particles:

                dx = random.randint(-8, 8)
                dy = random.randint(-8, 8)

                self.bg_canvas.move(p, dx, dy)

            self.root.after(
                30,
                lambda:
                animate(step + 1)
            )

        animate()

    # =========================
    # ОБНОВЛЕНИЕ UI
    # =========================

    def update_ui(self):

        self.player_label.config(
            text=f"Игрок: {self.player.hp}/{self.player.max_hp} HP | Мана: {self.player.mana}/{self.player.max_mana} | Монеты: {self.player.gold}"
        )

        self.enemy_label.config(
            text=f"Компьютер: {self.enemy.hp}/{self.enemy.max_hp} HP | Мана: {self.enemy.mana}/{self.enemy.max_mana} | Монеты: {self.enemy.gold}"
        )

        self.round_label.config(
            text=f"КРУГ {self.round_count}"
        )

        # УДАЛЕНИЕ КАРТ

        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        # СОЗДАНИЕ КАРТ

        for card in self.player.deck:

            # СИНИЕ КАРТЫ

            free_mana_card = (
                "mana_gain" in card
                or card.get("effect") == "trade"
            )

            # ТЕКСТ

            if free_mana_card:

                text = (
                    f"{card['name']}\n"
                    f"Мана: БЕСПЛАТНО"
                )

            else:

                text = (
                    f"{card['name']}\n"
                    f"Мана: {card['mana']}"
                )

            if "damage" in card:
                text += f"\nУрон: {card['damage']}"

            elif "heal" in card:
                text += f"\nЛечение: {card['heal']}"

            elif "mana_gain" in card:
                text += f"\n+{card['mana_gain']} маны"

            else:
                text += "\nЭффект"

            # ОБВОДКА

            border_color = "#555"

            # ЗЕЛЁНЫЕ

            if "damage" in card:
                border_color = "#00ff99"

            # КРАСНЫЕ

            elif (
                "heal" in card
                or card.get("effect") == "gods"
                or card.get("effect") == "last_chance"
            ):
                border_color = "#ff4444"

            # СИНИЕ

            elif (
                "mana_gain" in card
                or card.get("effect") == "trade"
            ):
                border_color = "#3399ff"

            # FRAME

            card_frame = tk.Frame(
                self.cards_frame,
                bg=border_color,
                padx=3,
                pady=3
            )

            card_frame.pack(
                side=tk.LEFT,
                padx=10,
                pady=10
            )

            # КАРТА

            button = tk.Button(
                card_frame,
                text=text,
                width=16,
                height=8,
                bg="#151515",
                fg="white",
                relief="flat",
                bd=0,
                activebackground="#333",
                activeforeground="white",
                font=("Arial", 10, "bold"),
                command=lambda c=card:
                self.play_card(c)
            )

            button.pack()

            # HOVER

            def on_enter(event, frame=card_frame):

                frame.config(
                    padx=6,
                    pady=6
                )

                button.config(bg="#2b2b2b")

            def on_leave(event, frame=card_frame):

                frame.config(
                    padx=3,
                    pady=3
                )

                button.config(bg="#151515")

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        self.canvas.update_idletasks()

        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    # =========================
    # ЛЕЧЕНИЕ
    # =========================

    def heal_player(self, player, amount):

        player.hp += amount

        if player.hp > player.max_hp:
            player.hp = player.max_hp

    # =========================
    # ЭФФЕКТЫ
    # =========================

    def apply_effects(self, player):

        # МАНА РАСТЁТ

        mana_gain = random.randint(1, 3)
        player.mana += mana_gain

        if player.mana > player.max_mana:
            player.mana = player.max_mana

        # ПРИЗНАНИЕ БОГОВ

        if player.gods_blessing:

            self.heal_player(player, 2)

            self.log(
                f"{player.name} получает +2 HP"
            )

        # ПОСЛЕДНИЙ ШАНС

        if player.last_chance_timer >= 0:

            player.last_chance_timer += 1

            if player.last_chance_timer >= 3:

                player.hp -= 20

                self.shake_screen()

                self.damage_flash()

                self.log(
                    f"{player.name} получает -20 HP!"
                )

                player.last_chance_timer = -1

    # =========================
    # ЛОГ
    # =========================

    def log(self, text):

        self.log_text.insert(
            tk.END,
            text + "\n"
        )

        self.log_text.see(tk.END)

    # =========================
    # ХОД ИГРОКА
    # =========================

    def play_card(self, card):
        # =========================
        # ПРОПУСК ХОДА
        # =========================

        def skip_turn(self):

            self.log(
                "Игрок пропускает ход"
            )

            # БОТ ХОДИТ

            self.enemy_turn()

            # НОВЫЙ РАУНД

            self.round_count += 1

            # ЭФФЕКТЫ ИГРОКА

            self.apply_effects(self.player)

            # ОБНОВЛЕНИЕ UI

            self.update_ui()

        free_mana_card = (
            "mana_gain" in card
            or card.get("effect") == "trade"
        )

        # ПРОВЕРКА МАНЫ

        if not free_mana_card:

            if self.player.mana < card["mana"]:

                messagebox.showwarning(
                    "Ошибка",
                    "Недостаточно маны!"
                )

                return

            self.player.mana -= card["mana"]

        self.player.deck.remove(card)

        self.log(
            f"Игрок использовал: {card['name']}"
        )

        # УРОН

        if "damage" in card:

            self.enemy.hp -= card["damage"]

            self.shake_screen()

            self.damage_flash()

            self.create_particles("red")

            self.log(
                f"Нанесено {card['damage']} урона"
            )

        # ЛЕЧЕНИЕ

        elif "heal" in card:

            self.heal_player(
                self.player,
                card["heal"]
            )

            self.create_particles("white")

            self.log(
                f"Игрок восстановил {card['heal']} HP"
            )

        # МАНА

        elif "mana_gain" in card:

            self.player.mana += card["mana_gain"]

            if self.player.mana > self.player.max_mana:
                self.player.mana = self.player.max_mana

            self.create_particles("blue")

            self.log(
                f"+{card['mana_gain']} маны"
            )

        # ШИЛО НА МЫЛО

        elif card.get("effect") == "trade":

            chance = random.randint(1, 2)

            if chance == 1:

                self.player.hp -= 3

                self.damage_flash()

                self.log(
                    "Шило на мыло: -3 HP"
                )

            else:

                self.player.mana += 4

                self.create_particles("blue")

                self.log(
                    "Шило на мыло: +4 маны"
                )

        # ПРИЗНАНИЕ БОГОВ

        elif card.get("effect") == "gods":

            self.player.gods_blessing = True

            self.create_particles("white")

            self.log(
                "Активировано признание богов"
            )

        # ПОСЛЕДНИЙ ШАНС

        elif card.get("effect") == "last_chance":

            self.heal_player(
                self.player,
                30
            )

            self.player.last_chance_timer = 0

            self.create_particles("red")

            self.log(
                "Последний шанс активирован"
            )

        self.check_game()

        # +35 МОНЕТ ПОСЛЕ ХОДА

        self.player.gold += 35

        if self.player.gold > self.player.max_gold:
            self.player.gold = self.player.max_gold

        self.enemy_turn()

        self.round_count += 1

        self.apply_effects(self.player)

        self.update_ui()

    # =========================
    # ПРОПУСК ХОДА
    # =========================
    def skip_turn(self):

        self.log(
            "Игрок пропускает ход"
        )

        self.enemy_turn()

        self.round_count += 1

        self.apply_effects(self.player)

        self.update_ui()

    # =========================
    # ХОД БОТА
    # =========================

    def enemy_turn(self):

        self.apply_effects(self.enemy)

        possible_cards = []

        for card in self.enemy.deck:

            free_mana_card = (
                "mana_gain" in card
                or card.get("effect") == "trade"
            )

            if free_mana_card:
                possible_cards.append(card)

            elif self.enemy.mana >= card["mana"]:
                possible_cards.append(card)

        if len(possible_cards) == 0:

            self.log(
                "Компьютер пропускает ход"
            )

            return

        card = random.choice(possible_cards)

        self.enemy.deck.remove(card)

        free_mana_card = (
            "mana_gain" in card
            or card.get("effect") == "trade"
        )

        if not free_mana_card:
            self.enemy.mana -= card["mana"]

        self.log(
            f"Компьютер использовал: {card['name']}"
        )

        # УРОН

        if "damage" in card:

            self.player.hp -= card["damage"]

            self.shake_screen()

            self.damage_flash()

            self.create_particles("red")

        # ЛЕЧЕНИЕ

        elif "heal" in card:

            self.heal_player(
                self.enemy,
                card["heal"]
            )

            self.create_particles("white")

        # МАНА

        elif "mana_gain" in card:

            self.enemy.mana += card["mana_gain"]

            self.create_particles("blue")

            # +35 МОНЕТ БОТУ

            self.enemy.gold += 35

            if self.enemy.gold > self.enemy.max_gold:
                self.enemy.gold = self.enemy.max_gold

        self.check_game()

    def open_shop(self):

        shop = tk.Toplevel(self.root)

        shop.title("Магазин")
        shop.geometry("900x500")
        shop.configure(bg="#0a0a0a")

        title = tk.Label(
            shop,
            text="МАГАЗИН КАРТ",
            font=("Times New Roman", 24, "bold"),
            bg="#0a0a0a",
            fg="white"
        )

        title.pack(pady=15)

        money_label = tk.Label(
            shop,
            text=f"Монеты: {self.player.gold}",
            font=("Arial", 14, "bold"),
            bg="#0a0a0a",
            fg="#ffd700"
        )

        money_label.pack(pady=10)

        # =========================
        # КОНТЕЙНЕР
        # =========================

        container = tk.Frame(
            shop,
            bg="#0a0a0a"
        )

        container.pack(fill="both", expand=True)

        # =========================
        # КНОПКА ВЛЕВО
        # =========================

        left_button = tk.Button(
            container,
            text="⬅",
            font=("Arial", 18, "bold"),
            width=3,
            bg="#111",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#333",
            command=lambda:
            canvas.xview_scroll(-3, "units")
        )

        left_button.pack(side=tk.LEFT, padx=10)

        # =========================
        # CANVAS
        # =========================

        canvas = tk.Canvas(
            container,
            bg="#0a0a0a",
            highlightthickness=0,
            height=350
        )

        canvas.pack(
            side=tk.LEFT,
            fill="both",
            expand=True
        )

        # =========================
        # КНОПКА ВПРАВО
        # =========================

        right_button = tk.Button(
            container,
            text="➡",
            font=("Arial", 18, "bold"),
            width=3,
            bg="#111",
            fg="white",
            relief="flat",
            bd=0,
            activebackground="#333",
            command=lambda:
            canvas.xview_scroll(3, "units")
        )

        right_button.pack(side=tk.LEFT, padx=10)

        # =========================
        # FRAME КАРТ
        # =========================

        cards_frame = tk.Frame(
            canvas,
            bg="#0a0a0a"
        )

        canvas.create_window(
            (0, 0),
            window=cards_frame,
            anchor="nw"
        )

        # =========================
        # SCROLL
        # =========================

        def configure_scroll(event):

            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        cards_frame.bind(
            "<Configure>",
            configure_scroll
        )

        # =========================
        # КОЛЕСО МЫШКИ
        # =========================

        def mouse_scroll(event):

            canvas.xview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        canvas.bind_all(
            "<MouseWheel>",
            mouse_scroll
        )

        # =========================
        # КАРТЫ
        # =========================

        all_cards = create_deck()

        prices = {

            "Огненный маг": 150,
            "Рыцарь": 160,
            "Лучник": 180,
            "Дракон": 400,
            "Гоблин": 80,

            "Тёмный паладин": 230,
            "Ледяной воин": 170,

            "Зелье здоровья": 120,
            "Зелье маны": 150,

            "Шило на мыло": 130,
            "Признание богов": 110,
            "Последний шанс": 190,
        }

        for card in all_cards:

            price = prices.get(card["name"], 100)

            text = card["name"]

            if "damage" in card:
                text += f"\nУрон: {card['damage']}"

            elif "heal" in card:
                text += f"\nЛечение: {card['heal']}"

            elif "mana_gain" in card:
                text += f"\nМана: +{card['mana_gain']}"

            else:
                text += "\nЭффект"

            text += f"\nЦена: {price}"

            frame = tk.Frame(
                cards_frame,
                bg="#222",
                padx=3,
                pady=3
            )

            frame.pack(
                side=tk.LEFT,
                padx=10,
                pady=10
            )

            def buy_card(c=card, p=price):

                if self.player.gold < p:
                    messagebox.showwarning(
                        "Ошибка",
                        "Недостаточно монет!"
                    )

                    return

                self.player.gold -= p

                self.player.deck.append(c.copy())

                money_label.config(
                    text=f"Монеты: {self.player.gold}"
                )

                self.update_ui()

                self.log(
                    f"Куплена карта: {c['name']}"
                )

            button = tk.Button(
                frame,
                text=text,
                width=18,
                height=9,
                bg="#151515",
                fg="white",
                relief="flat",
                bd=0,
                activebackground="#333",
                activeforeground="white",
                font=("Arial", 10, "bold"),
                command=buy_card
            )

            button.pack()

    # =========================
    # ПОБЕДА
    # =========================

    def check_game(self):

        if self.player.hp <= 0:

            messagebox.showinfo(
                "Игра окончена",
                "Компьютер победил!"
            )

            self.root.destroy()

        elif self.enemy.hp <= 0:

            messagebox.showinfo(
                "Игра окончена",
                "Вы победили!"
            )

            self.root.destroy()


# =========================
# ЗАПУСК
# =========================

root = tk.Tk()

app = CardGame(root)

if root.winfo_exists():
    root.mainloop()