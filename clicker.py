import json
import math
import os
import random
import sys
import time
import tkinter as tk
from tkinter import messagebox
import psutil
import webbrowser
import urllib.request

# ==========================================
# 🔊 ВСТРОЕННЫЙ МОДУЛЬ ЗВУКА (SOUND SYSTEM)
# ==========================================
class SoundManager:
    def __init__(self):
        self.enabled = False
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        try:
            import pygame
            pygame.mixer.init()
            self.pygame = pygame
            self.enabled = True
        except Exception as e:
            print(f"Предупреждение: Не удалось инициализировать Pygame Mixer ({e}). Звук отключен.")

    def set_music_volume(self, val):
        self.music_volume = float(val)
        if self.enabled:
            try:
                self.pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, val):
        self.sfx_volume = float(val)

    def play_sfx(self, filename):
        if not self.enabled:
            return
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            try:
                sound_obj = self.pygame.mixer.Sound(path)
                sound_obj.set_volume(self.sfx_volume)
                sound_obj.play()
            except Exception:
                pass

    def play_music(self, filename):
        if not self.enabled:
            return
        path = os.path.join(BASE_DIR, filename)
        if os.path.exists(path):
            try:
                self.pygame.mixer.music.load(path)
                self.pygame.mixer.music.set_volume(self.music_volume)
                self.pygame.mixer.music.play(-1)
            except Exception:
                pass

# ==========================================
# 📂 ПУТИ И ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ
# ==========================================
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sound = SoundManager()

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "MinerSimulator")
os.makedirs(APPDATA_DIR, exist_ok=True)

SAVE_FILE = os.path.join(APPDATA_DIR, "save.json")

BOOSTY_URL = "https://boosty.to/minersimulator"
YOUTUBE_URL = "https://youtube.com/@MinerSimulator"
DONATIONALERTS_URL = "https://www.donationalerts.com/r/minersimulator"
GITHUB_REPO = "user/MinerSimulator"  # Укажи свой репозиторий GitHub
CURRENT_VERSION = "v3 Beta"

PANEL_HEIGHT = 45

BLOCKED_PROCESSES = [
    "autoclicker.exe",
    "auto_clicker.exe",
    "op auto clicker.exe",
    "op_auto_clicker.exe",
    "gsauto_clicker.exe",
    "fastclicker.exe",
    "speedclicker.exe",
]

# Шансы и свойства выпадаемой руды (Drop Rates)
ORE_TYPES = [
    {"name_ru": "Камень", "name_en": "Stone", "chance": 0.50, "mult": 1.0, "color": "#8d99ae"},
    {"name_ru": "Уголь", "name_en": "Coal", "chance": 0.25, "mult": 1.5, "color": "#2b2d42"},
    {"name_ru": "Железо", "name_en": "Iron", "chance": 0.15, "mult": 2.5, "color": "#d8f3dc"},
    {"name_ru": "Золото", "name_en": "Gold", "chance": 0.08, "mult": 5.0, "color": "#ffd166"},
    {"name_ru": "Алмаз", "name_en": "Diamond", "chance": 0.02, "mult": 12.0, "color": "#89dceb"}
]

STONE_BG_MAIN = "#1a1c1e"
STONE_BG_CANVAS = "#24272b"
STONE_PANEL_BG = "#2b2e34"
STONE_PANEL_BORDER = "#40454f"
STONE_BTN_BG = "#383c44"
STONE_BTN_HOVER = "#484e58"
STONE_BTN_ACTIVE = "#22252a"
STONE_TEXT_LIGHT = "#e0e3e8"
STONE_TEXT_GOLD = "#ffd166"
STONE_TEXT_CRIT = "#ff595e"

current_lang = "ru"

SETTINGS = {
    "particles": "full",
    "show_miner": True,
    "music_volume": 0.5,
    "sfx_volume": 0.5,
}

# Инициализация игровых переменных
score = 0
total_score = 0
lifetime_score = 0
total_clicks = 0
rubies = 0
click_power = 1
auto_income = 0
upgrade_click_cost = 10
upgrade_auto_cost = 20

level = 1
xp = 0
xp_needed = 100

crit_chance = 0.05
crit_level = 0
upgrade_crit_cost = 50

has_combo = False
combo_cost = 1000
combo_multiplier = 1.0
last_tap_time = 0
tap_count = 0

click_timestamps = []
is_penalized = False
is_fullscreen = True
is_blocked_by_process = False

current_screen = "main_menu"
is_miner_swinging = False
_last_wall_size = (0, 0)

# ==========================================
# 🏆 СИСТЕМА АЧИВОК (ACHIEVEMENTS SYSTEM)
# ==========================================
ACHIEVEMENTS = {
    "first_click": {
        "ru": {"title": "Первый взмах", "desc": "Сделайте свой первый удар киркой"},
        "en": {"title": "First Swing", "desc": "Take your first pickaxe swing"},
        "check": lambda: total_clicks >= 1,
        "unlocked": False
    },
    "ore_100": {
        "ru": {"title": "Начинающий шахтёр", "desc": "Добудьте 100 единиц руды за всё время"},
        "en": {"title": "Novice Miner", "desc": "Mine 100 total ore lifetime"},
        "check": lambda: lifetime_score >= 100,
        "unlocked": False
    },
    "ore_10000": {
        "ru": {"title": "Золотая жила", "desc": "Добудьте 10,000 единиц руды за всё время"},
        "en": {"title": "Gold Rush", "desc": "Mine 10,000 total ore lifetime"},
        "check": lambda: lifetime_score >= 10000,
        "unlocked": False
    },
    "clicks_100": {
        "ru": {"title": "Трудоголик", "desc": "Совершите 100 ударов киркой"},
        "en": {"title": "Workaholic", "desc": "Swing pickaxe 100 times"},
        "check": lambda: total_clicks >= 100,
        "unlocked": False
    },
    "ruby_1": {
        "ru": {"title": "Первые сокровища", "desc": "Заработайте свой первый рубин"},
        "en": {"title": "First Treasure", "desc": "Earn your first ruby"},
        "check": lambda: rubies >= 1,
        "unlocked": False
    },
    "combo_master": {
        "ru": {"title": "Мастер ритма", "desc": "Активируйте Навык Старателя"},
        "en": {"title": "Rhythm Master", "desc": "Purchase Prospector Skill"},
        "check": lambda: has_combo,
        "unlocked": False
    },
    "level_5": {
        "ru": {"title": "Опытный шахтёр", "desc": "Достигните 5 уровня шахтёра"},
        "en": {"title": "Experienced Miner", "desc": "Reach Miner Level 5"},
        "check": lambda: level >= 5,
        "unlocked": False
    }
}

