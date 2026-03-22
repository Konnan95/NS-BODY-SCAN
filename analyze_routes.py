"""
Модуль анализа осанки
"""

from flask import request, redirect, url_for, session, flash, render_template
from database import get_user_by_id, save_posture_analysis, save_body_composition
from posture_analyzer import analyze_posture
from config import UPLOAD_FOLDER
import os
from giga_helper import ask_gigachat
from local_exercises import get_exercise_media, get_exercise_instructions, get_exercise_target_muscles
import re
from pdf_generator import generate_pdf_report
from exercise_translations import translate_exercise_name


def extract_exercises_from_text(text):
    """Извлечь названия упражнений из текста GigaChat (включая таблицы)"""
    print("\n🔍 НАЧАЛО ПАРСИНГА УПРАЖНЕНИЙ")
    exercises = []
    lines = text.split('\n')
    print(f"   Всего строк в тексте: {len(lines)}")
    
    # Показываем первые 20 строк для отладки
    print("\n   📄 ПЕРВЫЕ 20 СТРОК ТЕКСТА:")
    for i, line in enumerate(lines[:20]):
        print(f"      {i}: {line[:80]}")
    
    in_table = False
    for line in lines:
        # Проверяем начало таблицы
        if '| Упражнение' in line or '| Упражнение ' in line:
            in_table = True
            continue
        
        # Если мы внутри таблицы и строка содержит |, извлекаем упражнение
        if in_table and '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                # Название упражнения — после первого разделителя
                exercise_name = parts[1].strip()
                # Пропускаем пустые и служебные строки
                if exercise_name and exercise_name not in ['---', ' ', '']:
                    # Очищаем название от лишних символов
                    exercise_name = re.sub(r'\s*\d+.*$', '', exercise_name).strip()
                    if 3 < len(exercise_name) < 50 and 'упражнение' not in exercise_name.lower():
                        exercises.append({'name': exercise_name})
                        print(f"   ✅ НАЙДЕНО: {exercise_name}")
            continue
        
        # Выход из таблицы
        if in_table and (not line.strip() or '####' in line):
            in_table = False
        
        # Пропускаем другие строки
        if '|' in line or '—' in line or 'упражнение' in line.lower():
            continue
        if 'подход' in line.lower() or 'повтор' in line.lower():
            continue
        if 'День' in line or 'ПН' in line or 'ВТ' in line or 'СР' in line:
            continue
    
    print(f"\n🔍 ИТОГО НАЙДЕНО УПРАЖНЕНИЙ: {len(exercises)}")
    return exercises

def analyze_page():
    """Страница анализа осанки"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        results = []
        views = {'front': 'Спереди', 'back': 'Сзади', 'side': 'Сбоку'}
        
        for view, view_name in views.items():
            if view in request.files:
                file = request.files[view]
                if file and file.filename:
                    path = os.path.join(UPLOAD_FOLDER, f"{user['username']}_{view}_{file.filename}")
                    file.save(path)
                    result = analyze_posture(path)
                    if result:
                        results.append(result)
        
        if not results:
            flash('Не удалось проанализировать фото. Убедитесь, что на фото видно тело в полный рост.', 'danger')
            return redirect(url_for('analyze_page'))
        
        # Усредняем результаты
        avg_shoulder = sum(r['shoulder_slope'] for r in results) / len(results)
        avg_hip = sum(r['hip_slope'] for r in results) / len(results)
        avg_head = sum(r['head_tilt'] for r in results) / len(results)
        avg_score = sum(r['score'] for r in results) / len(results)
        
        # Сохраняем анализ осанки в БД
        save_posture_analysis(user['id'], avg_shoulder, avg_hip, avg_head, avg_score)
        
        # Расчёт КБЖУ
        height = float(user['height']) if user['height'] else 165
        weight = float(user['weight']) if user['weight'] else 65
        age = int(user['age']) if user['age'] else 30
        activity = float(user['activity']) if user['activity'] else 1.375
        goal = user['goal'] if user['goal'] else 'tone'
        
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        calories = bmr * activity
        
        if goal == 'lose':
            calories -= 300
        elif goal == 'gain':
            calories += 300
        
        protein = weight * 2.0 if goal == 'gain' else weight * 1.5
        fat = weight * 0.8
        carbs = (calories - (protein * 4) - (fat * 9)) / 4
        if carbs < 0:
            carbs = 100
        if calories < 1500:
            calories = 1500
        
        # Расчёт состава тела
        bmi = weight / ((height/100) ** 2)
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
        muscle_mass = weight * (100 - body_fat) / 100 * 0.45
        water = weight * 0.6
        visceral_fat = max(1, min(30, int((bmi - 18.5) * 2)))
        
        # Сохраняем состав тела
        save_body_composition(user['id'], body_fat, muscle_mass, water, visceral_fat)
        
        # ========== ГЕНЕРАЦИЯ AI-ПЛАНОВ ЧЕРЕЗ GIGACHAT ==========
        
        # Генерация плана тренировок
        workout_prompt = f"""
