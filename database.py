import psycopg2
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    """Получить соединение с базой данных"""
    return psycopg2.connect(**DB_CONFIG)

def create_user(username, password, name, age, height, weight, goal, activity, role='user',
                equipment=None, injuries=None, chronic_diseases=None,
                problem_zones=None, allergies=None, preferences=None,
                wake_time=None, sleep_time=None,
                body_type=None, meals_per_day=None, eating_schedule=None,
                favorite_foods=None, disliked_foods=None, food_budget=None):
    """Создать нового пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = generate_password_hash(password)
    cur.execute("""
        INSERT INTO users (username, password, name, age, height, weight, goal, activity, role,
                           equipment, injuries, chronic_diseases, problem_zones, allergies,
                           preferences, wake_time, sleep_time,
                           body_type, meals_per_day, eating_schedule,
                           favorite_foods, disliked_foods, food_budget)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (username, hashed, name, age, height, weight, goal, activity, role,
          equipment, injuries, chronic_diseases, problem_zones, allergies,
          preferences, wake_time, sleep_time,
          body_type, meals_per_day, eating_schedule,
          favorite_foods, disliked_foods, food_budget))
    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id

def get_user_by_username(username):
    """Получить пользователя по логину"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    conn.close()
    if user:
        columns = ['id', 'username', 'password', 'name', 'age', 'height', 'weight', 'goal', 'activity', 'role', 'created_at',
                   'equipment', 'injuries', 'chronic_diseases', 'problem_zones', 'allergies',
                   'preferences', 'wake_time', 'sleep_time',
                   'body_type', 'meals_per_day', 'eating_schedule',
                   'favorite_foods', 'disliked_foods', 'food_budget']
        return dict(zip(columns, user))
    return None

def get_user_by_id(user_id):
    """Получить пользователя по ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    conn.close()
    if user:
        columns = ['id', 'username', 'password', 'name', 'age', 'height', 'weight', 'goal', 'activity', 'role', 'created_at',
                   'equipment', 'injuries', 'chronic_diseases', 'problem_zones', 'allergies',
                   'preferences', 'wake_time', 'sleep_time',
                   'body_type', 'meals_per_day', 'eating_schedule',
                   'favorite_foods', 'disliked_foods', 'food_budget']
        return dict(zip(columns, user))
    return None

def update_user_profile(user_id, name, age, height, weight, goal, activity,
                        equipment=None, injuries=None, chronic_diseases=None,
                        problem_zones=None, allergies=None, preferences=None,
                        wake_time=None, sleep_time=None,
                        body_type=None, meals_per_day=None, eating_schedule=None,
                        favorite_foods=None, disliked_foods=None, food_budget=None):
    """Обновить профиль пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET
            name=%s, age=%s, height=%s, weight=%s, goal=%s, activity=%s,
            equipment=%s, injuries=%s, chronic_diseases=%s, problem_zones=%s,
            allergies=%s, preferences=%s, wake_time=%s, sleep_time=%s,
            body_type=%s, meals_per_day=%s, eating_schedule=%s,
            favorite_foods=%s, disliked_foods=%s, food_budget=%s
        WHERE id=%s
    """, (name, age, height, weight, goal, activity,
          equipment, injuries, chronic_diseases, problem_zones,
          allergies, preferences, wake_time, sleep_time,
          body_type, meals_per_day, eating_schedule,
          favorite_foods, disliked_foods, food_budget, user_id))
    conn.commit()
    conn.close()

def save_posture_analysis(user_id, shoulder_slope, hip_slope, head_tilt, posture_score):
    """Сохранить анализ осанки"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO posture_analyses (user_id, shoulder_slope, hip_slope, head_tilt, posture_score)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, shoulder_slope, hip_slope, head_tilt, posture_score))
    conn.commit()
    conn.close()

def save_body_composition(user_id, body_fat, muscle_mass, water, visceral_fat):
    """Сохранить анализ состава тела"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO body_composition (user_id, body_fat, muscle_mass, water, visceral_fat)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, body_fat, muscle_mass, water, visceral_fat))
    conn.commit()
    conn.close()

def save_daily_health(user_id, steps, sleep_hours, weight):
    """Сохранить данные о шагах и сне"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO daily_health (user_id, steps, sleep_hours, weight)
        VALUES (%s, %s, %s, %s)
    """, (user_id, steps, sleep_hours, weight))
    conn.commit()
    conn.close()

def get_user_history(user_id):
    """Получить историю анализов пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM posture_analyses 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (user_id,))
    posture = cur.fetchall()
    cur.execute("""
        SELECT * FROM body_composition 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (user_id,))
    composition = cur.fetchall()
    conn.close()
    return posture, composition