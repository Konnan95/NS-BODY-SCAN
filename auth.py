from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_user_by_username, create_user, get_user_by_id
from config import GOALS, ACTIVITY_LEVELS
from utils import is_latin


def register_user():
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form.get('name', '')
        role = request.form.get('role', 'user')
        
        # Проверка латиницы
        if not is_latin(username):
            flash('Логин может содержать только латинские буквы, цифры и символ _', 'danger')
            return redirect(url_for('register'))
        
        # Проверка существования
        if get_user_by_username(username):
            flash('Пользователь уже существует', 'danger')
            return redirect(url_for('register'))
        
        if role == 'trainer':
            # Для тренера — упрощённая регистрация с дополнительными полями
            specialization = request.form.get('specialization', '')
            experience = request.form.get('experience', '')
            about = request.form.get('about', '')
            certifications = request.form.get('certifications', '')
            price_per_hour = request.form.get('price_per_hour', '')
            
            user_id = create_user(
                username=username,
                password=password,
                name=name,
                age=None,
                height=None,
                weight=None,
                goal=None,
                activity=None,
                role='trainer',
                subscription='free',
                specialization=specialization,
                experience=experience,
                about=about,
                certifications=certifications,
                price_per_hour=price_per_hour
            )
            flash('Регистрация тренера успешна! Войдите', 'success')
        else:
            # Для клиента — полная анкета
            age = request.form.get('age', 0, type=int)
            height = request.form.get('height', 0, type=float)
            weight = request.form.get('weight', 0, type=float)
            goal = request.form.get('goal', 'tone')
            activity = request.form.get('activity', '1.2')
            
            # Расширенная анкета (опционально)
            equipment = request.form.get('equipment', '')
            injuries = request.form.get('injuries', '')
            chronic_diseases = request.form.get('chronic_diseases', '')
            problem_zones = request.form.get('problem_zones', '')
            allergies = request.form.get('allergies', '')
            preferences = request.form.get('preferences', '')
            wake_time = request.form.get('wake_time') or None
            sleep_time = request.form.get('sleep_time') or None
            body_type = request.form.get('body_type', '')
            meals_per_day = request.form.get('meals_per_day', 4)
            eating_schedule = request.form.get('eating_schedule', '4')
            favorite_foods = request.form.get('favorite_foods', '')
            disliked_foods = request.form.get('disliked_foods', '')
            food_budget = request.form.get('food_budget', 'medium')
            
            user_id = create_user(
                username=username,
                password=password,
                name=name,
                age=age,
                height=height,
                weight=weight,
                goal=goal,
                activity=activity,
                role='user',
                equipment=equipment,
                injuries=injuries,
                chronic_diseases=chronic_diseases,
                problem_zones=problem_zones,
                allergies=allergies,
                preferences=preferences,
                wake_time=wake_time,
                sleep_time=sleep_time,
                body_type=body_type,
                meals_per_day=meals_per_day,
                eating_schedule=eating_schedule,
                favorite_foods=favorite_foods,
                disliked_foods=disliked_foods,
                food_budget=food_budget
            )
            flash('Регистрация успешна! Войдите', 'success')
        
        return redirect(url_for('login'))
    
    # GET запрос - показываем форму регистрации
    return render_template('simple_register.html')


def login_user():
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Вход выполнен!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')
    
    # GET запрос - показываем форму входа
    return render_template('simple_login.html')


def logout_user():
    """Выход из системы"""
    session.pop('user_id', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))