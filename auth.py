"""
Модуль аутентификации (с PostgreSQL)
"""

from flask import request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import GOALS, ACTIVITY_LEVELS
from utils import is_latin
from database import create_user, get_user_by_username, get_user_by_id


def register_user():
    """Обработка регистрации с PostgreSQL"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form.get('name', '')
        age = request.form.get('age', 0)
        height = request.form.get('height', 0)
        weight = request.form.get('weight', 0)
        goal = request.form.get('goal', '')
        activity = request.form.get('activity', 1.375)
        role = request.form.get('role', 'user')
        
        # Расширенная анкета
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
        
        # Проверка латиницы
        if not is_latin(username):
            flash('Логин может содержать только латинские буквы, цифры и символ _', 'danger')
            return redirect(url_for('register'))
        
        # Проверка существования пользователя
        existing = get_user_by_username(username)
        if existing:
            flash('Пользователь уже существует', 'danger')
        else:
            user_id = create_user(username, password, name, age, height, weight, goal, activity, role,
                                  equipment, injuries, chronic_diseases, problem_zones,
                                  allergies, preferences, wake_time, sleep_time,
                                  body_type, meals_per_day, eating_schedule,
                                  favorite_foods, disliked_foods, food_budget)
            flash('Регистрация успешна! Войдите', 'success')
            return redirect(url_for('login'))
    
    # HTML для страницы регистрации
    goal_options = ''.join(f'<option value="{k}">{v}</option>' for k, v in GOALS.items())
    activity_options = ''.join(f'<option value="{k}">{v}</option>' for k, v in ACTIVITY_LEVELS.items())
    
    # Опции для типа телосложения
    body_type_options = '''
        <option value="">Выберите тип телосложения</option>
        <option value="ectomorph">Эктоморф (худощавый, трудно набираю вес)</option>
        <option value="mesomorph">Мезоморф (спортивный от природы)</option>
        <option value="endomorph">Эндоморф (склонность к полноте)</option>
    '''
    
    # Опции для бюджета питания
    food_budget_options = '''
        <option value="economy">Эконом</option>
        <option value="medium">Средний</option>
        <option value="premium">Премиум</option>
    '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Регистрация - NS Body Scan</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: repeating-linear-gradient(45deg, #2c2c2c 0px, #2c2c2c 40px, #fff 40px, #fff 80px, #ff99cc 80px, #ff99cc 120px);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 50px auto;
                background: rgba(255,255,255,0.95);
                padding: 30px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            h1, h2 {{ text-align: center; color: #ff66b5; }}
            input, select {{
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 5px;
            }}
            button {{
                width: 100%;
                background: linear-gradient(135deg, #ff66b5 0%, #ff3388 100%);
                color: white;
                border: none;
                padding: 12px;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
            }}
            a {{ color: #ff66b5; text-decoration: none; }}
            .flash {{
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
            }}
            .danger {{
                background: #f8d7da;
                color: #721c24;
            }}
            .success {{
                background: #d4edda;
                color: #155724;
            }}
            .form-group {{
                margin-bottom: 15px;
            }}
            hr {{
                margin: 20px 0;
                border: none;
                border-top: 1px solid #ddd;
            }}
            .section-title {{
                font-weight: bold;
                color: #ff66b5;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 NS Body Scan</h1>
            <h2>Регистрация</h2>
            <form method="post">
                <div class="form-group">
                    <input type="text" name="name" placeholder="Ваше имя" required>
                </div>
                <div class="form-group">
                    <input type="text" name="username" placeholder="Логин (только латиница)" 
                           pattern="[a-zA-Z0-9_]+" 
                           title="Только латинские буквы, цифры и знак _" 
                           required>
                </div>
                <div class="form-group">
                    <input type="password" name="password" placeholder="Пароль" required>
                </div>
                <div class="form-group">
                    <input type="number" name="age" placeholder="Возраст" required>
                </div>
                <div class="form-group">
                    <input type="number" name="height" placeholder="Рост (см)" required>
                </div>
                <div class="form-group">
                    <input type="number" name="weight" placeholder="Вес (кг)" required>
                </div>
                <div class="form-group">
                    <select name="goal" required>
                        <option value="">Выберите цель</option>
                        {goal_options}
                    </select>
                </div>
                <div class="form-group">
                    <select name="activity" required>
                        <option value="">Уровень активности</option>
                        {activity_options}
                    </select>
                </div>
                <div class="form-group">
                    <select name="role">
                        <option value="user">Я клиент</option>
                        <option value="trainer">Я тренер</option>
                    </select>
                </div>
                
                <hr>
                <div class="section-title">Дополнительная информация</div>
                
                <div class="form-group">
                    <select name="body_type">
                        {body_type_options}
                    </select>
                </div>
                <div class="form-group">
                    <select name="food_budget">
                        {food_budget_options}
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" name="equipment" placeholder="Оборудование (дом/зал/гантели)">
                </div>
                <div class="form-group">
                    <input type="text" name="injuries" placeholder="Травмы/ограничения (если есть)">
                </div>
                <div class="form-group">
                    <input type="text" name="chronic_diseases" placeholder="Хронические заболевания">
                </div>
                <div class="form-group">
                    <input type="text" name="problem_zones" placeholder="Проблемные зоны (через запятую)">
                </div>
                <div class="form-group">
                    <input type="text" name="allergies" placeholder="Аллергии/непереносимости">
                </div>
                <div class="form-group">
                    <input type="text" name="preferences" placeholder="Предпочтения в еде">
                </div>
                <div class="form-group">
                    <input type="text" name="favorite_foods" placeholder="Любимые продукты">
                </div>
                <div class="form-group">
                    <input type="text" name="disliked_foods" placeholder="Нелюбимые продукты">
                </div>
                <div class="form-group">
                    <input type="number" name="meals_per_day" placeholder="Количество приёмов пищи в день" min="3" max="6" value="4">
                </div>
                <div class="form-group">
                    <select name="eating_schedule">
                        <option value="3">3 раза (завтрак, обед, ужин)</option>
                        <option value="4" selected>4 раза (+ перекус)</option>
                        <option value="5">5 раз (дробно)</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="time" name="wake_time" placeholder="Во сколько просыпаетесь?">
                </div>
                <div class="form-group">
                    <input type="time" name="sleep_time" placeholder="Во сколько ложитесь?">
                </div>
                
                <button type="submit">Зарегистрироваться</button>
            </form>
            <p style="text-align:center">Уже есть аккаунт? <a href="/login">Войти</a></p>
        </div>
    </body>
    </html>
    '''


def login_user():
    """Обработка входа с PostgreSQL"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Вход выполнен!', 'success')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash('Неверный логин или пароль', 'danger')
            return redirect(url_for('login'))
    
    # GET-запрос — показываем форму
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Вход - NS Body Scan</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: repeating-linear-gradient(45deg, #2c2c2c 0px, #2c2c2c 40px, #fff 40px, #fff 80px, #ff99cc 80px, #ff99cc 120px); min-height: 100vh; padding: 20px; }
            .container { max-width: 400px; margin: 100px auto; background: rgba(255,255,255,0.95); padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
            h1 { text-align: center; color: #ff66b5; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { width: 100%; background: linear-gradient(135deg, #ff66b5 0%, #ff3388 100%); color: white; border: none; padding: 12px; border-radius: 25px; cursor: pointer; }
            a { color: #ff66b5; text-decoration: none; }
            .flash { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .danger { background: #f8d7da; color: #721c24; }
            .success { background: #d4edda; color: #155724; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧠 NS Body Scan</h1>
            <h2>Вход</h2>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endwith %}
            <form method="post">
                <input type="text" name="username" placeholder="Логин (только латиница)" 
                       pattern="[a-zA-Z0-9_]+" 
                       title="Только латинские буквы, цифры и знак _" 
                       required>
                <input type="password" name="password" placeholder="Пароль" required>
                <button type="submit">Войти</button>
            </form>
            <p style="text-align:center">Нет аккаунта? <a href="/register">Зарегистрироваться</a></p>
        </div>
    </body>
    </html>
    '''


def logout_user():
    """Выход из системы"""
    session.pop('user_id', None)
    return redirect(url_for('login'))


def get_user_data(username):
    """Получить данные пользователя (совместимость со старым кодом)"""
    user = get_user_by_username(username)
    if user:
        return {
            'name': user.get('name', ''),
            'age': user.get('age', ''),
            'height': user.get('height', ''),
            'weight': user.get('weight', ''),
            'goal': user.get('goal', ''),
            'activity': user.get('activity', ''),
            'photos': []
        }
    return {}


def update_user_data(username, data):
    """Обновить данные пользователя (совместимость)"""
    pass


def user_exists(username):
    """Проверить существование пользователя"""
    return get_user_by_username(username) is not None