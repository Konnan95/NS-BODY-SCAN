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

# Раздача загруженных файлов
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True)