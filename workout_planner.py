"""
Генератор индивидуальных планов тренировок
"""

import json
import random
import os

# Путь к базе упражнений
EXERCISES_FILE = os.path.join(os.path.dirname(__file__), 'exercises.json')

def load_exercises():
    """Загружает базу упражнений из JSON"""
    try:
        with open(EXERCISES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Если файла нет, возвращаем базовый набор
        return {
            "squat": {"name": "Приседания", "video": "", "instructions": ""},
            "pushup": {"name": "Отжимания", "video": "", "instructions": ""}
        }

def get_exercise_video(exercise_key):
    """Получить видео для упражнения"""
    exercises = load_exercises()
    exercise = exercises.get(exercise_key)
    if exercise:
        return {
            'name': exercise['name'],
            'video_url': exercise.get('video', ''),
            'instructions': exercise.get('instructions', '')
        }
    return None

def generate_workout_plan(user_data, posture_data):
    """
    Генерация индивидуального плана тренировок
    
    user_data: {goal, activity_level, equipment}
    posture_data: {shoulder_slope, hip_slope, head_tilt}
    """
    
    exercises = load_exercises()
    
    # Определяем уровень сложности
    activity = user_data.get('activity_level', 1.375)
    if activity <= 1.375:
        difficulty = 'beginner'
        sets = 2
    elif activity <= 1.55:
        difficulty = 'intermediate'
        sets = 3
    else:
        difficulty = 'advanced'
        sets = 4
    
    # Базовые упражнения
    base_exercises = []
    
    # Добавляем приседания
    if 'squat' in exercises:
        base_exercises.append({
            'key': 'squat',
            'name': exercises['squat']['name'],
            'sets': sets,
            'reps': '12-15',
            'video': exercises['squat'].get('video', '')
        })
    
    # Добавляем отжимания
    if 'pushup' in exercises:
        base_exercises.append({
            'key': 'pushup',
            'name': exercises['pushup']['name'],
            'sets': sets,
            'reps': '8-12',
            'video': exercises['pushup'].get('video', '')
        })
    
    # Добавляем выпады
    if 'lunge' in exercises:
        base_exercises.append({
            'key': 'lunge',
            'name': exercises['lunge']['name'],
            'sets': sets,
            'reps': '10 на ногу',
            'video': exercises['lunge'].get('video', '')
        })
    
    # Корректирующие упражнения
    corrective = []
    
    # Для плеч
    if abs(posture_data.get('shoulder_slope', 0)) > 3:
        if 'face_pull' in exercises:
            corrective.append({
                'key': 'face_pull',
                'name': exercises['face_pull']['name'],
                'sets': 3,
                'reps': 15,
                'video': exercises['face_pull'].get('video', '')
            })
    
    # Для таза
    if abs(posture_data.get('hip_slope', 0)) > 3:
        if 'glute_bridge' in exercises:
            corrective.append({
                'key': 'glute_bridge',
                'name': exercises['glute_bridge']['name'],
                'sets': 3,
                'reps': 15,
                'video': exercises['glute_bridge'].get('video', '')
            })
        if 'side_plank' in exercises:
            corrective.append({
                'key': 'side_plank',
                'name': exercises['side_plank']['name'],
                'sets': 3,
                'duration': '30 сек',
                'video': exercises['side_plank'].get('video', '')
            })
    
    # Для головы/шеи
    if abs(posture_data.get('head_tilt', 0)) > 5:
        if 'neck_stretch' in exercises:
            corrective.append({
                'key': 'neck_stretch',
                'name': exercises['neck_stretch']['name'],
                'sets': 1,
                'reps': '10 повторений',
                'video': exercises['neck_stretch'].get('video', '')
            })
    
    # Формируем план на неделю
    weekly_plan = {
        'monday': {
            'name': 'Понедельник — Силовая + коррекция',
            'exercises': base_exercises[:2] + corrective[:2]
        },
        'wednesday': {
            'name': 'Среда — Кардио + растяжка',
            'exercises': [{'name': 'Быстрая ходьба 20-30 мин', 'sets': 1}]
        },
        'friday': {
            'name': 'Пятница — Силовая + коррекция',
            'exercises': base_exercises[2:] + corrective[2:4]
        }
    }
    
    return weekly_plan