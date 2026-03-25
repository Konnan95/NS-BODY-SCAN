"""
Модуль анализа осанки
"""

from flask import request, redirect, url_for, session, flash, render_template
from database import get_user_by_id, save_posture_analysis, save_body_composition, save_workout_program, save_meal_plan
from posture_analyzer import analyze_posture, save_analyzed_photo, save_original_photo
from config import UPLOAD_FOLDER
import os
from giga_helper import ask_gigachat
from local_exercises import get_exercise_media, get_exercise_instructions, get_exercise_target_muscles
import re
from pdf_generator import generate_pdf_report
from body_fat_predictor_sklearn import body_fat_predictor
from bodypix_analyzer import bodypix
from exercise_translations import translate_exercise_name


def extract_exercises_from_text(text):
    """Извлечь названия упражнений из текста GigaChat"""
    exercises = []
    lines = text.split('\n')
    in_table = False
    for line in lines:
        if '| Упражнение' in line or '| Упражнение ' in line:
            in_table = True
            continue
        if in_table and '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                exercise_name = parts[1].strip()
                if exercise_name and exercise_name not in ['---', ' ', '']:
                    exercise_name = re.sub(r'\s*\d+.*$', '', exercise_name).strip()
                    if 3 < len(exercise_name) < 50 and 'упражнение' not in exercise_name.lower():
                        exercises.append({'name': exercise_name})
            continue
        if in_table and (not line.strip() or '####' in line):
            in_table = False
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
                    temp_path = os.path.join(UPLOAD_FOLDER, f"temp_{user['username']}_{view}_{file.filename}")
                    file.save(temp_path)
                    
                    try:
                        result = analyze_posture(temp_path)
                        if result:
                            original_path = save_original_photo(temp_path, user['id'], view)
                            analyzed_path = save_analyzed_photo(result['annotated_image'], user['id'], view)
                            
                            results.append({
                                'view': view,
                                'shoulder_tilt': result['shoulder_tilt'],
                                'hip_tilt': result['hip_tilt'],
                                'head_tilt': result['head_tilt'],
                                'kyphosis': result['kyphosis'],
                                'neck_angle': result['neck_angle'],
                                'knee_valgus': result['knee_valgus'],
                                'symmetry': result['symmetry'],
                                'score': result['posture_score'],
                                'original_path': original_path,
                                'analyzed_path': analyzed_path
                            })
                    except Exception as e:
                        print(f"Ошибка анализа {view}: {e}")
                        flash(f'Ошибка анализа {view_name}: {str(e)}', 'danger')
                    finally:
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
        
        if not results:
            flash('Не удалось проанализировать фото. Убедитесь, что на фото видно тело в полный рост.', 'danger')
            return redirect(url_for('analyze_page'))
        
        # Усредняем результаты
        avg_shoulder = sum(r['shoulder_tilt'] for r in results) / len(results)
        avg_hip = sum(r['hip_tilt'] for r in results) / len(results)
        avg_head = sum(r['head_tilt'] for r in results) / len(results)
        avg_kyphosis = sum(r.get('kyphosis', 0) for r in results) / len(results)
        avg_neck = sum(r.get('neck_angle', 0) for r in results) / len(results)
        avg_knee = sum(r.get('knee_valgus', 0) for r in results) / len(results)
        avg_symmetry = sum(r.get('symmetry', 0) for r in results) / len(results)
        avg_score = sum(r['score'] for r in results) / len(results)
        
        # Сохраняем все три фото с разметкой
        photo_paths = {'front': None, 'back': None, 'side': None}
        for r in results:
            view = r.get('view')
            if view and r.get('analyzed_path'):
                photo_paths[view] = r['analyzed_path']
        
        # Сохраняем анализ осанки в БД
        save_posture_analysis(
            user_id=user['id'],
            shoulder_slope=float(round(avg_shoulder, 1)),
            hip_slope=float(round(avg_hip, 1)),
            head_tilt=float(round(avg_head, 1)),
            posture_score=float(round(avg_score, 1)),
            kyphosis=float(round(avg_kyphosis, 1)) if avg_kyphosis else None,
            neck_angle=float(round(avg_neck, 1)) if avg_neck else None,
            knee_valgus=float(round(avg_knee, 1)) if avg_knee else None,
            symmetry=float(round(avg_symmetry, 1)) if avg_symmetry else None,
            original_photo_path=results[0].get('original_path') if results else None,
            analyzed_photo_path=photo_paths['back'],
            front_photo_path=photo_paths['front'],
            side_photo_path=photo_paths['side']
        )
        
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
        
        # Расчёт состава тела (ML модель Random Forest)
        measurements = {
            'neck': user.get('neck', 35),
            'waist': user.get('waist', 80),
            'hip': user.get('hip', 95),
            'height': height,
            'weight': weight,
            'age': age
        }
        
        result = body_fat_predictor.predict(measurements)
        
        if result:
            body_fat = result['body_fat']
            muscle_mass = result['muscle_mass']
            visceral_fat = result['visceral_fat']
            water = weight * 0.6
            print(f"🧬 ML-анализ: {result}")
            if 'details' in result:
                print(f"   📊 Детали: US Navy={result['details']['US Navy']}%, YMCA={result['details']['YMCA']}%, BMI={result['details']['BMI']}%")
        else:
            # Запасной вариант (формулы)
            bmi = weight / ((height/100) ** 2)
            body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
            muscle_mass = weight * (100 - body_fat) / 100 * 0.45
            water = weight * 0.6
            visceral_fat = max(1, min(30, int((bmi - 18.5) * 2)))
            print("⚠️ Использую формулы")
        
        # Сохраняем состав тела
        save_body_composition(user['id'], body_fat, muscle_mass, water, visceral_fat)
        
        # BodyPix анализ пропорций тела
        bodypix_result = None
        first_photo = None
        for r in results:
            if r.get('original_path'):
                first_photo = r['original_path']
                break
        
        if first_photo:
            bodypix_result = bodypix.analyze_from_image(first_photo)
            if bodypix_result and bodypix_result.get('success'):
                print(f"📊 BodyPix анализ: {bodypix_result['body_type']}, плечи/талия={bodypix_result['ratio_shoulder_waist']}, бёдра/талия={bodypix_result['ratio_hip_waist']}")
            else:
                print("⚠️ BodyPix анализ не удался")
        
        # Генерация плана тренировок
        workout_prompt = f"""
Составь план тренировок для человека:
- Пол: женщина
- Возраст: {age}
- Вес: {weight} кг
- Рост: {height} см
- Цель: {goal}
- Нарушения осанки: плечи {avg_shoulder:.1f}°, таз {avg_hip:.1f}°, голова {avg_head:.1f}°
Напиши 3 тренировки на неделю (пн, ср, пт). Для каждого упражнения укажи подходы и повторения.
"""
        workout_plan_text = ask_gigachat(workout_prompt)
        
        # Сохраняем программу тренировок в БД
        save_workout_program(
            user_id=user['id'],
            program_data=workout_plan_text,
            days_per_week=3,
            is_active=True
        )
        print(f"✅ Программа тренировок сохранена для user {user['id']}")
        
        # Извлекаем упражнения
        extracted_exercises = extract_exercises_from_text(workout_plan_text)
        
        # Добавляем GIF для упражнений
        exercises_with_media = []
        for ex in extracted_exercises[:12]:
            name = ex['name'].lower()
            english_name = translate_exercise_name(name)
            search_name = english_name if english_name else name
            media = get_exercise_media(search_name)
            instructions = get_exercise_instructions(search_name)
            muscles = get_exercise_target_muscles(search_name)
            exercises_with_media.append({
                'name': ex['name'],
                'media': media,
                'instructions': instructions[:2] if instructions else [],
                'target_muscles': muscles[:3] if muscles else []
            })
        
        # Генерация плана питания
        meal_prompt = f"""
Составь примерный план питания на день для человека:
- Цель: {goal}
- Калории: {calories:.0f} ккал
- Белки: {protein:.0f} г, жиры: {fat:.0f} г, углеводы: {carbs:.0f} г
Напиши план на день с граммовками продуктов.
"""
        meal_plan = ask_gigachat(meal_prompt)
        
        # Сохраняем план питания в БД
        save_meal_plan(
            user_id=user['id'],
            plan_data=meal_plan,
            is_active=True
        )
        print(f"✅ План питания сохранён для user {user['id']}")
        
        # Генерация PDF-отчёта
        pdf_url = generate_pdf_report(user, 
            {'shoulder': round(avg_shoulder, 1), 'hip': round(avg_hip, 1), 
             'head': round(avg_head, 1), 'score': round(avg_score, 1)},
            {'body_fat': round(body_fat, 1), 'muscle_mass': round(muscle_mass, 1), 
             'water': round(water, 1), 'visceral_fat': visceral_fat,
             'calories': round(calories, 0), 'protein': round(protein, 0), 
             'fat': round(fat, 0), 'carbs': round(carbs, 0)},
            workout_plan_text, meal_plan)
        
        return render_template('result.html',
            user=user,
            shoulder=round(avg_shoulder, 1),
            hip=round(avg_hip, 1),
            head=round(avg_head, 1),
            kyphosis=round(avg_kyphosis, 1),
            neck_angle=round(avg_neck, 1),
            knee_valgus=round(avg_knee, 1),
            symmetry=round(avg_symmetry, 1),
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
            pdf_url=pdf_url,
            analyzed_photo_path=photo_paths['back'],
            front_photo_path=photo_paths['front'],
            side_photo_path=photo_paths['side'],
            bodypix_result=bodypix_result
        )
    
    return render_template('analyze.html', user=user)