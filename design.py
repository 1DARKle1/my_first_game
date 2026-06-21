import os

from PIL import Image, ImageDraw, ImageFont

from paths import resource_dir, writable_dir

ASSETS_DIR = os.path.join(resource_dir(), "assets")
WRITABLE_ASSETS_DIR = os.path.join(writable_dir(), "assets")
CARDS_DIR = os.path.join(ASSETS_DIR, "cards")

COLORS = {
    "bg_dark": "#0a0612",
    "bg_panel": "#14101f",
    "bg_card": "#1a1528",
    "border_gold": "#c9a227",
    "border_attack": "#00ff99",
    "border_heal": "#ff4466",
    "border_mana": "#4488ff",
    "text_primary": "#f0e6d3",
    "text_secondary": "#a89bb0",
    "text_gold": "#ffd700",
    "hp_fill": "#e63946",
    "hp_bg": "#3d1520",
    "mana_fill": "#4cc9f0",
    "mana_bg": "#152535",
    "btn_normal": "#2a2240",
    "btn_hover": "#3d3260",
    "btn_active": "#524480",
    "log_bg": "#0d0a14",
    "title_glow": "#9d4edd",
}

CARD_W = 155
CARD_H = 220

CARD_TYPE_ART = {
    "attack": "card_attack.png",
    "heal": "card_heal.png",
    "mana": "card_mana.png",
}

CARD_ART = {
    "Огненный маг": "card_fire_mage.png",
    "Рыцарь": "card_knight.png",
    "Лучник": "card_archer.png",
    "Дракон": "card_dragon.png",
    "Гоблин": "card_goblin.png",
    "Тёмный паладин": "card_dark_paladin.png",
    "Ледяной воин": "card_ice_warrior.png",
    "Зелье здоровья": "card_health_potion.png",
    "Зелье маны": "card_mana_potion.png",
    "Шило на мыло": "card_risky_trade.png",
    "Признание богов": "card_gods_blessing.png",
    "Последний шанс": "card_last_chance.png",
}

CARD_TYPE_BORDER = {
    "attack": COLORS["border_attack"],
    "heal": COLORS["border_heal"],
    "mana": COLORS["border_mana"],
}

CARD_PRICES = {
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

APP_STYLE = """
QMainWindow, QDialog {{
    background-color: {bg_dark};
}}
QFrame#panel {{
    background-color: {bg_panel};
    border: 2px solid {border_gold};
    border-radius: 10px;
}}
QFrame#enemyPanel {{
    background-color: {bg_panel};
    border: 2px solid {border_heal};
    border-radius: 10px;
}}
QFrame#playerPanel {{
    background-color: {bg_panel};
    border: 2px solid {border_attack};
    border-radius: 10px;
}}
QFrame#roundBadge {{
    background-color: {bg_panel};
    border: 2px solid {border_gold};
    border-radius: 8px;
}}
QTextEdit#log {{
    background-color: {log_bg};
    color: {text_primary};
    border: 2px solid {border_gold};
    border-radius: 8px;
    padding: 8px;
    font-family: Consolas;
    font-size: 10pt;
}}
QPushButton {{
    background-color: {btn_normal};
    color: {text_primary};
    border: 1px solid #3d3260;
    border-radius: 8px;
    padding: 10px 16px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {btn_hover};
}}
QPushButton:pressed {{
    background-color: {btn_active};
}}
QProgressBar {{
    background-color: {hp_bg};
    border: none;
    border-radius: 6px;
    height: 14px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    border-radius: 6px;
}}
QProgressBar#hpBar::chunk {{
    background-color: {hp_fill};
}}
QProgressBar#manaBar::chunk {{
    background-color: {mana_fill};
}}
QLabel#title {{
    color: {text_gold};
    font-family: Georgia;
    font-size: 34pt;
    font-weight: bold;
}}
QLabel#subtitle {{
    color: {text_secondary};
    font-size: 10pt;
}}
QLabel#statTitle {{
    font-weight: bold;
    font-size: 11pt;
}}
QLabel#goldLabel {{
    color: {text_gold};
    font-weight: bold;
}}
""".format(**COLORS)


def _hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)


def _icon_path(filename):
    return _resolve_asset_path(filename)


def _card_art_path(card):
    art_file = CARD_ART.get(card["name"])
    if art_file:
        path = os.path.join(CARDS_DIR, art_file)
        if os.path.exists(path):
            return path
    card_type = get_card_type(card)
    return _asset_path(CARD_TYPE_ART[card_type])


def _load_font(size, bold=False):
    names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    if bold:
        names = ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"] + names
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def get_card_type(card):
    if "damage" in card:
        return "attack"
    if "heal" in card or card.get("effect") in ("gods", "last_chance"):
        return "heal"
    return "mana"


def ensure_ui_icons():
    icons = {
        "icon_hp.png": _draw_hp_icon,
        "icon_mana.png": _draw_mana_icon,
        "icon_gold.png": _draw_gold_icon,
        "icon_skip.png": _draw_skip_icon,
    }
    for filename, drawer in icons.items():
        bundled = _asset_path(filename)
        if not os.path.exists(bundled):
            os.makedirs(WRITABLE_ASSETS_DIR, exist_ok=True)
            drawer(os.path.join(WRITABLE_ASSETS_DIR, filename))


def _resolve_asset_path(filename):
    bundled = _asset_path(filename)
    if os.path.exists(bundled):
        return bundled
    generated = os.path.join(WRITABLE_ASSETS_DIR, filename)
    if os.path.exists(generated):
        return generated
    return bundled