Составь план тренировок для человека:
- Пол: женщина
- Возраст: {age}
- Вес: {weight} кг
- Рост: {height} см
- Цель: {goal}
- Тип телосложения: {user.get('body_type', 'не указан')}
- Оборудование: {user.get('equipment', 'дом')}
- Травмы/ограничения: {user.get('injuries', 'нет')}
- Хронические заболевания: {user.get('chronic_diseases', 'нет')}
- Проблемные зоны: {user.get('problem_zones', 'нет')}
- Нарушения осанки: плечи {avg_shoulder:.1f}°, таз {avg_hip:.1f}°, голова {avg_head:.1f}°

Напиши 3 тренировки на неделю (пн, ср, пт). Для каждого упражнения укажи подходы и повторения. Учитывай оборудование и ограничения.
"""
        workout_plan_text = ask_gigachat(workout_prompt)
        
        print("\n" + "="*60)
        print("📋 ТЕКСТ ПЛАНА ТРЕНИРОВОК (первые 1000 символов):")
        print(workout_plan_text[:1000])
        print("="*60)
        
        # Извлекаем упражнения из текста GigaChat
                # Извлекаем упражнения из текста GigaChat
        extracted_exercises = extract_exercises_from_text(workout_plan_text)
        
        # Добавляем GIF для каждого найденного упражнения
        exercises_with_media = []
        for ex in extracted_exercises[:12]:  # максимум 12 упражнений
            name = ex['name'].lower()
            print(f"\n🔍 Ищем медиа для: {name}")
            
            # Пробуем перевести название
            english_name = translate_exercise_name(name)
            if english_name:
                print(f"   🔄 Перевод: '{name}' -> '{english_name}'")
                search_name = english_name
            else:
                search_name = name
                print(f"   ⚠️ Перевод не найден для: '{name}', ищем как '{search_name}'")
            
            media = get_exercise_media(search_name)
            instructions = get_exercise_instructions(search_name)
            muscles = get_exercise_target_muscles(search_name)
            exercises_with_media.append({
                'name': ex['name'],
                'media': media,
                'instructions': instructions[:2] if instructions else [],
                'target_muscles': muscles[:3] if muscles else []
            })
        
        print(f"\n📊 ИТОГО УПРАЖНЕНИЙ С МЕДИА: {len(exercises_with_media)}")
        
        # Генерация плана питания
        meal_prompt = f"""
Составь примерный план питания на день для человека:
- Цель: {goal}
- Калории: {calories:.0f} ккал
- Белки: {protein:.0f} г, жиры: {fat:.0f} г, углеводы: {carbs:.0f} г
- Тип телосложения: {user.get('body_type', 'не указан')}
- Количество приёмов пищи: {user.get('meals_per_day', 4)}
- Режим питания: {user.get('eating_schedule', '4')} приёма
- Любимые продукты: {user.get('favorite_foods', 'нет')}
- Нелюбимые продукты: {user.get('disliked_foods', 'нет')}
- Бюджет на питание: {user.get('food_budget', 'средний')}
- Аллергии: {user.get('allergies', 'нет')}
- Предпочтения: {user.get('preferences', 'нет')}
- Время пробуждения: {user.get('wake_time', 'не указано')}
- Время отхода ко сну: {user.get('sleep_time', 'не указано')}

Важно: калорийность не должна быть ниже 1500 ккал для безопасного похудения.
Напиши план на день с граммовками продуктов.
"""
        meal_plan = ask_gigachat(meal_prompt)
        
        # Генерация PDF-отчёта
        print("\n📄 ГЕНЕРАЦИЯ PDF-ОТЧЁТА...")
        pdf_url = generate_pdf_report(user, 
            {'shoulder': round(avg_shoulder, 1), 
             'hip': round(avg_hip, 1), 
             'head': round(avg_head, 1), 
             'score': round(avg_score, 1)},
            {'body_fat': round(body_fat, 1), 
             'muscle_mass': round(muscle_mass, 1), 
             'water': round(water, 1), 
             'visceral_fat': visceral_fat,
             'calories': round(calories, 0), 
             'protein': round(protein, 0), 
             'fat': round(fat, 0), 
             'carbs': round(carbs, 0)},
            workout_plan_text, 
            meal_plan)
        print(f"   ✅ PDF создан: {pdf_url}")
        
        # Показываем страницу с результатами
        return render_template('result.html',
            user=user,
            shoulder=round(avg_shoulder, 1),
            hip=round(avg_hip, 1),
            head=round(avg_head, 1),
            score=round(avg_score, 1),
            body_fat=round(body_fat, 1),
            muscle_mass=round(muscle_mass, 1),
            water=round(water, 1),
            visceral_fat=visceral_fat,
            calories=round(calories, 0),
            protein=round(protein, 0),
            fat=round(fat, 0),
            carbs=round(carbs, 0),
            workout_plan_text=workout_plan_text,
            meal_plan=meal_plan,
            exercises_with_media=exercises_with_media,
            pdf_url=pdf_url
        )
    
    return render_template('analyze.html', user=user)