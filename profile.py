"""
Модуль профиля пользователя
"""

from flask import request, redirect, url_for, session, flash, render_template
from database import get_user_by_id, update_user_profile


def profile_page():
    """Страница редактирования профиля"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Основные поля
        name = request.form.get('name', '')
        age = request.form.get('age', 0)
        height = request.form.get('height', 0)
        weight = request.form.get('weight', 0)
        goal = request.form.get('goal', '')
        activity = request.form.get('activity', 1.375)
        
        # Поля из расширенной анкеты
        equipment = request.form.get('equipment', '')
        injuries = request.form.get('injuries', '')
        chronic_diseases = request.form.get('chronic_diseases', '')
        problem_zones = request.form.get('problem_zones', '')
        allergies = request.form.get('allergies', '')
        preferences = request.form.get('preferences', '')
        wake_time = request.form.get('wake_time') or None
        sleep_time = request.form.get('sleep_time') or None
        
        # Новые поля
        body_type = request.form.get('body_type', '')
        meals_per_day = request.form.get('meals_per_day', 4)
        eating_schedule = request.form.get('eating_schedule', '4')
        favorite_foods = request.form.get('favorite_foods', '')
        disliked_foods = request.form.get('disliked_foods', '')
        food_budget = request.form.get('food_budget', 'medium')
        
        # Обновляем профиль с новыми полями
        update_user_profile(user['id'], name, age, height, weight, goal, activity,
                            equipment, injuries, chronic_diseases, problem_zones,
                            allergies, preferences, wake_time, sleep_time,
                            body_type, meals_per_day, eating_schedule,
                            favorite_foods, disliked_foods, food_budget)
        flash('Данные обновлены!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html', user=user)