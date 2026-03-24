from flask import Flask, session, render_template, redirect, url_for, send_from_directory
from config import SECRET_KEY, UPLOAD_PATH
from auth import register_user, login_user, logout_user
from dashboard import dashboard_page
from profile import profile_page
from analyze_routes import analyze_page
from api_exercises import exercises_bp
from history_routes import history_page
from health_routes import save_health, health_page
from pricing import pricing_page, subscribe
from generate_workout import generate_workout_page, generate_workout_api
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

# Страница библиотеки упражнений
@app.route('/exercises')
def exercises_page():
    from exercise_manager import exercise_manager
    exercises = exercise_manager.get_all_with_media()
    
    # Добавляем поле media для каждого упражнения
    for ex in exercises:
        gif_name = ex.get('gifUrl', '').split('/')[-1]
        if gif_name:
            ex['media'] = {
                'type': 'gif',
                'url': f'/static/media/{gif_name}'
            }
        else:
            ex['media'] = None
        print(f"Упражнение: {ex.get('name')}, gif: {gif_name}")  # Отладка
    
    return render_template('exercises.html', exercises=exercises)
# Тестовый маршрут
@app.route('/test')
def test():
    return "<h1>Flask работает!</h1><p>Это прямой HTML без шаблона</p>"

# Обработка POST на главную
@app.route('/', methods=['POST'])
def home_post():
    return redirect(url_for('login'))

# Раздача загруженных файлов
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/static/media/<path:filename>')
def serve_media(filename):
    return send_from_directory('static/media', filename)
app.add_url_rule('/generate_workout', 'generate_workout', generate_workout_page, methods=['GET', 'POST'])
app.add_url_rule('/api/generate_workout', 'generate_workout_api', generate_workout_api, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)