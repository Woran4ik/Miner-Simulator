import os
import pygame

# Инициализируем микшер pygame
pygame.mixer.init()

# Словари для кэширования звуков и музыки
_sfx_cache = {}
_music_cache = {}
_current_music_channel = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def play_sfx(filename):
    """Воспроизведение коротких звуковых эффектов"""
    try:
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            path = filename

        if path not in _sfx_cache:
            _sfx_cache[path] = pygame.mixer.Sound(path)
        
        _sfx_cache[path].play()
    except Exception as e:
        print(f"[Sound Error] Ошибка SFX ({filename}): {e}")

def play_music(filename, loops=-1):
    """
    Воспроизведение фоновой музыки через mixer.Sound / Channel.
    Это решает проблему, когда pygame.mixer.music отказывается проигрывать MP3.
    """
    global _current_music_channel
    try:
        path = os.path.join(BASE_DIR, filename)
        if not os.path.exists(path):
            path = filename

        # Кэшируем музыкальный файл как Sound
        if path not in _music_cache:
            _music_cache[path] = pygame.mixer.Sound(path)

        sound_obj = _music_cache[path]

        # Используем выделенный канал (например, канал 7) для музыки
        if _current_music_channel is None:
            _current_music_channel = pygame.mixer.Channel(7)

        # Если эта же музыка уже играет — не перезапускаем
        if _current_music_channel.get_sound() == sound_obj and _current_music_channel.get_busy():
            return

        _current_music_channel.stop()
        _current_music_channel.play(sound_obj, loops=loops)
    except Exception as e:
        print(f"[Sound Error] Ошибка Music ({filename}): {e}")

def stop_music():
    """Остановка музыки"""
    global _current_music_channel
    if _current_music_channel:
        _current_music_channel.stop()