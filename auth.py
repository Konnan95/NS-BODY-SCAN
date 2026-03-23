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
        age = request.form.get('age', 0, type=int)
        height = request.form.get('height', 0, type=float)
        weight = request.form.get('weight', 0, type=float)
        goal = request.form.get('goal', 'tone')
        activity = request.form.get('activity', '1.2')
        
        # Проверка существования
        if get_user_by_username(username):
            flash('Пользователь уже существует', 'danger')
            return redirect(url_for('register'))
        
        # Создаем пользователя
        user_id = create_user(username, password, name, age, height, weight, goal, activity)
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