LANGUAGES = {
    "ru": {
        "title": "MINER SIMULATOR",
        "play_btn": "⛏️ ИГРАТЬ",
        "main_settings_btn": "⚙ НАСТРОЙКИ",
        "main_exit_btn": "🚪 ВЫЙТИ",
        "score": "⛏️ Руда: ",
        "hit": "Удар: +",
        "drills": "Буры: +",
        "per_sec": "/сек",
        "rubies": "💎 Рубины: ",
        "miner_lvl": "⭐ Шахтёр Ур. ",
        "rhythm": "🔥 РИТМ x",
        "upg_click": "Усилить кирку (+1)\nЦена: ",
        "upg_auto": "Авто-бур (+1/сек)\nЦена: ",
        "upg_crit": "Точный удар (+3% крит)\n",
        "upg_crit_max": "Точный удар: МАКС (50%)",
        "crit_price": "% | Цена: ",
        "combo_bought": "Старатель: КУПЛЕНО",
        "combo_btn": "Навык Старателя\nЦена: ",
        "combo_need": "Навык Старателя\n(Нужно 1,000 руды)",
        "prestige": "ПЕРЕРОЖДЕНИЕ (10k)",
        "menu_btn": "🏠 Меню",
        "settings_btn": "⚙ Настройки",
        "achievements_btn": "🏆 АЧИВКИ",
        "achievements_title": "🏆 ДОСТИЖЕНИЯ",
        "lang_btn": "🌐 Язык: RU",
        "lucky_ore": "💎 РУДНАЯ ЖИЛА!",
        "bonus": "БОНУС +",
        "crit_text": " КРИТ!",
        "anticheat": "🚨 АВТОКЛИКЕР! -",
        "blocked_title": "🚫 ДОСТУП ЗАПРЕЩЁН!\n\nОбнаружен автокликер:\n[{proc}]\n\nЗакройте его, чтобы продолжить добычу!",
        "blocked_quit": "Закрыть игру",
        "settings_title": "📜 НАСТРОЙКИ И СТАТИСТИКА",
        "stats_text": "📊 СТАТИСТИКА ШАХТЫ:\n\n• Взмахов киркой: {clicks}\n• Добыто за всё время: {lifetime}\n• Уровень шахтёра: {lvl}\n• Рубинов найдено: {rubs}",
        "toggle_screen": "Режим Экран / Окно (F11)",
        "reset_btn": "Сбросить полный прогресс",
        "back_btn": "← Назад",
        "reset_confirm_title": "Сброс",
        "reset_confirm_msg": "Уверен, что хочешь сбросить весь прогресс?",
        "exit_title": "Вы уверены, что\nхотите покинуть шахту?",
        "exit_yes": "Да, выйти",
        "exit_no": "Нет, остаться",
        "opt_title": "⚡ ОПТИМИЗАЦИЯ И ЗВУК",
        "part_full": "Частицы: Макс (8)",
        "part_min": "Частицы: Мало (3)",
        "part_off": "Частицы: Выкл",
        "miner_on": "Работник: Включен",
        "miner_off": "Работник: Выключен (Бур)",
        "ach_unlocked": "🏆 ДОСТИЖЕНИЕ ПОЛУЧЕНО!",
        "vol_music": "🎵 Музыка:",
        "vol_sfx": "🔊 Эффекты:",
        "update_avail": "🎁 Доступно обновление!",
    },
    "en": {
        "title": "MINER SIMULATOR",
        "play_btn": "⛏️ PLAY",
        "main_settings_btn": "⚙ SETTINGS",
        "main_exit_btn": "🚪 EXIT",
        "score": "⛏️ Ore: ",
        "hit": "Hit: +",
        "drills": "Drills: +",
        "per_sec": "/sec",
        "rubies": "💎 Rubies: ",
        "miner_lvl": "⭐ Miner Lvl. ",
        "rhythm": "🔥 RHYTHM x",
        "upg_click": "Upgrade Pickaxe (+1)\nCost: ",
        "upg_auto": "Auto-Drill (+1/sec)\nCost: ",
        "upg_crit": "Precision Hit (+3% crit)\n",
        "upg_crit_max": "Precision Hit: MAX (50%)",
        "crit_price": "% | Cost: ",
        "combo_bought": "Prospector: BOUGHT",
        "combo_btn": "Prospector Skill\nCost: ",
        "combo_need": "Prospector Skill\n(Need 1,000 ore)",
        "prestige": "PRESTIGE (10k)",
        "menu_btn": "🏠 Menu",
        "settings_btn": "⚙ Settings",
        "achievements_btn": "🏆 ACHIEVEMENTS",
        "achievements_title": "🏆 ACHIEVEMENTS",
        "lang_btn": "🌐 Lang: EN",
        "lucky_ore": "💎 ORE VEIN!",
        "bonus": "BONUS +",
        "crit_text": " CRIT!",
        "anticheat": "🚨 AUTOCLICKER! -",
        "blocked_title": "🚫 ACCESS DENIED!\n\nAutoclicker detected:\n[{proc}]\n\nClose it to continue mining!",
        "blocked_quit": "Close Game",
        "settings_title": "📜 SETTINGS & STATS",
        "stats_text": "📊 MINE STATS:\n\n• Pickaxe swings: {clicks}\n• Lifetime ore mined: {lifetime}\n• Miner level: {lvl}\n• Rubies found: {rubs}",
        "toggle_screen": "Toggle Screen Mode (F11)",
        "reset_btn": "Reset All Progress",
        "back_btn": "← Back",
        "reset_confirm_title": "Reset",
        "reset_confirm_msg": "Are you sure you want to reset all progress?",
        "exit_title": "Are you sure you\nwant to leave the mine?",
        "exit_yes": "Yes, Exit",
        "exit_no": "No, Stay",
        "opt_title": "⚡ OPTIMIZATION & AUDIO",
        "part_full": "Particles: Max (8)",
        "part_min": "Particles: Low (3)",
        "part_off": "Particles: Off",
        "miner_on": "Worker: Enabled",
        "miner_off": "Worker: Disabled (Rig)",
        "ach_unlocked": "🏆 ACHIEVEMENT UNLOCKED!",
        "vol_music": "🎵 Music:",
        "vol_sfx": "🔊 SFX:",
        "update_avail": "🎁 Update Available!",
    },
}

# ==========================================
# 🔄 МОДУЛЬ АВТООБНОВЛЕНИЙ
# ==========================================
def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                latest_tag = data.get("tag_name", "")
                if latest_tag and latest_tag != CURRENT_VERSION:
                    root.after(0, lambda: show_update_banner(latest_tag))
    except Exception:
        pass

def show_update_banner(new_version):
    t = LANGUAGES[current_lang]
    version_label.config(text=f"{CURRENT_VERSION} ({t['update_avail']} {new_version})", fg="#ffd166")

# ==========================================
# 💾 СИСТЕМА СОХРАНЕНИЯ / ЗАГРУЗКИ
# ==========================================
def load_game():
    global score, total_score, lifetime_score, total_clicks, rubies, click_power, auto_income
    global upgrade_click_cost, upgrade_auto_cost, upgrade_crit_cost
    global level, xp, xp_needed, crit_chance, crit_level, has_combo, current_lang, SETTINGS

    if not os.path.exists(SAVE_FILE):
        return

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Содержимое save.json не является объектом JSON")

        score = int(data.get("score", 0))
        total_score = int(data.get("total_score", score))
        lifetime_score = int(data.get("lifetime_score", total_score))
        total_clicks = int(data.get("total_clicks", 0))
        rubies = int(data.get("rubies", 0))
        click_power = int(data.get("click_power", 1))
        auto_income = int(data.get("auto_income", 0))
        upgrade_click_cost = int(data.get("upgrade_click_cost", 10))
        upgrade_auto_cost = int(data.get("upgrade_auto_cost", 20))
        level = int(data.get("level", 1))
        xp = int(data.get("xp", 0))
        xp_needed = int(data.get("xp_needed", 100))
        crit_chance = float(data.get("crit_chance", 0.05))
        crit_level = int(data.get("crit_level", 0))
        upgrade_crit_cost = int(data.get("upgrade_crit_cost", 50))
        has_combo = bool(data.get("has_combo", False))
        
        saved_ach = data.get("achievements", {})
        for key in ACHIEVEMENTS:
            if key in saved_ach:
                ACHIEVEMENTS[key]["unlocked"] = bool(saved_ach[key])

        lang = data.get("current_lang", "ru")
        current_lang = lang if lang in LANGUAGES else "ru"

        saved_opt = data.get("settings", {})
        if isinstance(saved_opt, dict):
            SETTINGS["particles"] = saved_opt.get("particles", "full")
            SETTINGS["show_miner"] = bool(saved_opt.get("show_miner", True))
            SETTINGS["music_volume"] = float(saved_opt.get("music_volume", 0.5))
            SETTINGS["sfx_volume"] = float(saved_opt.get("sfx_volume", 0.5))
            sound.set_music_volume(SETTINGS["music_volume"])
            sound.set_sfx_volume(SETTINGS["sfx_volume"])

    except Exception as e:
        print(f"Ошибка чтения save.json: {e}")

def save_game():
    data = {
        "score": score,
        "total_score": total_score,
        "lifetime_score": lifetime_score,
        "total_clicks": total_clicks,
        "rubies": rubies,
        "click_power": click_power,
        "auto_income": auto_income,
        "upgrade_click_cost": upgrade_click_cost,
        "upgrade_auto_cost": upgrade_auto_cost,
        "level": level,
        "xp": xp,
        "xp_needed": xp_needed,
        "crit_chance": crit_chance,
        "crit_level": crit_level,
        "upgrade_crit_cost": upgrade_crit_cost,
        "has_combo": has_combo,
        "achievements": {k: v["unlocked"] for k, v in ACHIEVEMENTS.items()},
        "current_lang": current_lang,
        "settings": SETTINGS,
    }
    
    temp_file = SAVE_FILE + ".tmp"
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        os.replace(temp_file, SAVE_FILE)
    except Exception as e:
        print(f"Ошибка сохранения save.json: {e}")

# ==========================================
# 🛠️ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ И АЧИВКИ
# ==========================================
def check_achievements():
    for key, ach in ACHIEVEMENTS.items():
        if not ach["unlocked"] and ach["check"]():
            ach["unlocked"] = True
            show_achievement_toast(key)
            save_game()

