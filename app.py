from flask import Flask, session, render_template, redirect, url_for, send_from_directory, jsonify, request, flash
from config import SECRET_KEY, UPLOAD_PATH
from auth import register_user, login_user, logout_user
from dashboard import dashboard_page
from profile import profile_page
from analyze_routes import analyze_page
from api_exercises import exercises_bp
from history_routes import history_page
from health_routes import save_health, health_page
from pricing import pricing_page, subscribe
from generate_workout import generate_workout_page
from generate_meal import generate_meal_page
from export_routes import export_posture_csv, export_body_composition_csv
from video_analyzer_mediapipe import video_analyzer
from decorators import require_subscription
from tts_helper import voice_trainer
from pose_comparator import pose_comparator
from trainer_routes import trainer_dashboard, trainer_client, edit_client_program, edit_client_meal, leave_review
from admin_routes import admin_dashboard, admin_users, export_admin_stats
from database import get_user_by_id, get_trainer_clients
from datetime import datetime, timedelta
import calendar
from food_api import food_api
from datetime import datetime
from database import add_food_log, get_food_logs, delete_food_log

import cv2
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_PATH
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Регистрируем Blueprint для упражнений
app.register_blueprint(exercises_bp)

# Маршруты
app.add_url_rule('/', 'home', lambda: dashboard_page() if 'user_id' in session else login_user())
app.add_url_rule('/register', 'register', register_user, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login_user, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout_user)
app.add_url_rule('/dashboard', 'dashboard', dashboard_page)
app.add_url_rule('/profile', 'profile', profile_page, methods=['GET', 'POST'])
app.add_url_rule('/analyze', 'analyze', analyze_page, methods=['GET', 'POST'])
app.add_url_rule('/history', 'history', history_page)
app.add_url_rule('/health', 'health', health_page, methods=['GET'])
app.add_url_rule('/save_health', 'save_health', save_health, methods=['POST'])
app.add_url_rule('/pricing', 'pricing', pricing_page)
app.add_url_rule('/subscribe/<plan>', 'subscribe', subscribe)

# Защищённые маршруты
@app.route('/generate_workout', methods=['GET', 'POST'])
@require_subscription('ai_assistant')
def generate_workout():
    return generate_workout_page()

@app.route('/generate_meal', methods=['GET', 'POST'])
@require_subscription('ai_assistant')
def generate_meal():
    return generate_meal_page()

@app.route('/export/posture', methods=['GET'])
@require_subscription('ai_assistant')
def export_posture():
    return export_posture_csv()

@app.route('/export/composition', methods=['GET'])
@require_subscription('ai_assistant')
def export_composition():
    return export_body_composition_csv()

# Анализ видео
@app.route('/analyze_video', methods=['POST'])
@require_subscription('ai_assistant')
def analyze_video():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    file = request.files['video']
    exercise = request.form.get('exercise', 'squat')
    
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_video_{session['user_id']}_{file.filename}")
    file.save(temp_path)
    
    try:
        result = video_analyzer.analyze_video(temp_path, exercise)
        
        # Добавляем эталонный GIF
        result['template_gif'] = video_analyzer.get_template_gif(exercise)
        
        if result.get('success'):
            from database import get_db_connection
            import json
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO exercise_analyses (user_id, exercise_type, score, feedback, angles)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                session['user_id'],
                exercise,
                result['avg_score'],
                '\n'.join(result['feedback']),
                json.dumps(result.get('angles', {}))
            ))
            conn.commit()
            conn.close()
            print(f"✅ Сохранён анализ {exercise}: {result['avg_score']} баллов")
            
            # Сравнение с эталоном (если есть фото из видео)
            comparison = None
            cap = cv2.VideoCapture(temp_path)
            ret, frame = cap.read()
            if ret:
                temp_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], f"temp_frame_{session['user_id']}.jpg")
                cv2.imwrite(temp_frame_path, frame)
                comparison = pose_comparator.compare_with_template(temp_frame_path, exercise)
                if os.path.exists(temp_frame_path):
                    os.remove(temp_frame_path)
            cap.release()
            
            if comparison:
                result['comparison_feedback'] = comparison['feedback']
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/analyze_video_page')
@require_subscription('ai_assistant')
def analyze_video_page():
    return render_template('analyze_video.html')

