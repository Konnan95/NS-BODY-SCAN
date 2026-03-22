"""
Модуль для работы с локальной базой упражнений ExerciseDB
Поддерживает GIF-анимации из полного файла exercises_full.json
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
EXERCISES_FILE = os.path.join(DATA_DIR, 'exercises_full.json')
MEDIA_DIR = '/static/media/'

# Запасной файл для YouTube-видео (если есть)
YOUTUBE_EXERCISES_FILE = os.path.join(DATA_DIR, 'exercises.json')

def load_exercises():
    """Загрузить все упражнения из полного JSON-файла"""
    if not os.path.exists(EXERCISES_FILE):
        print(f"❌ Файл {EXERCISES_FILE} не найден")
        return []
    with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_youtube_exercises():
    """Загрузить YouTube-упражнения (запасной вариант)"""
    if not os.path.exists(YOUTUBE_EXERCISES_FILE):
        return {}
    with open(YOUTUBE_EXERCISES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_exercise_by_name(name):
    """Найти упражнение по названию в полной базе"""
    exercises = load_exercises()
    name_lower = name.lower()
    for ex in exercises:
        if name_lower in ex.get('name', '').lower():
            return ex
    return None

def get_exercise_gif(name):
    """Получить локальный GIF для упражнения"""
    ex = find_exercise_by_name(name)
    if ex:
        gif_url = ex.get('gifUrl')
        if gif_url:
            filename = gif_url.split('/')[-1]
            return f'{MEDIA_DIR}{filename}'
    return None

def get_exercise_youtube(name):
    """Получить YouTube-видео для упражнения (запасной вариант)"""
    youtube_data = load_youtube_exercises()
    name_lower = name.lower()
    
    # Если это список, а не словарь
    if isinstance(youtube_data, list):
        for ex in youtube_data:
            if name_lower in ex.get('name', '').lower():
                return ex.get('video')
        return None
    
    # Если это словарь (старый формат)
    for key, ex in youtube_data.items():
        if name_lower in ex.get('name', '').lower() or name_lower in key.lower():
            return ex.get('video')
    return None

def get_exercise_media(name):
    """Получить медиа для упражнения (сначала GIF, если нет — YouTube)"""
    gif = get_exercise_gif(name)
    if gif:
        return {'type': 'gif', 'url': gif}
    
    youtube = get_exercise_youtube(name)
    if youtube:
        return {'type': 'youtube', 'url': youtube}
    
    return None

def get_exercise_instructions(name):
    """Получить инструкции для упражнения"""
    ex = find_exercise_by_name(name)
    if ex:
        return ex.get('instructions', [])
    return []

def get_exercise_target_muscles(name):
    """Получить целевые мышцы для упражнения"""
    ex = find_exercise_by_name(name)
    if ex:
        return ex.get('targetMuscles', [])
    return []

def get_exercise_equipment(name):
    """Получить оборудование для упражнения"""
    ex = find_exercise_by_name(name)
    if ex:
        return ex.get('equipments', [])
    return []

def list_all_exercises():
    """Получить список всех упражнений"""
    exercises = load_exercises()
    return [ex.get('name') for ex in exercises]