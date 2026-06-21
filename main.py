import random
import sys

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QTimer,
    QUrl,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtMultimedia import QSoundEffect
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from cards import Player, create_deck
from design import APP_STYLE, CARD_PRICES, COLORS, AssetCache
from sounds import ensure_sounds, sound_path


class SoundManager:
    def __init__(self):
        ensure_sounds()
        self._effects = {}
        for name in (
            "click", "attack", "heal", "mana", "buy",
            "damage", "victory", "defeat", "card_play",
        ):
            effect = QSoundEffect()
            path = sound_path(f"{name}.wav")
            effect.setSource(QUrl.fromLocalFile(path))
            effect.setVolume(0.55)
            self._effects[name] = effect

    def play(self, name):
        effect = self._effects.get(name)
        if effect:
            effect.stop()
            effect.play()


class ParticleOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._particles = [
            {"x": random.randint(0, 1200), "y": random.randint(0, 820), "r": random.randint(30, 70)}
            for _ in range(30)
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(60)

    def _tick(self):
        for p in self._particles:
            p["x"] += 1
            if p["x"] > 1250:
                p["x"] = -80
                p["y"] = random.randint(0, 820)
        self.update()

    def paintEvent(self, event):
        from PyQt6.QtGui import QColor, QPainter

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = QColor(26, 16, 48, 35)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self._particles:
            painter.drawEllipse(int(p["x"]), int(p["y"]), p["r"], p["r"])


class FlashOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def flash(self, color="#550015", duration=120):
        self.setStyleSheet(f"background-color: {color};")
        self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)


class StatPanel(QFrame):
    def __init__(self, title, accent, icon_cache, parent=None):
        super().__init__(parent)
        self.setObjectName("enemyPanel" if "КОМПЬЮТЕР" in title else "playerPanel")
        self._icon_cache = icon_cache

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setStyleSheet(f"color: {accent};")
        layout.addWidget(title_label)

        self.hp_bar = QProgressBar()
        self.hp_bar.setObjectName("hpBar")
        self.hp_bar.setRange(0, 100)
        self.hp_bar.setFixedHeight(14)
        self.hp_bar.setTextVisible(False)
        layout.addWidget(self._row("icon_hp.png", self.hp_bar))

        self.mana_bar = QProgressBar()
        self.mana_bar.setObjectName("manaBar")
        self.mana_bar.setRange(0, 100)
        self.mana_bar.setFixedHeight(14)
        self.mana_bar.setTextVisible(False)
        layout.addWidget(self._row("icon_mana.png", self.mana_bar))

        self.hp_label = QLabel()
        self.mana_label = QLabel()
        self.gold_label = QLabel()
        self.gold_label.setObjectName("goldLabel")

        stats = QHBoxLayout()
        stats.addWidget(self.hp_label)
        stats.addSpacing(16)
        stats.addWidget(self.mana_label)
        stats.addStretch()
        layout.addLayout(stats)

        gold_row = QHBoxLayout()
        gold_icon = QLabel()
        gold_icon.setPixmap(icon_cache.get_icon_pixmap("icon_gold.png"))
        gold_row.addWidget(gold_icon)
        gold_row.addWidget(self.gold_label)
        gold_row.addStretch()
        layout.addLayout(gold_row)

        self._hp_anim = QPropertyAnimation(self.hp_bar, b"value")
        self._hp_anim.setDuration(350)
        self._hp_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._mana_anim = QPropertyAnimation(self.mana_bar, b"value")
        self._mana_anim.setDuration(350)
        self._mana_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _row(self, icon_name, bar):
        row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(self._icon_cache.get_icon_pixmap(icon_name))
        wrapper = QWidget()
        inner = QHBoxLayout(wrapper)
        inner.setContentsMargins(0, 0, 0, 0)
        inner.addWidget(icon)
        inner.addWidget(bar, 1)
        return wrapper

    def update_player(self, player):
        hp_pct = int((player.hp / player.max_hp) * 100) if player.max_hp else 0
        mana_pct = int((player.mana / player.max_mana) * 100) if player.max_mana else 0

        self._hp_anim.stop()
        self._hp_anim.setStartValue(self.hp_bar.value())
        self._hp_anim.setEndValue(max(0, hp_pct))
        self._hp_anim.start()

        self._mana_anim.stop()
        self._mana_anim.setStartValue(self.mana_bar.value())
        self._mana_anim.setEndValue(max(0, mana_pct))
        self._mana_anim.start()

        self.hp_label.setText(f"{player.hp}/{player.max_hp} HP")
        self.mana_label.setText(f"{player.mana}/{player.max_mana} маны")
        self.gold_label.setText(f"{player.gold} монет")