@app.route('/exercise_history')
@require_subscription('ai_assistant')
def exercise_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT exercise_type, score, feedback, angles, created_at
        FROM exercise_analyses
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    analyses = []
    for row in rows:
        analyses.append({
            'exercise_type': row[0],
            'score': row[1],
            'feedback': row[2],
            'angles': row[3],
            'created_at': row[4]
        })
    
    return render_template('exercise_history.html', analyses=analyses)

# Страница библиотеки упражнений
@app.route('/exercises')
@require_subscription('ai_assistant')
def exercises_page():
    from exercise_manager import exercise_manager
    exercises = exercise_manager.get_all_with_media()
    
    for ex in exercises:
        gif_name = ex.get('gifUrl', '').split('/')[-1]
        if gif_name:
            ex['media'] = {
                'type': 'gif',
                'url': f'/static/media/{gif_name}'
            }
        else:
            ex['media'] = None
    
    return render_template('exercises.html', exercises=exercises)

# История программ
@app.route('/workout_history')
def workout_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, program_data, version, days_per_week, created_at, is_active
        FROM workout_programs
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    programs = []
    for row in rows:
        programs.append({
            'id': row[0],
            'program_data': row[1],
            'version': row[2],
            'days_per_week': row[3],
            'created_at': row[4],
            'is_active': row[5]
        })
    
    return render_template('workout_history.html', programs=programs)

