"""
Конфигурационный файл NS Body Scan
Секреты загружаются из .env файла
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Секретный ключ (из переменных окружения)
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

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

# Создаём папку для загрузки, если её нет
os.makedirs(UPLOAD_PATH, exist_ok=True)

# ========== НАСТРОЙКИ POSTGRESQL ==========
DB_CONFIG = {
    'dbname': os.environ.get('DB_NAME', 'ns_body_scan'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': os.environ.get('DB_PORT', '5432')
}

# ========== НАСТРОЙКИ GIGACHAT ==========
GIGACHAT_AUTH_KEY = os.environ.get('GIGACHAT_AUTH_KEY')

# ========== НАСТРОЙКИ EXERCISEDB API ==========
EXERCISEDB_API_KEY = os.environ.get('EXERCISEDB_API_KEY')
EXERCISEDB_HOST = os.environ.get('EXERCISEDB_HOST', 'exercisedb.p.rapidapi.com')

# ========== ПРОВЕРКА ОБЯЗАТЕЛЬНЫХ ПЕРЕМЕННЫХ ==========
if not DB_CONFIG['password']:
    print("⚠️ ВНИМАНИЕ: DB_PASSWORD не задан в .env файле!")

if not SECRET_KEY or SECRET_KEY == 'change-me-in-production':
    print("⚠️ ВНИМАНИЕ: SECRET_KEY не задан в .env файле!")

if not GIGACHAT_AUTH_KEY:
    print("⚠️ ВНИМАНИЕ: GIGACHAT_AUTH_KEY не задан в .env файле!")

if not EXERCISEDB_API_KEY:
    print("⚠️ ВНИМАНИЕ: EXERCISEDB_API_KEY не задан в .env файле!")