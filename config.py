"""
Конфигурационный файл NS Body Scan
"""

import os

# Секретный ключ (в продакшене должен быть в переменных окружения)
SECRET_KEY = 'ns_body_scan_secret_key_2026'

# Папка для загрузки фото
UPLOAD_FOLDER = 'uploads'

# Расширения разрешённых файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Настройки MediaPipe
MEDIAPIPE_SETTINGS = {
    'static_image_mode': True,
    'min_detection_confidence': 0.5,
    'model_complexity': 1
}

# Цели пользователя
GOALS = {
    'lose': 'Похудение',
    'gain': 'Набор массы',
    'tone': 'Подтянутое тело',
    'posture': 'Коррекция осанки'
}

# Уровни активности
ACTIVITY_LEVELS = {
    '1.2': 'Минимальный (сидячая работа)',
    '1.375': 'Низкий (1-2 тренировки в неделю)',
    '1.55': 'Средний (3-5 тренировок)',
    '1.725': 'Высокий (ежедневные тренировки)'
}

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_PATH = os.path.join(BASE_DIR, UPLOAD_FOLDER)
EXERCISES_FILE = os.path.join(BASE_DIR, 'exercises.json')

# Создаём папку для загрузки, если её нет
os.makedirs(UPLOAD_PATH, exist_ok=True)

# ========== НАСТРОЙКИ POSTGRESQL ==========
# Импортируем пароль из секретного файла
from db_secret import DB_PASSWORD

DB_CONFIG = {
    'dbname': 'ns_body_scan',
    'user': 'postgres',
    'password': DB_PASSWORD,
    'host': 'localhost',
    'port': '5432'
}

# ========== НАСТРОЙКИ GIGACHAT ==========
GIGACHAT_AUTH_KEY = "MDE5ZDEwOTAtMWVkMy03NjgxLThmOTEtNDdhYzE5NDlkYzgwOjBlNDIyMzRmLThjNmQtNDFmNS1iMDUyLWQ4OTVjNWM0Y2ZjZQ=="

# ========== НАСТРОЙКИ EXERCISEDB API ==========
EXERCISEDB_API_KEY = "f7b1970b4fmshab4a7caadcbb35fp126741jsn27ab090ace7d"
EXERCISEDB_HOST = "exercisedb.p.rapidapi.com"