def show_achievement_toast(ach_key):
    sound.play_sfx("achievement.ogg")
    ach = ACHIEVEMENTS[ach_key][current_lang]
    t = LANGUAGES[current_lang]

    toast_frame = tk.Frame(root, bg=STONE_PANEL_BG, bd=4, relief="ridge", highlightbackground=STONE_TEXT_GOLD, highlightthickness=2)
    
    lbl_title = tk.Label(toast_frame, text=t["ach_unlocked"], font=("Arial", 10, "bold"), fg=STONE_TEXT_GOLD, bg=STONE_PANEL_BG)
    lbl_title.pack(padx=15, pady=(5, 2))
    
    lbl_name = tk.Label(toast_frame, text=f"{ach['title']}: {ach['desc']}", font=("Arial", 9), fg=STONE_TEXT_LIGHT, bg=STONE_PANEL_BG)
    lbl_name.pack(padx=15, pady=(0, 5))

    toast_frame.place(relx=0.5, rely=0.88, anchor="center")

    def animate_toast(steps=20):
        if steps > 0:
            root.after(100, lambda: animate_toast(steps - 1))
        else:
            toast_frame.destroy()

    animate_toast()

def set_game_icon(root_window):
    icon_path = os.path.join(BASE_DIR, "icon.png")
    if os.path.exists(icon_path):
        try:
            img = tk.PhotoImage(file=icon_path)
            root_window.iconphoto(True, img)
            root_window._app_icon = img
        except Exception:
            pass

def bind_hover_sound(widget):
    widget.bind("<Enter>", lambda e: sound.play_sfx("hover.ogg"), add="+")

def open_link(url):
    sound.play_sfx("click.ogg")
    webbrowser.open(url)

def format_num(num):
    try:
        num = int(num)
    except (ValueError, TypeError):
        return str(num)

    if abs(num) < 1000:
        return f"{num}"

    units = ["", "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp", "Oc", "No", "Dc"]
    unit_index = 0
    val = float(num)

    while abs(val) >= 1000.0 and unit_index < len(units) - 1:
        val /= 1000.0
        unit_index += 1

    return f"{val:.3f} {units[unit_index]}"

def toggle_language():
    sound.play_sfx("click.ogg")
    global current_lang
    current_lang = "en" if current_lang == "ru" else "ru"
    update_ui()
    if main_menu_canvas.find_withtag("settings_window") or game_canvas.find_withtag("settings_window"):
        show_settings_screen()
    if main_menu_canvas.find_withtag("achievements_window") or game_canvas.find_withtag("achievements_window"):
        show_achievements_screen()

def check_prohibited_processes():
    global is_blocked_by_process
    found_process = None
    try:
        for proc in psutil.process_iter(["name"]):
            try:
                proc_name = proc.info["name"]
                if proc_name and proc_name.lower() in BLOCKED_PROCESSES:
                    found_process = proc_name
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception:
        pass

    if found_process:
        if not is_blocked_by_process:
            is_blocked_by_process = True
            show_cheat_block_screen(found_process)
    else:
        if is_blocked_by_process:
            is_blocked_by_process = False
            hide_cheat_block_screen()

    root.after(3000, check_prohibited_processes)

def show_cheat_block_screen(process_name):
    t = LANGUAGES[current_lang]
    main_menu_frame.pack_forget()
    main_game_frame.pack_forget()
    main_menu_canvas.delete("settings_window")
    main_menu_canvas.delete("exit_window")
    main_menu_canvas.delete("achievements_window")
    game_canvas.delete("settings_window")
    game_canvas.delete("exit_window")
    game_canvas.delete("achievements_window")

    block_label.config(text=t["blocked_title"].format(proc=process_name))
    btn_quit_blocked.config(text=t["blocked_quit"])
    block_frame.pack(expand=True)

def hide_cheat_block_screen():
    block_frame.pack_forget()
    if current_screen == "main_menu":
        show_main_menu()
    else:
        show_game_screen()

def add_xp(amount):
    global xp, level, xp_needed
    xp += amount
    while xp >= xp_needed:
        xp -= xp_needed
        level += 1
        xp_needed = int(xp_needed * 1.4)
        level_label.config(fg="#ffd166")
        root.after(500, lambda: level_label.config(fg="#e0e3e8"))
    check_achievements()

def get_random_ore():
    rand_val = random.random()
    cumulative = 0.0
    for ore in ORE_TYPES:
        cumulative += ore["chance"]
        if rand_val <= cumulative:
            return ore
    return ORE_TYPES[0]

def toggle_particles():
    sound.play_sfx("click.ogg")
    if SETTINGS["particles"] == "full":
        SETTINGS["particles"] = "minimal"
    elif SETTINGS["particles"] == "minimal":
        SETTINGS["particles"] = "off"
    else:
        SETTINGS["particles"] = "full"
    update_ui()

def toggle_miner_visibility():
    sound.play_sfx("click.ogg")
    SETTINGS["show_miner"] = not SETTINGS["show_miner"]
    active_canvas = main_menu_canvas if current_screen == "main_menu" else game_canvas
    draw_miner(active_canvas, swing=False)
    update_ui()

def update_ui():
    t = LANGUAGES[current_lang]
    
    menu_title_label.config(text=t["title"])
    btn_menu_play.config(text=t["play_btn"])
    btn_menu_achievements.config(text=t["achievements_btn"])
    btn_menu_settings.config(text=t["main_settings_btn"])
    btn_menu_exit.config(text=t["main_exit_btn"])
    btn_menu_lang.config(text=t["lang_btn"])

    ruby_buff = 1 + (rubies * 0.5)
    level_buff = 1 + ((level - 1) * 0.1)
    total_multiplier = ruby_buff * level_buff

    current_hit = int(click_power * total_multiplier)
    current_cps = int(auto_income * total_multiplier)

    score_label.config(text=f"{t['score']}{format_num(score)}")
    info_label.config(
        text=(
            f"{t['hit']}{format_num(current_hit)}\n{t['drills']}{format_num(current_cps)}{t['per_sec']}"
        )
    )

    ruby_bonus_percent = int((ruby_buff - 1) * 100)
    ruby_label.config(
        text=(
            f"{t['rubies']}{format_num(rubies)}"
            f" (+{format_num(ruby_bonus_percent)}%)"
        )
    )
    level_label.config(
        text=(
            f"{t['miner_lvl']}{level}"
            f" ({format_num(xp)}/{format_num(xp_needed)} XP) | x{level_buff:.1f}"
        )
    )

    if has_combo and combo_multiplier > 1.0:
        combo_label.config(text=f"{t['rhythm']}{combo_multiplier:.1f}! 🔥")
    else:
        combo_label.config(text="")

    btn_click_upg.config(text=f"{t['upg_click']}{format_num(upgrade_click_cost)}")
    btn_auto_upg.config(text=f"{t['upg_auto']}{format_num(upgrade_auto_cost)}")

    if crit_chance >= 0.50:
        btn_crit_upg.config(
            text=t["upg_crit_max"], state="disabled", bg="#22252a", fg="#6c757d"
        )
    else:
        btn_crit_upg.config(
            text=(
                f"{t['upg_crit']}{int(crit_chance*100)}{t['crit_price']}{format_num(upgrade_crit_cost)}"
            ),
            state="normal",
            bg=STONE_BTN_BG,
            fg=STONE_TEXT_LIGHT,
        )

    if has_combo:
        btn_combo_upg.config(
            text=t["combo_bought"], state="disabled", bg="#22252a", fg="#6c757d"
        )
    elif score >= combo_cost:
        btn_combo_upg.config(
            text=f"{t['combo_btn']}{format_num(combo_cost)}",
            state="normal",
            bg=STONE_BTN_BG,
            fg=STONE_TEXT_GOLD,
        )
    else:
        btn_combo_upg.config(
            text=t["combo_need"], state="disabled", bg="#22252a", fg="#6c757d"
        )

    btn_prestige.config(text=t["prestige"])
    if score >= 10000:
        btn_prestige.config(state="normal", bg="#5c2427", fg="#ff595e")
    else:
        btn_prestige.config(state="disabled", bg="#22252a", fg="#6c757d")

    btn_main_menu.config(text=t["menu_btn"])
    btn_settings.config(text=t["settings_btn"])
    btn_achievements.config(text=t["achievements_btn"])
    btn_lang.config(text=t["lang_btn"])

    if SETTINGS["particles"] == "full":
        btn_opt_particles.config(text=t["part_full"])
    elif SETTINGS["particles"] == "minimal":
        btn_opt_particles.config(text=t["part_min"])
    else:
        btn_opt_particles.config(text=t["part_off"])

    btn_opt_miner.config(
        text=t["miner_on"] if SETTINGS["show_miner"] else t["miner_off"]
    )

    lbl_vol_music.config(text=t["vol_music"])
    lbl_vol_sfx.config(text=t["vol_sfx"])

    check_achievements()
    save_game()