def _draw_hp_icon(path):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 6, 28, 28), fill="#e63946")
    draw.polygon([(16, 8), (10, 16), (16, 26), (22, 16)], fill="#ff6b7a")
    img.save(path)


def _draw_mana_icon(path):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.polygon([(16, 2), (28, 12), (22, 30), (10, 30), (4, 12)], fill="#4cc9f0")
    draw.polygon([(16, 8), (22, 14), (18, 24), (14, 24), (10, 14)], fill="#a8ecff")
    img.save(path)


def _draw_gold_icon(path):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((4, 4, 28, 28), fill="#ffd700", outline="#c9a227", width=2)
    font = _load_font(14, bold=True)
    draw.text((10, 7), "G", fill="#8b6914", font=font)
    img.save(path)


def _draw_skip_icon(path):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((2, 8, 30, 24), radius=4, fill="#a89bb0")
    draw.polygon([(10, 12), (22, 16), (10, 20)], fill="#1a1528")
    img.save(path)


def render_card_image(card, price=None):
    card_type = get_card_type(card)
    border_rgb = _hex_to_rgb(CARD_TYPE_BORDER[card_type])
    bg_rgb = _hex_to_rgb(COLORS["bg_card"])

    img = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (0, 0, CARD_W - 1, CARD_H - 1),
        radius=12,
        fill=bg_rgb,
        outline=border_rgb,
        width=4,
    )

    art_path = _card_art_path(card)
    if os.path.exists(art_path):
        art = Image.open(art_path).convert("RGBA")
        art = art.resize((CARD_W - 20, 95), Image.Resampling.LANCZOS)
        img.paste(art, (10, 10), art)

    name_font = _load_font(11, bold=True)
    stat_font = _load_font(10)
    small_font = _load_font(9)

    name = card["name"]
    if len(name) > 14:
        parts = name.split()
        if len(parts) > 1:
            mid = len(parts) // 2
            draw.text((CARD_W // 2, 110), " ".join(parts[:mid]), fill=COLORS["text_primary"], font=name_font, anchor="mm")
            draw.text((CARD_W // 2, 124), " ".join(parts[mid:]), fill=COLORS["text_primary"], font=name_font, anchor="mm")
        else:
            draw.text((CARD_W // 2, 117), name, fill=COLORS["text_primary"], font=name_font, anchor="mm")
    else:
        draw.text((CARD_W // 2, 117), name, fill=COLORS["text_primary"], font=name_font, anchor="mm")

    free_mana = "mana_gain" in card or card.get("effect") == "trade"
    mana_text = "Мана: FREE" if free_mana else f"Мана: {card['mana']}"
    mana_color = COLORS["border_mana"] if free_mana else COLORS["text_secondary"]

    draw.rounded_rectangle((10, 138, CARD_W - 10, 156), radius=6, fill="#221c35")
    draw.text((CARD_W // 2, 147), mana_text, fill=mana_color, font=small_font, anchor="mm")

    if "damage" in card:
        stat_text = f"Урон: {card['damage']}"
        stat_color = COLORS["border_attack"]
    elif "heal" in card:
        stat_text = f"Лечение: {card['heal']}"
        stat_color = COLORS["border_heal"]
    elif "mana_gain" in card:
        stat_text = f"+{card['mana_gain']} маны"
        stat_color = COLORS["border_mana"]
    else:
        stat_text = "Особый эффект"
        stat_color = COLORS["title_glow"]

    draw.rounded_rectangle((10, 161, CARD_W - 10, 181), radius=6, fill="#221c35")
    draw.text((CARD_W // 2, 171), stat_text, fill=stat_color, font=stat_font, anchor="mm")

    if price is not None:
        draw.rounded_rectangle((10, 191, CARD_W - 10, 213), radius=6, fill="#2a2240", outline="#c9a227", width=1)
        draw.text((CARD_W // 2, 202), f"{price} монет", fill=COLORS["text_gold"], font=stat_font, anchor="mm")

    return img


def pil_to_qpixmap(pil_image):
    from PyQt6.QtGui import QImage, QPixmap

    if pil_image.mode != "RGBA":
        pil_image = pil_image.convert("RGBA")
    data = pil_image.tobytes("raw", "RGBA")
    qimage = QImage(
        data,
        pil_image.width,
        pil_image.height,
        pil_image.width * 4,
        QImage.Format.Format_RGBA8888,
    )
    return QPixmap.fromImage(qimage.copy())


def load_background_pixmap(width=1200, height=820):
    from PyQt6.QtGui import QPixmap

    path = _asset_path("bg_main.png")
    if os.path.exists(path):
        bg = Image.open(path).convert("RGBA")
        bg = bg.resize((width, height), Image.Resampling.LANCZOS)
        overlay = Image.new("RGBA", (width, height), (10, 6, 18, 150))
        bg = Image.alpha_composite(bg, overlay)
        return pil_to_qpixmap(bg)
    return QPixmap()


class AssetCache:
    def __init__(self):
        ensure_ui_icons()
        self._cards = {}
        self._icons = {}

    def get_card_pixmap(self, key, card, price=None):
        cache_key = (key, card["name"], price)
        if cache_key not in self._cards:
            self._cards[cache_key] = pil_to_qpixmap(render_card_image(card, price=price))
        return self._cards[cache_key]

    def get_icon_pixmap(self, filename, size=(24, 24)):
        key = (filename, size)
        if key not in self._icons:
            path = _icon_path(filename)
            if os.path.exists(path):
                icon = Image.open(path).convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                self._icons[key] = pil_to_qpixmap(icon)
            else:
                from PyQt6.QtGui import QPixmap
                self._icons[key] = QPixmap()
        return self._icons[key]