class CardButton(QPushButton):
    clicked_card = pyqtSignal(dict)

    def __init__(self, card, pixmap, parent=None):
        super().__init__(parent)
        self.card = card
        self._base_pixmap = pixmap
        self.setIcon(QIcon(pixmap))
        self.setIconSize(pixmap.size())
        self.setFixedSize(pixmap.size())
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton { background: transparent; border: none; }"
            "QPushButton:hover { background: rgba(255,255,255,0.05); border-radius: 12px; }"
        )

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 6)
        shadow.setColor(Qt.GlobalColor.black)
        self.setGraphicsEffect(shadow)

        self._hover_anim = QPropertyAnimation(self, b"geometry")
        self._hover_anim.setDuration(150)
        self._hover_anim.setEasingCurve(QEasingCurve.Type.OutBack)
        self._rest_geometry = None

        self.clicked.connect(self._emit)

    def _emit(self):
        self.clicked_card.emit(self.card)

    def enterEvent(self, event):
        if self._rest_geometry is None:
            self._rest_geometry = self.geometry()
        g = self._rest_geometry
        self._hover_anim.stop()
        self._hover_anim.setStartValue(g)
        self._hover_anim.setEndValue(g.adjusted(-4, -10, 4, 0))
        self._hover_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self._rest_geometry:
            self._hover_anim.stop()
            self._hover_anim.setStartValue(self.geometry())
            self._hover_anim.setEndValue(self._rest_geometry)
            self._hover_anim.start()
        super().leaveEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._rest_geometry = self.geometry()


class DifficultyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор сложности")
        self.setFixedSize(420, 400)
        self.selected_level = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("⚔ DARK FANTASY ⚔")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['text_gold']}; font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("ВЫБЕРИ СВОЮ СУДЬБУ")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(subtitle)

        options = [
            (1, "ЛЁГКИЙ", "35 HP против 15 HP"),
            (2, "СРЕДНИЙ", "30 HP против 30 HP"),
            (3, "ИСПЫТАНИЕ", "25 HP против 40 HP"),
        ]
        for level, name, desc in options:
            btn = QPushButton(f"{name}\n{desc}")
            btn.setMinimumHeight(56)
            btn.clicked.connect(lambda checked, l=level: self._choose(l))
            layout.addWidget(btn)

        layout.addStretch()

    def _choose(self, level):
        self.selected_level = level
        self.accept()