def draw_stone_wall(canvas, w, h):
    global _last_wall_size
    if _last_wall_size == (w, h) and canvas.find_withtag("stone_bg"):
        return
    _last_wall_size = (w, h)

    canvas.delete("stone_bg")
    canvas.create_rectangle(
        0, 0, w, h, fill=STONE_BG_CANVAS, outline="", tags="stone_bg"
    )

    brick_h = 40
    brick_w = 90
    random.seed(42)

    for row, y in enumerate(range(0, h + brick_h, brick_h)):
        offset = (row % 2) * (brick_w // 2)
        for x in range(-brick_w, w + brick_w, brick_w):
            bx = x + offset
            by = y
            canvas.create_rectangle(
                bx,
                by,
                bx + brick_w,
                by + brick_h,
                outline="#1d1f23",
                width=2,
                tags="stone_bg",
            )
            if random.random() > 0.6:
                canvas.create_line(
                    bx + random.randint(10, 70),
                    by + random.randint(5, 35),
                    bx + random.randint(10, 70),
                    by + random.randint(5, 35),
                    fill="#181a1d",
                    width=1,
                    tags="stone_bg",
                )
    random.seed()

def draw_miner(canvas, swing=False):
    canvas.delete("miner")

    w = canvas.winfo_width()
    h = canvas.winfo_height()

    if w <= 10 or h <= 10:
        return

    if canvas == main_menu_canvas:
        cx = int(w * 0.65) - 40
    else:
        cx = w // 2 - 40

    cy = h // 2 + 30

    canvas.create_oval(
        cx - 240,
        cy + 130,
        cx + 340,
        cy + 175,
        fill="#0d0e10",
        outline="",
        tags="miner",
    )

    canvas.create_polygon(
        cx + 90,
        cy + 140,
        cx + 310,
        cy + 150,
        cx + 350,
        cy - 20,
        cx + 230,
        cy - 130,
        cx + 100,
        cy - 20,
        fill="#2b2e34",
        outline="#0d0e10",
        width=4,
        tags="miner",
    )
    canvas.create_polygon(
        cx + 100,
        cy - 20,
        cx + 230,
        cy - 130,
        cx + 190,
        cy + 50,
        fill="#383c44",
        outline="",
        tags="miner",
    )
    canvas.create_polygon(
        cx + 230,
        cy - 130,
        cx + 350,
        cy - 20,
        cx + 280,
        cy + 30,
        fill="#484e58",
        outline="",
        tags="miner",
    )
    ore_color = STONE_TEXT_GOLD if not swing else "#ffffff"
    canvas.create_polygon(
        cx + 130,
        cy + 20,
        cx + 180,
        cy - 10,
        cx + 160,
        cy + 50,
        fill=ore_color,
        outline="#e0a96d",
        width=2,
        tags="miner",
    )
    canvas.create_polygon(
        cx + 230,
        cy + 60,
        cx + 290,
        cy + 30,
        cx + 270,
        cy + 100,
        fill=ore_color,
        outline="#e0a96d",
        width=2,
        tags="miner",
    )

    if SETTINGS["show_miner"]:
        canvas.create_rectangle(
            cx - 165,
            cy + 110,
            cx - 115,
            cy + 145,
            fill="#2b2e34",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )
        canvas.create_rectangle(
            cx - 165, cy + 135, cx - 115, cy + 145, fill="#ff595e", outline="", tags="miner"
        )

        canvas.create_rectangle(
            cx - 105,
            cy + 110,
            cx - 55,
            cy + 145,
            fill="#2b2e34",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )
        canvas.create_rectangle(
            cx - 105, cy + 135, cx - 55, cy + 145, fill="#ff595e", outline="", tags="miner"
        )

        canvas.create_rectangle(
            cx - 165,
            cy - 30,
            cx - 55,
            cy + 120,
            fill="#2a4d69",
            outline="#0d0e10",
            width=4,
            tags="miner",
        )
        canvas.create_rectangle(
            cx - 150, cy - 10, cx - 70, cy + 110, fill="#4b86b4", outline="", tags="miner"
        )
        canvas.create_polygon(
            cx - 125,
            cy + 15,
            cx - 95,
            cy + 15,
            cx - 95,
            cy + 60,
            cx - 110,
            cy + 75,
            cx - 125,
            cy + 60,
            fill="#2a4d69",
            outline="#1c3144",
            width=2,
            tags="miner",
        )
        canvas.create_oval(
            cx - 114,
            cy + 25,
            cx - 106,
            cy + 33,
            fill=STONE_TEXT_GOLD,
            outline="",
            tags="miner",
        )

        canvas.create_oval(
            cx - 185,
            cy - 155,
            cx - 35,
            cy - 25,
            fill="#e0a96d",
            outline="#0d0e10",
            width=4,
            tags="miner",
        )
        canvas.create_oval(
            cx - 170, cy - 70, cx - 130, cy - 50, fill="#d48c46", outline="", tags="miner"
        )

        canvas.create_rectangle(
            cx - 150,
            cy - 110,
            cx - 70,
            cy - 80,
            fill="#2b2e34",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )
        canvas.create_oval(
            cx - 145,
            cy - 107,
            cx - 112,
            cy - 83,
            fill="#89dceb",
            outline="#0d0e10",
            width=2,
            tags="miner",
        )
        canvas.create_oval(
            cx - 108,
            cy - 107,
            cx - 75,
            cy - 83,
            fill="#89dceb",
            outline="#0d0e10",
            width=2,
            tags="miner",
        )

        canvas.create_oval(
            cx - 195,
            cy - 180,
            cx - 25,
            cy - 100,
            fill="#ffd166",
            outline="#0d0e10",
            width=4,
            tags="miner",
        )
        canvas.create_rectangle(
            cx - 205,
            cy - 120,
            cx - 15,
            cy - 105,
            fill="#e0a96d",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )

        canvas.create_rectangle(
            cx - 100,
            cy - 150,
            cx - 60,
            cy - 115,
            fill="#484e58",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )
        canvas.create_oval(
            cx - 93,
            cy - 145,
            cx - 67,
            cy - 120,
            fill="#ffffff",
            outline="#ffd166",
            width=2,
            tags="miner",
        )

        canvas.create_polygon(
            cx - 67,
            cy - 132,
            cx + 250,
            cy - 60,
            cx + 190,
            cy + 110,
            fill="#fff4d3",
            outline="",
            stipple="gray25",
            tags="miner",
        )

        if not swing:
            canvas.create_line(
                cx - 70,
                cy + 20,
                cx + 30,
                cy - 60,
                fill="#0d0e10",
                width=32,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx - 70,
                cy + 20,
                cx + 30,
                cy - 60,
                fill="#e0a96d",
                width=24,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx - 20,
                cy + 40,
                cx + 140,
                cy - 190,
                fill="#5c3d2e",
                width=16,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx - 10,
                cy + 25,
                cx + 130,
                cy - 175,
                fill="#8b5e34",
                width=6,
                capstyle="round",
                tags="miner",
            )
            canvas.create_polygon(
                cx + 80,
                cy - 220,
                cx + 190,
                cy - 180,
                cx + 160,
                cy - 140,
                cx + 100,
                cy - 180,
                fill="#8d99ae",
                outline="#0d0e10",
                width=3,
                tags="miner",
            )
        else:
            canvas.create_line(
                cx - 70,
                cy + 20,
                cx + 100,
                cy + 60,
                fill="#0d0e10",
                width=32,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx - 70,
                cy + 20,
                cx + 100,
                cy + 60,
                fill="#e0a96d",
                width=24,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx + 30,
                cy - 30,
                cx + 200,
                cy + 130,
                fill="#5c3d2e",
                width=16,
                capstyle="round",
                tags="miner",
            )
            canvas.create_line(
                cx + 40,
                cy - 20,
                cx + 190,
                cy + 115,
                fill="#8b5e34",
                width=6,
                capstyle="round",
                tags="miner",
            )
            canvas.create_polygon(
                cx + 160,
                cy + 80,
                cx + 260,
                cy + 150,
                cx + 220,
                cy + 180,
                cx + 150,
                cy + 110,
                fill="#ffd166",
                outline="#0d0e10",
                width=3,
                tags="miner",
            )
    else:
        canvas.create_rectangle(
            cx - 140,
            cy + 10,
            cx - 40,
            cy + 145,
            fill="#383c44",
            outline="#0d0e10",
            width=4,
            tags="miner",
        )
        canvas.create_rectangle(
            cx - 120,
            cy - 40,
            cx - 60,
            cy + 10,
            fill="#484e58",
            outline="#0d0e10",
            width=3,
            tags="miner",
        )
        drill_col = STONE_TEXT_GOLD if swing else "#8d99ae"
        canvas.create_polygon(
            cx - 60,
            cy + 20,
            cx + 90,
            cy + 50,
            cx - 60,
            cy + 80,
            fill=drill_col,
            outline="#0d0e10",
            width=3,
            tags="miner",
        )

    if swing and SETTINGS["particles"] != "off":
        count = 8 if SETTINGS["particles"] == "full" else 3
        for _ in range(count):
            sx = cx + random.randint(160, 240)
            sy = cy + random.randint(60, 140)
            color = random.choice([STONE_TEXT_GOLD, "#ffffff", "#ff595e", "#89dceb"])
            spark = canvas.create_oval(
                sx,
                sy,
                sx + random.randint(5, 10),
                sy + random.randint(5, 10),
                fill=color,
                outline="",
            )
            animate_spark(canvas, spark, random.randint(-40, 40), random.randint(-45, -15))

def animate_spark(canvas, spark_id, dx, dy, steps=10):
    if steps > 0:
        canvas.move(spark_id, dx, dy)
        root.after(25, lambda: animate_spark(canvas, spark_id, dx * 0.9, dy + 2.0, steps - 1))
    else:
        canvas.delete(spark_id)

def spawn_floating_text(canvas, x, y, text, color):
    txt_id = canvas.create_text(
        x, y, text=text, font=("Impact", 28, "bold"), fill=color
    )

    def float_up(steps=15):
        if steps > 0:
            canvas.move(txt_id, random.randint(-1, 1), -4)
            root.after(30, lambda: float_up(steps - 1))
        else:
            canvas.delete(txt_id)

    float_up()

def animate_menu_miner():
    if current_screen == "main_menu" and not is_blocked_by_process:
        draw_miner(main_menu_canvas, swing=True)
        root.after(120, lambda: draw_miner(main_menu_canvas, swing=False))
    root.after(1200, animate_menu_miner)

def trigger_anti_cheat():
    global score, is_penalized, click_timestamps, combo_multiplier, tap_count
    t = LANGUAGES[current_lang]
    is_penalized = True
    click_timestamps.clear()
    combo_multiplier = 1.0
    tap_count = 0

    penalty = max(int(score * 0.15), 50) if score > 0 else 0
    score = max(0, score - penalty)

    cx = game_canvas.winfo_width() // 2
    cy = game_canvas.winfo_height() // 2
    spawn_floating_text(
        game_canvas, cx, cy - 100, f"{t['anticheat']}{format_num(penalty)}", STONE_TEXT_CRIT
    )
    draw_miner(game_canvas, False)
    update_ui()
    root.after(5000, lift_penalty)

def lift_penalty():
    global is_penalized
    is_penalized = False
    update_ui()

def tap(event=None):
    global score, total_score, lifetime_score, total_clicks, last_tap_time, tap_count, combo_multiplier
    global click_timestamps, is_penalized
    t = LANGUAGES[current_lang]

    if is_penalized or is_blocked_by_process:
        return

    sound.play_sfx("click.ogg")

    now = time.time()
    click_timestamps.append(now)
    click_timestamps = [t_time for t_time in click_timestamps if now - t_time <= 1.0]

    if len(click_timestamps) >= 20:
        trigger_anti_cheat()
        return

    total_clicks += 1

    if has_combo:
        if now - last_tap_time < 0.4:
            tap_count += 1
            if tap_count >= 15:
                combo_multiplier = 2.5
            elif tap_count >= 8:
                combo_multiplier = 1.8
            elif tap_count >= 3:
                combo_multiplier = 1.3
        else:
            tap_count = 1
            combo_multiplier = 1.0
    else:
        combo_multiplier = 1.0

    last_tap_time = now

    ore = get_random_ore()
    ore_name = ore["name_ru"] if current_lang == "ru" else ore["name_en"]

    ruby_buff = 1 + (rubies * 0.5)
    level_buff = 1 + ((level - 1) * 0.1)
    base_gain = click_power * ruby_buff * level_buff * combo_multiplier * ore["mult"]

    click_x = event.x if event else game_canvas.winfo_width() // 2 + 60
    click_y = event.y if event else game_canvas.winfo_height() // 2

    is_crit = random.random() < crit_chance
    if is_crit:
        gained = int(base_gain * 5)
        spawn_floating_text(
            game_canvas,
            click_x,
            click_y - 20,
            f"{ore_name}! +{format_num(gained)}{t['crit_text']}",
            STONE_TEXT_CRIT,
        )
    else:
        gained = int(base_gain)
        spawn_floating_text(
            game_canvas, click_x, click_y - 20, f"{ore_name} +{format_num(gained)}", ore["color"]
        )

    score += gained
    total_score += gained
    lifetime_score += gained
    add_xp(1)

    draw_miner(game_canvas, swing=True)
    root.after(110, lambda: draw_miner(game_canvas, swing=False))

    update_ui()

def check_combo_decay():
    global combo_multiplier, tap_count
    if has_combo and (time.time() - last_tap_time > 0.8):
        if combo_multiplier > 1.0:
            combo_multiplier = 1.0
            tap_count = 0
            update_ui()
    root.after(300, check_combo_decay)

def buy_click_upgrade():
    sound.play_sfx("click.ogg")
    global score, click_power, upgrade_click_cost
    if score >= upgrade_click_cost:
        score -= upgrade_click_cost
        click_power += 1
        upgrade_click_cost = int(upgrade_click_cost * 1.5)
        update_ui()

def buy_auto_upgrade():
    sound.play_sfx("click.ogg")
    global score, auto_income, upgrade_auto_cost
    if score >= upgrade_auto_cost:
        score -= upgrade_auto_cost
        auto_income += 1
        upgrade_auto_cost = int(upgrade_auto_cost * 1.6)
        update_ui()

def buy_crit_upgrade():
    sound.play_sfx("click.ogg")
    global score, crit_chance, crit_level, upgrade_crit_cost
    if score >= upgrade_crit_cost and crit_chance < 0.50:
        score -= upgrade_crit_cost
        crit_chance += 0.03
        crit_level += 1
        upgrade_crit_cost = int(upgrade_crit_cost * 1.8)
        update_ui()

def buy_combo():
    sound.play_sfx("click.ogg")
    global score, has_combo
    if not has_combo and score >= combo_cost:
        score -= combo_cost
        has_combo = True
        update_ui()

def prestige():
    sound.play_sfx("click.ogg")
    global score, total_score, rubies, click_power, auto_income, upgrade_click_cost, upgrade_auto_cost
    global crit_chance, crit_level, upgrade_crit_cost, has_combo, level, xp, xp_needed

    if score >= 10000:
        earned_rubies = score // 10000
        rubies += earned_rubies

        score = 0
        total_score = 0
        click_power = 1
        auto_income = 0
        upgrade_click_cost = 10
        upgrade_auto_cost = 20
        crit_chance = 0.05
        crit_level = 0
        upgrade_crit_cost = 50
        has_combo = False

        level = 1
        xp = 0
        xp_needed = 100

        update_ui()

def spawn_lucky_coin():
    if is_blocked_by_process or current_screen != "game":
        root.after(5000, spawn_lucky_coin)
        return

    t = LANGUAGES[current_lang]
    next_spawn = random.randint(15, 35) * 1000
    rel_x = random.uniform(0.2, 0.8)
    rel_y = random.uniform(0.2, 0.6)

    lucky_btn = tk.Button(
        root,
        text=t["lucky_ore"],
        font=("Arial", 12, "bold"),
        bg=STONE_TEXT_GOLD,
        fg="#11111b",
        bd=4,
        relief="raised",
        command=lambda: catch_lucky_coin(lucky_btn),
    )
    bind_hover_sound(lucky_btn)
    lucky_btn.place(relx=rel_x, rely=rel_y)

    root.after(3500, lambda: lucky_btn.destroy() if lucky_btn.winfo_exists() else None)
    root.after(next_spawn, spawn_lucky_coin)

def catch_lucky_coin(btn_obj):
    sound.play_sfx("click.ogg")
    global score, total_score, lifetime_score
    t = LANGUAGES[current_lang]
    ruby_buff = 1 + (rubies * 0.5)
    level_buff = 1 + ((level - 1) * 0.1)
    bonus = int(
        (click_power * 25 + auto_income * 10 + 50) * ruby_buff * level_buff
    )

    score += bonus
    total_score += bonus
    lifetime_score += bonus
    btn_obj.destroy()
    spawn_floating_text(
        game_canvas,
        game_canvas.winfo_width() // 2,
        100,
        f"{t['bonus']}{format_num(bonus)}!",
        STONE_TEXT_GOLD,
    )
    update_ui()

def toggle_fullscreen(event=None):
    sound.play_sfx("click.ogg")
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    root.attributes("-fullscreen", is_fullscreen)

def reset_progress():
    sound.play_sfx("click.ogg")
    global score, total_score, lifetime_score, total_clicks, rubies, click_power, auto_income
    global upgrade_click_cost, upgrade_auto_cost, upgrade_crit_cost, crit_chance, crit_level
    global has_combo, level, xp, xp_needed, is_penalized
    t = LANGUAGES[current_lang]

    if messagebox.askyesno(t["reset_confirm_title"], t["reset_confirm_msg"]):
        score = 0
        total_score = 0
        lifetime_score = 0
        total_clicks = 0
        rubies = 0
        click_power = 1
        auto_income = 0
        upgrade_click_cost = 10
        upgrade_auto_cost = 20
        crit_chance = 0.05
        crit_level = 0
        upgrade_crit_cost = 50
        has_combo = False
        level = 1
        xp = 0
        xp_needed = 100
        is_penalized = False

        for ach in ACHIEVEMENTS.values():
            ach["unlocked"] = False

        if os.path.exists(SAVE_FILE):
            try:
                os.remove(SAVE_FILE)
            except Exception:
                pass
        update_ui()
        if current_screen == "main_menu":
            show_main_menu()
        else:
            show_game_screen()

def show_main_menu():
    global current_screen
    if is_blocked_by_process:
        return
    current_screen = "main_menu"
    sound.play_music("music_menu.mp3")
    main_game_frame.pack_forget()
    main_menu_canvas.delete("settings_window")
    main_menu_canvas.delete("exit_window")
    main_menu_canvas.delete("achievements_window")
    
    main_menu_frame.pack(fill="both", expand=True)
    draw_stone_wall(main_menu_canvas, main_menu_canvas.winfo_width(), main_menu_canvas.winfo_height())
    draw_miner(main_menu_canvas, swing=False)

def show_game_screen():
    sound.play_sfx("click.ogg")
    global current_screen
    if is_blocked_by_process:
        return
    current_screen = "game"
    sound.play_music("music_game.mp3")
    main_menu_frame.pack_forget()
    game_canvas.delete("settings_window")
    game_canvas.delete("exit_window")
    game_canvas.delete("achievements_window")
    
    main_game_frame.pack(fill="both", expand=True)
    draw_stone_wall(game_canvas, game_canvas.winfo_width(), game_canvas.winfo_height())
    draw_miner(game_canvas, swing=False)

def on_music_volume_change(val):
    v = float(val) / 100.0
    SETTINGS["music_volume"] = v
    sound.set_music_volume(v)
    save_game()

def on_sfx_volume_change(val):
    v = float(val) / 100.0
    SETTINGS["sfx_volume"] = v
    sound.set_sfx_volume(v)
    save_game()

def show_settings_screen():
    sound.play_sfx("click.ogg")
    if is_blocked_by_process:
        return
    t = LANGUAGES[current_lang]
    settings_title_label.config(text=t["settings_title"])
    opt_title_label.config(text=t["opt_title"])
    stats_label.config(
        text=t["stats_text"].format(
            clicks=format_num(total_clicks),
            lifetime=format_num(lifetime_score),
            lvl=level,
            rubs=format_num(rubies),
        )
    )
    btn_mode.config(text=t["toggle_screen"])
    btn_reset.config(text=t["reset_btn"])
    btn_back_sets.config(text=t["back_btn"])

    music_slider.set(int(SETTINGS.get("music_volume", 0.5) * 100))
    sfx_slider.set(int(SETTINGS.get("sfx_volume", 0.5) * 100))

    active_canvas = main_menu_canvas if current_screen == "main_menu" else game_canvas
    active_canvas.delete("exit_window")
    active_canvas.delete("achievements_window")

    active_canvas.create_window(
        active_canvas.winfo_width() - 20,
        20,
        anchor="ne",
        window=settings_frame,
        tags="settings_window",
    )

def hide_settings_screen():
    sound.play_sfx("click.ogg")
    main_menu_canvas.delete("settings_window")
    game_canvas.delete("settings_window")

def show_achievements_screen():
    sound.play_sfx("click.ogg")
    if is_blocked_by_process:
        return
    t = LANGUAGES[current_lang]
    ach_title_label.config(text=t["achievements_title"])
    btn_back_ach.config(text=t["back_btn"])

    for widget in ach_list_frame.winfo_children():
        widget.destroy()

    for key, ach in ACHIEVEMENTS.items():
        data = ach[current_lang]
        status = "✅ " if ach["unlocked"] else "🔒 "
        color = STONE_TEXT_GOLD if ach["unlocked"] else "#6c757d"
        
        item_frame = tk.Frame(ach_list_frame, bg=STONE_BG_MAIN, bd=2, relief="groove")
        item_frame.pack(fill="x", pady=4, padx=5)

        lbl = tk.Label(
            item_frame,
            text=f"{status}{data['title']}\n{data['desc']}",
            font=("Arial", 9, "bold" if ach["unlocked"] else "normal"),
            fg=color,
            bg=STONE_BG_MAIN,
            justify="left"
        )
        lbl.pack(anchor="w", padx=8, pady=4)

    active_canvas = main_menu_canvas if current_screen == "main_menu" else game_canvas
    active_canvas.delete("settings_window")
    active_canvas.delete("exit_window")

    active_canvas.create_window(
        active_canvas.winfo_width() // 2,
        active_canvas.winfo_height() // 2,
        anchor="center",
        window=achievements_frame,
        tags="achievements_window",
    )

def hide_achievements_screen():
    sound.play_sfx("click.ogg")
    main_menu_canvas.delete("achievements_window")
    game_canvas.delete("achievements_window")

def show_exit_confirm_screen():
    sound.play_sfx("click.ogg")
    if is_blocked_by_process:
        quit_game()
        return
    t = LANGUAGES[current_lang]
    exit_label.config(text=t["exit_title"])
    btn_yes_exit.config(text=t["exit_yes"])
    btn_no_exit.config(text=t["exit_no"])

    active_canvas = main_menu_canvas if current_screen == "main_menu" else game_canvas
    active_canvas.delete("settings_window")
    active_canvas.delete("achievements_window")

    active_canvas.create_window(
        active_canvas.winfo_width() // 2,
        active_canvas.winfo_height() // 2,
        anchor="center",
        window=exit_confirm_frame,
        tags="exit_window",
    )

def hide_exit_confirm_screen():
    sound.play_sfx("click.ogg")
    main_menu_canvas.delete("exit_window")
    game_canvas.delete("exit_window")

def quit_game():
    save_game()
    root.destroy()

def auto_farm():
    global score, total_score, lifetime_score
    if not is_blocked_by_process:
        ruby_buff = 1 + (rubies * 0.5)
        level_buff = 1 + ((level - 1) * 0.1)
        gained = int(auto_income * ruby_buff * level_buff)

        score += gained
        total_score += gained
        lifetime_score += gained
        if auto_income > 0:
            add_xp(1)

        update_ui()
    root.after(1000, auto_farm)

def on_menu_canvas_resize(event):
    w = event.width
    h = event.height

    draw_stone_wall(main_menu_canvas, w, h)
    draw_miner(main_menu_canvas, swing=False)

    if main_menu_canvas.find_withtag("menu_ui"):
        main_menu_canvas.coords("menu_ui", int(w * 0.05), h // 2)

    if main_menu_canvas.find_withtag("top_hud"):
        main_menu_canvas.itemconfig("top_hud", width=w, height=PANEL_HEIGHT)
        main_menu_canvas.coords("top_hud", 0, 0)

    if main_menu_canvas.find_withtag("bottom_hud"):
        main_menu_canvas.itemconfig("bottom_hud", width=w, height=PANEL_HEIGHT)
        main_menu_canvas.coords("bottom_hud", 0, h - PANEL_HEIGHT)

    if main_menu_canvas.find_withtag("settings_window"):
        main_menu_canvas.coords("settings_window", w - 20, 20)
    if main_menu_canvas.find_withtag("achievements_window"):
        main_menu_canvas.coords("achievements_window", w // 2, h // 2)
    if main_menu_canvas.find_withtag("exit_window"):
        main_menu_canvas.coords("exit_window", w // 2, h // 2)

def on_game_canvas_resize(event):
    draw_stone_wall(game_canvas, event.width, event.height)
    draw_miner(game_canvas, swing=False)
    if game_canvas.find_withtag("settings_window"):
        game_canvas.coords("settings_window", event.width - 20, 20)
    if game_canvas.find_withtag("achievements_window"):
        game_canvas.coords("achievements_window", event.width // 2, event.height // 2)
    if game_canvas.find_withtag("exit_window"):
        game_canvas.coords("exit_window", event.width // 2, event.height // 2)

# ==========================================
# 🚀 ИНИЦИАЛИЗАЦИЯ ОКНА И ГРАФИКИ
# ==========================================
root = tk.Tk()
root.title("Miner Simulator")

set_game_icon(root)

window_width = 1280
window_height = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int((screen_width / 2) - (window_width / 2))
center_y = int((screen_height / 2) - (window_height / 2))

root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
root.attributes("-fullscreen", True)
root.configure(bg=STONE_BG_MAIN)

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", lambda e: hide_settings_screen() if (main_menu_canvas.find_withtag("settings_window") or game_canvas.find_withtag("settings_window")) else (hide_achievements_screen() if (main_menu_canvas.find_withtag("achievements_window") or game_canvas.find_withtag("achievements_window")) else show_exit_confirm_screen()))
root.protocol("WM_DELETE_WINDOW", show_exit_confirm_screen)

# ---------------- ЭКРАН БЛОКИРОВКИ ----------------
block_frame = tk.Frame(root, bg=STONE_BG_MAIN)
block_label = tk.Label(
    block_frame,
    text="",
    font=("Arial", 18, "bold"),
    fg=STONE_TEXT_CRIT,
    bg=STONE_BG_MAIN,
    justify="center",
)
block_label.pack(pady=20)

btn_quit_blocked = tk.Button(
    block_frame,
    text="",
    font=("Arial", 11, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    command=quit_game,
    width=20,
    height=2,
)
bind_hover_sound(btn_quit_blocked)
btn_quit_blocked.pack(pady=10)

# ---------------- 1. ГЛАВНОЕ МЕНЮ ----------------
main_menu_frame = tk.Frame(root, bg=STONE_BG_MAIN)

main_menu_canvas = tk.Canvas(
    main_menu_frame,
    bg=STONE_BG_CANVAS,
    bd=0,
    highlightthickness=0,
)
main_menu_canvas.pack(fill="both", expand=True)
main_menu_canvas.bind("<Configure>", on_menu_canvas_resize)

menu_top_hud = tk.Frame(
    main_menu_canvas,
    bg=STONE_PANEL_BG,
    bd=3,
    relief="ridge",
    height=PANEL_HEIGHT,
)

main_menu_canvas.create_window(
    0,
    0,
    anchor="nw",
    window=menu_top_hud,
    width=window_width,
    height=PANEL_HEIGHT,
    tags="top_hud",
)

menu_buttons_frame = tk.Frame(main_menu_canvas, bg=STONE_PANEL_BG, bd=6, relief="ridge")

menu_title_label = tk.Label(
    menu_buttons_frame,
    text="",
    font=("Impact", 36, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
menu_title_label.pack(pady=(20, 15), padx=40)

btn_menu_play = tk.Button(
    menu_buttons_frame,
    text="",
    font=("Arial", 16, "bold"),
    bg="#3a5a40",
    fg="#a3b18a",
    activebackground="#344e41",
    activeforeground="#dad7cd",
    bd=4,
    relief="raised",
    width=18,
    height=2,
    command=show_game_screen,
)
bind_hover_sound(btn_menu_play)
btn_menu_play.pack(pady=8)

btn_menu_achievements = tk.Button(
    menu_buttons_frame,
    text="",
    font=("Arial", 14, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=4,
    relief="raised",
    width=18,
    height=1,
    command=show_achievements_screen,
)
bind_hover_sound(btn_menu_achievements)
btn_menu_achievements.pack(pady=8)

btn_menu_settings = tk.Button(
    menu_buttons_frame,
    text="",
    font=("Arial", 14, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=4,
    relief="raised",
    width=18,
    height=1,
    command=show_settings_screen,
)
bind_hover_sound(btn_menu_settings)
btn_menu_settings.pack(pady=8)

btn_menu_exit = tk.Button(
    menu_buttons_frame,
    text="",
    font=("Arial", 14, "bold"),
    bg="#5c2427",
    fg="#ff595e",
    activebackground="#3a1618",
    activeforeground="#ff595e",
    bd=4,
    relief="raised",
    width=18,
    height=1,
    command=show_exit_confirm_screen,
)
bind_hover_sound(btn_menu_exit)
btn_menu_exit.pack(pady=8)

btn_menu_lang = tk.Button(
    menu_buttons_frame,
    text="",
    font=("Arial", 10, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    command=toggle_language,
)
bind_hover_sound(btn_menu_lang)
btn_menu_lang.pack(pady=(8, 20))

main_menu_canvas.create_window(
    60, window_height // 2, anchor="w", window=menu_buttons_frame, tags="menu_ui"
)

menu_bottom_hud = tk.Frame(
    main_menu_canvas,
    bg=STONE_PANEL_BG,
    bd=3,
    relief="ridge",
    height=PANEL_HEIGHT,
)

version_label = tk.Label(
    menu_bottom_hud,
    text=CURRENT_VERSION,
    font=("Impact", 13),
    fg="#ff595e",
    bg=STONE_PANEL_BG,
)
version_label.pack(side="left", padx=15)

btn_boosty = tk.Button(
    menu_bottom_hud,
    text="Boosty",
    font=("Arial", 9, "bold"),
    bg="#e64a19",
    fg="#ffffff",
    activebackground="#bf360c",
    activeforeground="#ffffff",
    bd=2,
    relief="raised",
    command=lambda: open_link(BOOSTY_URL),
)
bind_hover_sound(btn_boosty)
btn_boosty.pack(side="right", padx=(4, 15), pady=6)

btn_yt = tk.Button(
    menu_bottom_hud,
    text="YouTube",
    font=("Arial", 9, "bold"),
    bg="#d32f2f",
    fg="#ffffff",
    activebackground="#9a0007",
    activeforeground="#ffffff",
    bd=2,
    relief="raised",
    command=lambda: open_link(YOUTUBE_URL),
)
bind_hover_sound(btn_yt)
btn_yt.pack(side="right", padx=4, pady=6)

btn_da = tk.Button(
    menu_bottom_hud,
    text="DonationAlerts",
    font=("Arial", 9, "bold"),
    bg="#f57c00",
    fg="#ffffff",
    activebackground="#b75100",
    activeforeground="#ffffff",
    bd=2,
    relief="raised",
    command=lambda: open_link(DONATIONALERTS_URL),
)
bind_hover_sound(btn_da)
btn_da.pack(side="right", padx=4, pady=6)

main_menu_canvas.create_window(
    0,
    window_height - PANEL_HEIGHT,
    anchor="nw",
    window=menu_bottom_hud,
    width=window_width,
    height=PANEL_HEIGHT,
    tags="bottom_hud",
)

# ---------------- 2. ОСНОВНАЯ ИГРА ----------------
main_game_frame = tk.Frame(root, bg=STONE_BG_MAIN)

top_hud = tk.Frame(
    main_game_frame,
    bg=STONE_PANEL_BG,
    bd=4,
    relief="ridge",
    highlightbackground=STONE_PANEL_BORDER,
)
top_hud.pack(fill="x", padx=15, pady=10)

hud_left = tk.Frame(top_hud, bg=STONE_PANEL_BG)
hud_left.pack(side="left", padx=10, pady=5)

score_label = tk.Label(
    hud_left,
    text="",
    font=("Arial", 24, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
score_label.pack(anchor="w")

info_label = tk.Label(
    hud_left,
    text="",
    font=("Arial", 10, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
    justify="left",
)
info_label.pack(anchor="w")

hud_center = tk.Frame(top_hud, bg=STONE_PANEL_BG)
hud_center.pack(side="left", expand=True)

level_label = tk.Label(
    hud_center,
    text="",
    font=("Arial", 11, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
)
level_label.pack()

ruby_label = tk.Label(
    hud_center,
    text="",
    font=("Arial", 11, "bold"),
    fg=STONE_TEXT_CRIT,
    bg=STONE_PANEL_BG,
)
ruby_label.pack()

combo_label = tk.Label(
    hud_center,
    text="",
    font=("Arial", 13, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
combo_label.pack()

hud_right = tk.Frame(top_hud, bg=STONE_PANEL_BG)
hud_right.pack(side="right", padx=10)

btn_main_menu = tk.Button(
    hud_right,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    command=show_main_menu,
)
bind_hover_sound(btn_main_menu)
btn_main_menu.pack(side="right", padx=(5, 0))

btn_settings = tk.Button(
    hud_right,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    command=show_settings_screen,
)
bind_hover_sound(btn_settings)
btn_settings.pack(side="right", padx=(5, 0))

btn_achievements = tk.Button(
    hud_right,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    command=show_achievements_screen,
)
bind_hover_sound(btn_achievements)
btn_achievements.pack(side="right", padx=(5, 0))

btn_lang = tk.Button(
    hud_right,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    command=toggle_language,
)
bind_hover_sound(btn_lang)
btn_lang.pack(side="right")

game_canvas = tk.Canvas(
    main_game_frame,
    bg=STONE_BG_CANVAS,
    bd=0,
    highlightthickness=0,
    cursor="hand2",
)
game_canvas.pack(fill="both", expand=True, padx=15)
game_canvas.bind("<Button-1>", tap)
game_canvas.bind("<Configure>", on_game_canvas_resize)

bottom_hud = tk.Frame(
    main_game_frame,
    bg=STONE_PANEL_BG,
    bd=4,
    relief="ridge",
    highlightbackground=STONE_PANEL_BORDER,
)
bottom_hud.pack(fill="x", padx=15, pady=10)

upg_frame = tk.Frame(bottom_hud, bg=STONE_PANEL_BG)
upg_frame.pack(pady=5)

btn_click_upg = tk.Button(
    upg_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=23,
    command=buy_click_upgrade,
)
bind_hover_sound(btn_click_upg)
btn_click_upg.grid(row=0, column=0, padx=4, pady=2)

btn_auto_upg = tk.Button(
    upg_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=23,
    command=buy_auto_upgrade,
)
bind_hover_sound(btn_auto_upg)
btn_auto_upg.grid(row=0, column=1, padx=4, pady=2)

btn_crit_upg = tk.Button(
    upg_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=23,
    command=buy_crit_upgrade,
)
bind_hover_sound(btn_crit_upg)
btn_crit_upg.grid(row=0, column=2, padx=4, pady=2)

btn_combo_upg = tk.Button(
    upg_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    width=23,
    command=buy_combo,
)
bind_hover_sound(btn_combo_upg)
btn_combo_upg.grid(row=0, column=3, padx=4, pady=2)

btn_prestige = tk.Button(
    upg_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_CRIT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_CRIT,
    bd=3,
    relief="raised",
    width=23,
    command=prestige,
)
bind_hover_sound(btn_prestige)
btn_prestige.grid(row=0, column=4, padx=4, pady=2)

# ---------------- ОВЕРЛЕЙ: НАСТРОЙКИ ----------------
settings_frame = tk.Frame(root, bg=STONE_PANEL_BG, bd=6, relief="ridge")

settings_title_label = tk.Label(
    settings_frame,
    text="",
    font=("Arial", 16, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
settings_title_label.pack(pady=8, padx=20)

stats_label = tk.Label(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
    justify="left",
)
stats_label.pack(pady=4)

btn_mode = tk.Button(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=26,
    command=toggle_fullscreen,
)
bind_hover_sound(btn_mode)
btn_mode.pack(pady=(8, 3))

opt_title_label = tk.Label(
    settings_frame,
    text="",
    font=("Arial", 11, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
opt_title_label.pack(pady=(12, 4))

lbl_vol_music = tk.Label(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
)
lbl_vol_music.pack(anchor="w", padx=15, pady=(4, 0))

music_slider = tk.Scale(
    settings_frame,
    from_=0,
    to=100,
    orient="horizontal",
    bg=STONE_PANEL_BG,
    fg=STONE_TEXT_LIGHT,
    highlightthickness=0,
    troughcolor=STONE_BG_MAIN,
    activebackground=STONE_TEXT_GOLD,
    command=on_music_volume_change,
    length=200,
)
music_slider.pack(pady=(0, 4))

lbl_vol_sfx = tk.Label(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
)
lbl_vol_sfx.pack(anchor="w", padx=15, pady=(4, 0))

sfx_slider = tk.Scale(
    settings_frame,
    from_=0,
    to=100,
    orient="horizontal",
    bg=STONE_PANEL_BG,
    fg=STONE_TEXT_LIGHT,
    highlightthickness=0,
    troughcolor=STONE_BG_MAIN,
    activebackground=STONE_TEXT_GOLD,
    command=on_sfx_volume_change,
    length=200,
)
sfx_slider.pack(pady=(0, 6))

btn_opt_particles = tk.Button(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=26,
    command=toggle_particles,
)
bind_hover_sound(btn_opt_particles)
btn_opt_particles.pack(pady=2)

btn_opt_miner = tk.Button(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=26,
    command=toggle_miner_visibility,
)
bind_hover_sound(btn_opt_miner)
btn_opt_miner.pack(pady=2)

btn_reset = tk.Button(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg="#5c2427",
    fg="#ff595e",
    activebackground="#3a1618",
    activeforeground="#ff595e",
    bd=3,
    relief="raised",
    width=26,
    command=reset_progress,
)
bind_hover_sound(btn_reset)
btn_reset.pack(pady=(12, 3))

btn_back_sets = tk.Button(
    settings_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    width=26,
    command=hide_settings_screen,
)
bind_hover_sound(btn_back_sets)
btn_back_sets.pack(pady=8)

# ---------------- ОВЕРЛЕЙ: ДОСТИЖЕНИЯ ----------------
achievements_frame = tk.Frame(root, bg=STONE_PANEL_BG, bd=6, relief="ridge")

ach_title_label = tk.Label(
    achievements_frame,
    text="",
    font=("Arial", 16, "bold"),
    fg=STONE_TEXT_GOLD,
    bg=STONE_PANEL_BG,
)
ach_title_label.pack(pady=10, padx=25)

ach_list_frame = tk.Frame(achievements_frame, bg=STONE_PANEL_BG)
ach_list_frame.pack(pady=5, padx=10, fill="both", expand=True)

btn_back_ach = tk.Button(
    achievements_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_GOLD,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_GOLD,
    bd=3,
    relief="raised",
    width=22,
    command=hide_achievements_screen,
)
bind_hover_sound(btn_back_ach)
btn_back_ach.pack(pady=10)

# ---------------- ОВЕРЛЕЙ: ВЫХОД ----------------
exit_confirm_frame = tk.Frame(root, bg=STONE_PANEL_BG, bd=6, relief="ridge")

exit_label = tk.Label(
    exit_confirm_frame,
    text="",
    font=("Arial", 16, "bold"),
    fg=STONE_TEXT_LIGHT,
    bg=STONE_PANEL_BG,
    justify="center",
)
exit_label.pack(pady=15, padx=25)

btn_yes_exit = tk.Button(
    exit_confirm_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg="#5c2427",
    fg="#ff595e",
    activebackground="#3a1618",
    activeforeground="#ff595e",
    bd=3,
    relief="raised",
    width=22,
    height=2,
    command=quit_game,
)
bind_hover_sound(btn_yes_exit)
btn_yes_exit.pack(pady=6)

btn_no_exit = tk.Button(
    exit_confirm_frame,
    text="",
    font=("Arial", 9, "bold"),
    bg=STONE_BTN_BG,
    fg=STONE_TEXT_LIGHT,
    activebackground=STONE_BTN_ACTIVE,
    activeforeground=STONE_TEXT_LIGHT,
    bd=3,
    relief="raised",
    width=22,
    height=2,
    command=hide_exit_confirm_screen,
)
bind_hover_sound(btn_no_exit)
btn_no_exit.pack(pady=6)

# ==========================================
# 🎮 СТАРТ ИГРОВОГО ЦИКЛА
# ==========================================
load_game()
show_main_menu()
update_ui()
auto_farm()
check_combo_decay()
check_prohibited_processes()
animate_menu_miner()
check_for_updates()
root.after(10000, spawn_lucky_coin)

root.mainloop()