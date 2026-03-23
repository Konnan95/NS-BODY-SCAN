from flask import Flask, session, render_template
from config import SECRET_KEY, UPLOAD_PATH
from auth import register_user, login_user, logout_user
from dashboard import dashboard_page
from profile import profile_page
from analyze_routes import analyze_page
from api_exercises import exercises_bp
from history_routes import history_page
from health_routes import save_health, health_page
from pricing import pricing_page, subscribe
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
app.add_url_rule('/exercises', 'exercises_page', lambda: render_template('exercises.html'))
app.add_url_rule('/test', 'test', lambda: render_template('simple_test.html'))
app.add_url_rule('/history', 'history', history_page)
app.add_url_rule('/health', 'health', health_page, methods=['GET'])
app.add_url_rule('/save_health', 'save_health', save_health, methods=['POST'])
app.add_url_rule('/pricing', 'pricing', pricing_page)
app.add_url_rule('/subscribe/<plan>', 'subscribe', subscribe)

if __name__ == '__main__':
    app.run(debug=True)