class ShopDialog(QDialog):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setWindowTitle("Магазин")
        self.setFixedSize(980, 560)

        layout = QVBoxLayout(self)

        title = QLabel("🛒 МАГАЗИН КАРТ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {COLORS['text_gold']}; font-size: 22pt; font-weight: bold;")
        layout.addWidget(title)

        self.gold_label = QLabel()
        self.gold_label.setObjectName("goldLabel")
        self.gold_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.gold_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        self.cards_layout = QHBoxLayout(container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        self._build_cards()
        self._update_gold()

    def _update_gold(self):
        self.gold_label.setText(f"💰 {self.game.player.gold} монет")

    def _build_cards(self):
        for i, card in enumerate(create_deck()):
            price = CARD_PRICES.get(card["name"], 100)
            pixmap = self.game.assets.get_card_pixmap(f"shop_{i}", card, price=price)
            btn = CardButton(card, pixmap)
            btn.clicked_card.connect(lambda card, p=price: self._buy(card, p))
            self.cards_layout.addWidget(btn)

    def _buy(self, card, price):
        if self.game.player.gold < price:
            QMessageBox.warning(self, "Ошибка", "Недостаточно монет!")
            return
        self.game.player.gold -= price
        self.game.player.deck.append({**card})
        self.game.sounds.play("buy")
        self.game.log(f"Куплена карта: {card['name']}")
        self._update_gold()
        self.game.update_ui()


class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DARK FANTASY CARD GAME")
        self.setFixedSize(1200, 820)

        self.assets = AssetCache()
        self.sounds = SoundManager()
        self.player = Player("Игрок")
        self.enemy = Player("Компьютер")
        self.round_count = 1
        self._card_buttons = []
        self._animations = []
        self._busy = False

        if not self._setup_game():
            QTimer.singleShot(0, self.close)
            return

        self._build_ui()
        self.update_ui()

    def _setup_game(self):
        answer = QMessageBox.question(
            self,
            "Запуск игры",
            "Начать игру?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return False

        dialog = DifficultyDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted or dialog.selected_level is None:
            return False

        level = dialog.selected_level
        if level == 1:
            self.player.max_hp = self.player.hp = 35
            self.enemy.max_hp = self.enemy.hp = 15
        elif level == 2:
            self.player.max_hp = self.player.hp = 30
            self.enemy.max_hp = self.enemy.hp = 30
        else:
            self.player.max_hp = self.player.hp = 25
            self.enemy.max_hp = self.enemy.hp = 40

        all_cards = create_deck()
        green = [c for c in all_cards if "damage" in c]
        red = [c for c in all_cards if "heal" in c or c.get("effect") in ("gods", "last_chance")]
        blue = [c for c in all_cards if "mana_gain" in c or c.get("effect") == "trade"]

        self.player.deck = random.sample(green, 3) + random.sample(red, 1) + random.sample(blue, 1)
        self.enemy.deck = random.sample(green, 3) + random.sample(red, 1) + random.sample(blue, 1)
        random.shuffle(self.player.deck)
        random.shuffle(self.enemy.deck)
        return True

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        from design import load_background_pixmap

        self.bg_label = QLabel(central)
        self.bg_label.setPixmap(load_background_pixmap(1200, 820))
        self.bg_label.setGeometry(0, 0, 1200, 820)
        self.bg_label.lower()

        self.particles = ParticleOverlay(central)
        self.particles.setGeometry(0, 0, 1200, 820)

        self.flash = FlashOverlay(central)
        self.flash.setGeometry(0, 0, 1200, 820)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 12, 20, 12)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("DARK FANTASY")
        title.setObjectName("title")
        subtitle = QLabel("Карточная битва")
        subtitle.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles)
        header.addStretch()

        shop_btn = QPushButton("  МАГАЗИН")
        shop_icon = self.assets.get_icon_pixmap("icon_shop.png", (28, 28))
        if not shop_icon.isNull():
            shop_btn.setIcon(QIcon(shop_icon))
        shop_btn.clicked.connect(self.open_shop)
        header.addWidget(shop_btn)
        layout.addLayout(header)

        self.enemy_panel = StatPanel("👹 КОМПЬЮТЕР", COLORS["border_heal"], self.assets)
        layout.addWidget(self.enemy_panel)

        round_frame = QFrame()
        round_frame.setObjectName("roundBadge")
        round_layout = QVBoxLayout(round_frame)
        self.round_label = QLabel()
        self.round_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.round_label.setStyleSheet(f"color: {COLORS['text_gold']}; font-size: 14pt; font-weight: bold;")
        round_layout.addWidget(self.round_label)
        layout.addWidget(round_frame)

        self.player_panel = StatPanel("🛡 ИГРОК", COLORS["border_attack"], self.assets)
        layout.addWidget(self.player_panel)

        log_title = QLabel("📜 Журнал боя")
        log_title.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(log_title)

        self.log_text = QTextEdit()
        self.log_text.setObjectName("log")
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(130)
        layout.addWidget(self.log_text)

        cards_scroll = QScrollArea()
        cards_scroll.setWidgetResizable(True)
        cards_scroll.setFixedHeight(250)
        cards_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        cards_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.cards_container = QWidget()
        self.cards_layout = QHBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.cards_layout.setSpacing(10)
        cards_scroll.setWidget(self.cards_container)
        layout.addWidget(cards_scroll)

        skip_btn = QPushButton("  ПРОПУСТИТЬ ХОД")
        skip_icon = self.assets.get_icon_pixmap("icon_skip.png", (22, 22))
        if not skip_icon.isNull():
            skip_btn.setIcon(QIcon(skip_icon))
        skip_btn.clicked.connect(self.skip_turn)
        layout.addWidget(skip_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(content)
        self.particles.raise_()
        self.flash.raise_()

    def log(self, text):
        self.log_text.append(text)

    def update_ui(self):
        self.player_panel.update_player(self.player)
        self.enemy_panel.update_player(self.enemy)
        self.round_label.setText(f"⚔ КРУГ {self.round_count} ⚔")

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self._card_buttons.clear()

        for i, card in enumerate(self.player.deck):
            pixmap = self.assets.get_card_pixmap(i, card)
            btn = CardButton(card, pixmap, self.cards_container)
            btn.clicked_card.connect(self.play_card)
            self.cards_layout.addWidget(btn)
            self._card_buttons.append(btn)

    def open_shop(self):
        self.sounds.play("click")
        dialog = ShopDialog(self, self)
        dialog.exec()

    def _shake(self):
        origin = self.frameGeometry().topLeft()
        steps = [(random.randint(-8, 8), random.randint(-8, 8)) for _ in range(8)]

        def step(i=0):
            if i >= len(steps):
                self.move(origin)
                return
            dx, dy = steps[i]
            self.move(origin.x() + dx, origin.y() + dy)
            QTimer.singleShot(20, lambda: step(i + 1))

        step()

    def _spawn_particles(self, color_hex):
        overlay = QLabel(self.centralWidget())
        overlay.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        overlay.setStyleSheet("background: transparent;")
        overlay.setGeometry(450, 180, 300, 120)
        overlay.show()
        overlay.raise_()

        dots = []
        for _ in range(12):
            dot = QLabel(overlay)
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background: {color_hex}; border-radius: 5px;")
            x, y = random.randint(0, 280), random.randint(0, 100)
            dot.move(x, y)
            dot.show()
            dots.append((dot, x, y))

        def animate(frame=0):
            if frame > 18:
                overlay.deleteLater()
                return
            for dot, x, y in dots:
                dot.move(x + random.randint(-12, 12), y + random.randint(-12, 12))
            QTimer.singleShot(30, lambda: animate(frame + 1))

        animate()

    def _animate_card_play(self, pixmap, callback):
        flyer = QLabel(self.centralWidget())
        flyer.setPixmap(pixmap)
        flyer.setFixedSize(pixmap.size())
        start = self.cards_container.mapTo(self.centralWidget(), self.cards_container.rect().center())
        flyer.move(start.x() - pixmap.width() // 2, start.y())
        flyer.show()
        flyer.raise_()

        anim = QPropertyAnimation(flyer, b"geometry")
        anim.setDuration(320)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        start_rect = flyer.geometry()
        end_rect = start_rect.translated(0, -220)
        anim.setStartValue(start_rect)
        anim.setEndValue(end_rect)

        def finish():
            flyer.deleteLater()
            callback()

        anim.finished.connect(finish)
        self._animations.append(anim)
        anim.start()
        self.sounds.play("card_play")

    def play_card(self, card):
        if self._busy:
            return

        free_mana = "mana_gain" in card or card.get("effect") == "trade"
        if not free_mana and self.player.mana < card["mana"]:
            QMessageBox.warning(self, "Ошибка", "Недостаточно маны!")
            return

        self._busy = True
        pixmap = self.assets.get_card_pixmap(f"play_{card['name']}", card)

        def resolve():
            if not free_mana:
                self.player.mana -= card["mana"]
            self.player.deck.remove(card)
            self.log(f"Игрок использовал: {card['name']}")
            self._apply_player_card(card)
            if self.check_game():
                self._busy = False
                return

            self.player.gold = min(self.player.gold + 35, self.player.max_gold)
            self.enemy_turn()
            if self.check_game():
                self._busy = False
                return
            self.round_count += 1
            self.apply_effects(self.player)
            self.update_ui()
            self._busy = False

        self._animate_card_play(pixmap, resolve)

    def _apply_player_card(self, card):
        if "damage" in card:
            self.enemy.hp -= card["damage"]
            self.sounds.play("attack")
            self._shake()
            self.flash.flash("#660018")
            self._spawn_particles("#ff4466")
            self.log(f"Нанесено {card['damage']} урона")

        elif "heal" in card:
            self.heal_player(self.player, card["heal"])
            self.sounds.play("heal")
            self._spawn_particles("#ffffff")
            self.log(f"Игрок восстановил {card['heal']} HP")

        elif "mana_gain" in card:
            self.player.mana = min(self.player.mana + card["mana_gain"], self.player.max_mana)
            self.sounds.play("mana")
            self._spawn_particles("#4488ff")
            self.log(f"+{card['mana_gain']} маны")

        elif card.get("effect") == "trade":
            if random.randint(1, 2) == 1:
                self.player.hp -= 3
                self.sounds.play("damage")
                self.flash.flash("#440010")
                self.log("Шило на мыло: -3 HP")
            else:
                self.player.mana = min(self.player.mana + 4, self.player.max_mana)
                self.sounds.play("mana")
                self._spawn_particles("#4488ff")
                self.log("Шило на мыло: +4 маны")

        elif card.get("effect") == "gods":
            self.player.gods_blessing = True
            self.sounds.play("heal")
            self._spawn_particles("#ffd700")
            self.log("Активировано признание богов")

        elif card.get("effect") == "last_chance":
            self.heal_player(self.player, 30)
            self.player.last_chance_timer = 0
            self.sounds.play("damage")
            self._spawn_particles("#ff4466")
            self.log("Последний шанс активирован")

    def skip_turn(self):
        if self._busy:
            return
        self.sounds.play("click")
        self.log("Игрок пропускает ход")
        self.enemy_turn()
        if self.check_game():
            return
        self.round_count += 1
        self.apply_effects(self.player)
        self.update_ui()

    def heal_player(self, player, amount):
        player.hp = min(player.hp + amount, player.max_hp)

    def apply_effects(self, player):
        player.mana = min(player.mana + random.randint(1, 3), player.max_mana)

        if player.gods_blessing:
            self.heal_player(player, 2)
            self.log(f"{player.name} получает +2 HP (благословение богов)")

        if player.last_chance_timer >= 0:
            player.last_chance_timer += 1
            if player.last_chance_timer >= 3:
                player.hp -= 20
                self._shake()
                self.flash.flash("#770000")
                self.sounds.play("damage")
                self.log(f"{player.name} получает -20 HP! (последний шанс)")
                player.last_chance_timer = -1

    def enemy_turn(self):
        self.apply_effects(self.enemy)

        possible = []
        for card in self.enemy.deck:
            free = "mana_gain" in card or card.get("effect") == "trade"
            if free or self.enemy.mana >= card["mana"]:
                possible.append(card)

        if not possible:
            self.log("Компьютер пропускает ход")
            return False

        card = random.choice(possible)
        self.enemy.deck.remove(card)
        free = "mana_gain" in card or card.get("effect") == "trade"
        if not free:
            self.enemy.mana -= card["mana"]

        self.log(f"Компьютер использовал: {card['name']}")

        if "damage" in card:
            self.player.hp -= card["damage"]
            self.sounds.play("damage")
            self._shake()
            self.flash.flash("#660018")
            self._spawn_particles("#ff4466")

        elif "heal" in card:
            self.heal_player(self.enemy, card["heal"])
            self.sounds.play("heal")
            self._spawn_particles("#ffffff")

        elif "mana_gain" in card:
            self.enemy.mana = min(self.enemy.mana + card["mana_gain"], self.enemy.max_mana)
            self.sounds.play("mana")
            self.enemy.gold = min(self.enemy.gold + 35, self.enemy.max_gold)

        elif card.get("effect") == "trade":
            if random.randint(1, 2) == 1:
                self.enemy.hp -= 3
                self.sounds.play("damage")
                self.log("Компьютер: Шило на мыло -3 HP")
            else:
                self.enemy.mana = min(self.enemy.mana + 4, self.enemy.max_mana)
                self.sounds.play("mana")
                self.log("Компьютер: Шило на мыло +4 маны")

        elif card.get("effect") == "gods":
            self.enemy.gods_blessing = True
            self.sounds.play("heal")
            self.log("Компьютер активировал признание богов")

        elif card.get("effect") == "last_chance":
            self.heal_player(self.enemy, 30)
            self.enemy.last_chance_timer = 0
            self.sounds.play("damage")
            self.log("Компьютер активировал последний шанс")

        return self.check_game()

    def check_game(self):
        if self.player.hp <= 0:
            self.sounds.play("defeat")
            QMessageBox.information(self, "Игра окончена", "Компьютер победил!")
            self.close()
            return True
        if self.enemy.hp <= 0:
            self.sounds.play("victory")
            QMessageBox.information(self, "Игра окончена", "Вы победили!")
            self.close()
            return True
        return False


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)
    window = GameWindow()
    if window.centralWidget() is not None:
        window.show()
        sys.exit(app.exec())
    sys.exit(0)


if __name__ == "__main__":
    main()
