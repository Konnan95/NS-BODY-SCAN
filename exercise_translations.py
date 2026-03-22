"""
Сопоставление русских названий упражнений с английскими из базы ExerciseDB
"""

TRANSLATIONS = {
    # ГРУДЬ
    'жим гантелей лёжа': 'Dumbbell Bench Press',
    'жим гантелей лежа': 'Dumbbell Bench Press',
    'жим гантелей': 'Dumbbell Bench Press',
    'разводка гантелей лёжа': 'Dumbbell Fly',
    'разводка гантелей': 'Dumbbell Fly',
    
    # СПИНА
    'тяга верхнего блока': 'Lat Pulldown',
    'тяга верхнего блока широким хватом': 'Wide Grip Lat Pulldown',
    'гиперэкстензия': 'Hyperextension',
    'обратные гиперэкстензии': 'Reverse Hyperextension',
    'вертикальная тяга': 'Lat Pulldown',
    
    # НОГИ
    'приседания со штангой': 'Barbell Squat',
    'приседания': 'Barbell Squat',
    'выпады с гантелями': 'Dumbbell Lunge',
    'выпады': 'Lunge',
    'становая тяга': 'Deadlift',
    'мертвая тяга': 'Deadlift',
    'ягодичный мостик': 'Glute Bridge',
    'мостик с весом': 'Glute Bridge',
    
    # ПЛЕЧИ
    'жим гантелей сидя': 'Seated Dumbbell Press',
    'подъём гантелей перед собой': 'Dumbbell Front Raise',
    'махи гантелей назад': 'Dumbbell Rear Delt Fly',
    'протяжка гантелей вверх': 'Dumbbell Upright Row',
    
    # РУКИ
    'отжимания от лавочки': 'Bench Dip',
    'отжимания от лавки': 'Bench Dip',
    'сгибание рук с гантелями': 'Dumbbell Curl',
    'разгибание рук стоя': 'Tricep Extension',
    
    # ПРЕСС
    'скручивания': 'Crunch',
    'подъем ног': 'Leg Raise',
    
    # ДРУГИЕ
    'планка': 'Plank',
    'растяжка плеч': 'Shoulder Stretch',
    
    # НОВЫЕ ДОБАВЛЕНИЯ
    'приседания сумо': 'Barbell Squat',  # или Sumo Squat
    'тяга гантелей стоя': 'Dumbbell Upright Row',
    'жим лёжа узким хватом': 'Close Grip Bench Press',
    'отведение ноги назад': 'Donkey Kick',
    'мёртвая тяга сидя': 'Seated Good Morning',
    'становая тяга на одной ноге': 'Single Leg Deadlift',
    'наклон вперёд с весом': 'Good Morning',
    'лодочка': 'Superman',
    'боковое скручивание': 'Side Crunch',
    'махи гирей (гантелью)': 'Kettlebell Swing',
    'подъём таза лёжа': 'Hip Thrust',
    'повороты корпуса': 'Russian Twist',
    'румынская тяга': 'Romanian Deadlift',
    'приседания пистолетом': 'Pistol Squat',
    'болгарский сплит-присед': 'Bulgarian Split Squat',
    'сгибание ног сидя': 'Seated Leg Curl',
    'глубокие выпады': 'Deep Lunge',
    'жим ногами сидя': 'Seated Leg Press',
    'мостик обратным хватом': 'Reverse Bridge',
}

def translate_exercise_name(russian_name):
    """Перевести русское название упражнения в английское"""
    name_lower = russian_name.lower().strip()
    
    # Прямое совпадение
    if name_lower in TRANSLATIONS:
        return TRANSLATIONS[name_lower]
    
    # Поиск по ключевым словам
    for key, value in TRANSLATIONS.items():
        if key in name_lower:
            return value
    
    return None