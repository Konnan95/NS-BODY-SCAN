"""
Вспомогательные функции
"""

import re
import os
from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS, UPLOAD_PATH


def is_latin(text):
    """Проверяет, состоит ли текст только из латинских букв, цифр и символа _"""
    return bool(re.match(r'^[a-zA-Z0-9_]+$', text))


def allowed_file(filename):
    """Проверяет, разрешён ли тип файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_photo(file, username, view_type):
    """Сохраняет фото и возвращает путь"""
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{username}_{view_type}_{file.filename}")
        filepath = os.path.join(UPLOAD_PATH, filename)
        file.save(filepath)
        return filepath
    return None


def calculate_kbju(weight, height, age, activity, goal):
    """Расчёт КБЖУ на основе данных пользователя"""
    height_cm = float(height)
    weight_kg = float(weight)
    age_years = int(age)
    activity_factor = float(activity)
    
    # BMR по формуле Миффлина-Сан Жеора (для женщин)
    bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161
    
    # Дневная норма калорий
    calories = bmr * activity_factor
    
    # Корректировка под цель
    if goal == 'lose':
        calories -= 300
    elif goal == 'gain':
        calories += 300
    
    # Белки, жиры, углеводы
    if goal == 'gain':
        protein = weight_kg * 2.0
    else:
        protein = weight_kg * 1.5
    
    fat = weight_kg * 0.8
    carbs = (calories - (protein * 4) - (fat * 9)) / 4
    if carbs < 0:
        carbs = 100
    
    return {
        'calories': round(calories),
        'protein': round(protein),
        'fat': round(fat),
        'carbs': round(carbs)
    }