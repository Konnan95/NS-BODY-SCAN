"""
Сопоставление упражнений с локальными GIF-файлами
"""

import os

MEDIA_DIR = os.path.join(os.path.dirname(__file__), 'static', 'media')

def get_gif_for_exercise(exercise_name):
    """Получить путь к GIF для упражнения по названию"""
    # Нормализуем название (убираем пробелы, спецсимволы)
    name_key = exercise_name.lower().replace(' ', '_').replace('-', '_')
    
    # Ищем файл, который начинается с этого ключа
    if os.path.exists(MEDIA_DIR):
        for file in os.listdir(MEDIA_DIR):
            if file.lower().startswith(name_key) and file.endswith('.gif'):
                return f'/static/media/{file}'
    return None