@app.route('/activate_workout/<int:program_id>')
def activate_workout(program_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE workout_programs 
        SET is_active = FALSE 
        WHERE user_id = %s
    """, (session['user_id'],))
    
    cur.execute("""
        UPDATE workout_programs 
        SET is_active = TRUE 
        WHERE id = %s AND user_id = %s
    """, (program_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('Программа активирована!', 'success')
    return redirect(url_for('workout_history'))

# История планов питания
@app.route('/meal_history')
def meal_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, plan_data, version, created_at, is_active
        FROM meal_plans
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    meals = []
    for row in rows:
        meals.append({
            'id': row[0],
            'plan_data': row[1],
            'version': row[2],
            'created_at': row[3],
            'is_active': row[4]
        })
    
    return render_template('meal_history.html', meals=meals)

@app.route('/activate_meal/<int:meal_id>')
def activate_meal(meal_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_db_connection
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE meal_plans 
        SET is_active = FALSE 
        WHERE user_id = %s
    """, (session['user_id'],))
    
    cur.execute("""
        UPDATE meal_plans 
        SET is_active = TRUE 
        WHERE id = %s AND user_id = %s
    """, (meal_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    flash('План питания активирован!', 'success')
    return redirect(url_for('meal_history'))

# Обработка POST на главную
@app.route('/', methods=['POST'])
def home_post():
    return redirect(url_for('login'))

@app.route('/speak', methods=['POST'])
def speak():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    text = data.get('text', '')
    if text:
        audio_url = voice_trainer.speak(text)
        if audio_url:
            return jsonify({'audio_url': audio_url})
        return jsonify({'error': 'Ошибка генерации речи'}), 500
    return jsonify({'error': 'No text'}), 400

# Раздача загруженных файлов
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Логируем для достижений
    from database import log_user_activity
    log_user_activity(session['user_id'], 'chat', '/chat')
    
    from database import get_user_by_id
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        question = request.form.get('question', '')
        if not question:
            return jsonify({'error': 'Введите вопрос'}), 400
        
        from giga_helper import ask_gigachat
        
        prompt = f"""
Ты AI-тренер по фитнесу. Отвечай кратко, дружелюбно, давай практические советы.

Данные пользователя:
- Возраст: {user.get('age', 'не указан')}
- Вес: {user.get('weight', 'не указан')} кг
- Рост: {user.get('height', 'не указан')} см
- Цель: {user.get('goal', 'не указана')}
- Ограничения/травмы: {user.get('injuries', 'нет')}

Вопрос пользователя: {question}

Ответ:
"""
        try:
            answer = ask_gigachat(prompt)
            return jsonify({'answer': answer})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return render_template('chat.html', user=user)

# Кабинет тренера
app.add_url_rule('/trainer/dashboard', 'trainer_dashboard', trainer_dashboard)
app.add_url_rule('/trainer/client/<int:client_id>', 'trainer_client', trainer_client)
app.add_url_rule('/trainer/client/<int:client_id>/edit_program', 
                 'edit_client_program', edit_client_program, methods=['GET', 'POST'])
app.add_url_rule('/trainer/client/<int:client_id>/edit_meal', 
                 'edit_client_meal', edit_client_meal, methods=['GET', 'POST'])
app.add_url_rule('/trainer/client/<int:client_id>/review/<int:trainer_id>', 
                 'leave_review', leave_review, methods=['GET', 'POST'])

# Админка
app.add_url_rule('/admin/dashboard', 'admin_dashboard', admin_dashboard)
app.add_url_rule('/admin/users', 'admin_users', admin_users, methods=['GET', 'POST'])
app.add_url_rule('/admin/export_stats', 'export_admin_stats', export_admin_stats)

# Вход для админа
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        from database import get_user_by_username
        from werkzeug.security import check_password_hash
        
        user = get_user_by_username(username)
        
        if user and user.get('role') == 'admin' and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['is_admin'] = True
            flash('Вход в админ-панель выполнен!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Неверный логин, пароль или недостаточно прав', 'danger')
    
    return render_template('admin_login.html')

# Чат тренера с клиентом
@app.route('/chat_trainer/<int:client_id>')
def chat_trainer(client_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_user_by_id, get_messages, mark_as_read
    user = get_user_by_id(session['user_id'])
    client = get_user_by_id(client_id)
    
    mark_as_read(session['user_id'], client_id)
    messages = get_messages(session['user_id'], client_id)
    
    return render_template('chat_trainer.html', user=user, client=client, messages=messages)

# Список чатов для тренера
@app.route('/chat_trainer_list')
def chat_trainer_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    clients = get_trainer_clients(session['user_id'])
    
    return render_template('chat_trainer_list.html', user=user, clients=clients)

# Чат клиента с тренером
@app.route('/chat_client/<int:trainer_id>')
def chat_client(trainer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_user_by_id, get_messages, mark_as_read
    user = get_user_by_id(session['user_id'])
    trainer = get_user_by_id(trainer_id)
    
    mark_as_read(session['user_id'], trainer_id)
    messages = get_messages(session['user_id'], trainer_id)
    
    return render_template('chat_client.html', user=user, trainer=trainer, messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    receiver_id = request.form.get('receiver_id', type=int)
    message = request.form.get('message', '')
    
    print(f"DEBUG: sender={session['user_id']}, receiver={receiver_id}, message={message}")
    
    if not message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400
    
    from database import send_message as send_msg
    send_msg(session['user_id'], receiver_id, message)
    
    return jsonify({'success': True})
# Получение сообщений
@app.route('/get_messages')
def get_messages_route():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    with_user = request.args.get('with', type=int)
    if not with_user:
        return jsonify({'success': False, 'error': 'No user specified'}), 400
    
    from database import get_messages
    messages = get_messages(session['user_id'], with_user)
    
    return jsonify({'messages': messages})



@app.route('/calendar')
def calendar_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Текущий месяц
    now = datetime.now()
    year = request.args.get('year', now.year, type=int)
    month = request.args.get('month', now.month, type=int)
    
    from database import get_calendar_workouts
    workouts = get_calendar_workouts(session['user_id'], year, month)
    
    # Календарь
    import calendar
    cal = calendar.monthcalendar(year, month)
    month_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                  'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'][month-1]
    
    return render_template('calendar.html', 
                          user=user,
                          calendar=cal,
                          year=year,
                          month=month,
                          month_name=month_name,
                          workouts=workouts,
                          now=now)
@app.route('/add_workout', methods=['POST'])
def add_workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    date = request.form.get('date')
    exercise_name = request.form.get('exercise_name')
    sets = request.form.get('sets', type=int)
    reps = request.form.get('reps', type=int)
    
    from database import add_calendar_workout
    add_calendar_workout(session['user_id'], date, exercise_name, sets, reps)
    
    flash('Тренировка добавлена!', 'success')
    return redirect(url_for('calendar_page', year=date[:4], month=date[5:7]))

@app.route('/toggle_workout/<int:workout_id>')
def toggle_workout(workout_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import toggle_workout_completed
    toggle_workout_completed(workout_id)
    
    return redirect(request.referrer or url_for('calendar_page'))

@app.route('/nutrition')
def nutrition_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    logs = get_food_logs(session['user_id'])
    
    return render_template('nutrition.html', user=user, logs=logs)

@app.route('/search_food')
def search_food():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '')
    if not query:
        return jsonify({'results': []})
    
    results = food_api.search_food(query)
    return jsonify({'results': results})

@app.route('/add_food', methods=['POST'])
def add_food():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    food_name = request.form.get('food_name')
    serving_size = request.form.get('serving_size', 100, type=float)
    calories = request.form.get('calories', 0, type=float)
    protein = request.form.get('protein', 0, type=float)
    fat = request.form.get('fat', 0, type=float)
    carbs = request.form.get('carbs', 0, type=float)
    meal_type = request.form.get('meal_type', 'lunch')
    
    add_food_log(session['user_id'], food_name, serving_size, calories, protein, fat, carbs, meal_type)
    
    flash('Продукт добавлен в дневник!', 'success')
    return redirect(url_for('nutrition_page'))

@app.route('/delete_food/<int:log_id>')
def delete_food(log_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    delete_food_log(log_id, session['user_id'])
    flash('Запись удалена!', 'success')
    return redirect(url_for('nutrition_page'))
@app.route('/test_food_api')
def test_food_api():
    from food_api import food_api
    results = food_api.search_food('курица')
    return jsonify(results)
@app.route('/trainer/client_nutrition/<int:client_id>')
def trainer_client_nutrition(client_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_user_by_id(client_id)
    logs = get_food_logs(client_id)
    
    # Суммируем за сегодня
    today_logs = [l for l in logs if l['created_at'].date() == datetime.now().date()]
    total_calories = sum(l['calories'] for l in today_logs)
    total_protein = sum(l['protein'] for l in today_logs)
    total_fat = sum(l['fat'] for l in today_logs)
    total_carbs = sum(l['carbs'] for l in today_logs)
    
    return render_template('trainer_client_nutrition.html', 
                          user=user, 
                          client=client, 
                          logs=logs,
                          total_calories=total_calories,
                          total_protein=total_protein,
                          total_fat=total_fat,
                          total_carbs=total_carbs)
app.add_url_rule('/trainer/client_nutrition/<int:client_id>', 'trainer_client_nutrition', trainer_client_nutrition)
@app.route('/test_fatsecret')
def test_fatsecret():
    from food_api import food_api
    result = food_api.search_food('bread', limit=5)
    return jsonify({'count': len(result), 'results': result, 'raw_response': 'check console'})
@app.route('/trainers')
def trainers_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import get_user_by_id, get_all_trainers
    user = get_user_by_id(session['user_id'])
    trainers = get_all_trainers()
    
    return render_template('trainers.html', user=user, trainers=trainers)
@app.route('/select_trainer/<int:trainer_id>')
def select_trainer(trainer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from database import select_trainer
    select_trainer(session['user_id'], trainer_id)
    
    flash('Тренер выбран! Теперь вы можете общаться с ним в чате.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/apply_promocode', methods=['POST'])
def apply_promocode():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    code = data.get('code', '').upper()
    
    from database import get_promocode, apply_promocode as use_promo
    promo = get_promocode(code)
    
    if not promo:
        return jsonify({'error': 'Промокод не найден'}), 404
    
    from datetime import datetime
    if promo['valid_until'] and promo['valid_until'] < datetime.now().date():
        return jsonify({'error': 'Промокод истек'}), 400
    
    if promo['used_count'] >= promo['max_uses']:
        return jsonify({'error': 'Промокод уже использован максимальное количество раз'}), 400
    
    use_promo(promo['id'])
    
    return jsonify({
        'success': True,
        'discount': promo['discount_percent'],
        'code': promo['code']
    })
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')
if __name__ == '__main__':
    app.run(debug=True)