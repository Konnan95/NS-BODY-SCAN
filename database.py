import psycopg2
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    """Получить соединение с базой данных"""
    return psycopg2.connect(**DB_CONFIG)

def create_user(username, password, name, age, height, weight, goal, activity, role='user', subscription='free',
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
        INSERT INTO users (username, password, name, age, height, weight, goal, activity, role, subscription,
                           equipment, injuries, chronic_diseases, problem_zones, allergies,
                           preferences, wake_time, sleep_time,
                           body_type, meals_per_day, eating_schedule,
                           favorite_foods, disliked_foods, food_budget)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (username, hashed, name, age, height, weight, goal, activity, role, subscription,
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
        columns = [
            'id', 'username', 'password', 'name', 'age', 'height', 'weight',
            'goal', 'activity', 'role', 'created_at',
            'body_type', 'meals_per_day', 'eating_schedule',
            'favorite_foods', 'disliked_foods', 'food_budget',
            'equipment', 'injuries', 'chronic_diseases', 'problem_zones',
            'allergies', 'preferences', 'wake_time', 'sleep_time',
            'subscription'
        ]
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
        columns = [
            'id', 'username', 'password', 'name', 'age', 'height', 'weight',
            'goal', 'activity', 'role', 'created_at',
            'body_type', 'meals_per_day', 'eating_schedule',
            'favorite_foods', 'disliked_foods', 'food_budget',
            'equipment', 'injuries', 'chronic_diseases', 'problem_zones',
            'allergies', 'preferences', 'wake_time', 'sleep_time',
            'subscription'
        ]
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

def save_posture_analysis(user_id, shoulder_slope, hip_slope, head_tilt, posture_score,
                          kyphosis=None, neck_angle=None, knee_valgus=None, symmetry=None,
                          original_photo_path=None, analyzed_photo_path=None,
                          front_photo_path=None, side_photo_path=None):
    """Сохранить анализ осанки с расширенными метриками и фото"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO posture_analyses 
        (user_id, shoulder_slope, hip_slope, head_tilt, posture_score,
         kyphosis, neck_angle, knee_valgus, symmetry,
         original_photo_path, analyzed_photo_path, front_photo_path, side_photo_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id, shoulder_slope, hip_slope, head_tilt, posture_score,
        kyphosis, neck_angle, knee_valgus, symmetry,
        original_photo_path, analyzed_photo_path, front_photo_path, side_photo_path
    ))
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

def save_daily_health(user_id, steps, sleep_hours, weight=None):
    """Сохранить данные о шагах и сне"""
    from datetime import date
    conn = get_db_connection()
    cur = conn.cursor()
    today = date.today()
    
    try:
        cur.execute("""
            INSERT INTO daily_health (user_id, steps, sleep_hours, weight, date)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, date) 
            DO UPDATE SET 
                steps = EXCLUDED.steps,
                sleep_hours = EXCLUDED.sleep_hours,
                weight = EXCLUDED.weight
        """, (user_id, steps, sleep_hours, weight, today))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving daily health: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_daily_health(user_id, days=7):
    """Получить историю шагов и сна за последние N дней"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, steps, sleep_hours, weight
        FROM daily_health
        WHERE user_id = %s
        ORDER BY date DESC
        LIMIT %s
    """, (user_id, days))
    rows = cur.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            'date': row[0].strftime('%d.%m.%Y'),
            'steps': row[1],
            'sleep_hours': float(row[2]) if row[2] else 0,
            'weight': float(row[3]) if row[3] else None
        })
    return result

def get_today_health(user_id):
    """Получить данные за сегодня"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT steps, sleep_hours, weight
        FROM daily_health
        WHERE user_id = %s AND date = CURRENT_DATE
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return {
            'steps': row[0],
            'sleep_hours': float(row[1]) if row[1] else 0,
            'weight': float(row[2]) if row[2] else None
        }
    return None

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

def get_progress_data(user_id, days=30):
    """Получить данные для графиков прогресса"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Данные состава тела (жир, мышцы)
    cur.execute("""
        SELECT created_at::date, body_fat, muscle_mass
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at ASC
        LIMIT %s
    """, (user_id, days))
    body_data = cur.fetchall()
    
    # Данные активности (шаги, сон)
    cur.execute("""
        SELECT date, steps, sleep_hours
        FROM daily_health
        WHERE user_id = %s
        ORDER BY date ASC
        LIMIT %s
    """, (user_id, days))
    activity_data = cur.fetchall()
    
    conn.close()
    
    # Форматируем данные для графиков
    result = {
        'dates': [],
        'body_fat': [],
        'muscle_mass': [],
        'steps': [],
        'sleep': []
    }
    
    # Обрабатываем данные состава тела
    for row in body_data:
        date_str = row[0].strftime('%d.%m')
        result['dates'].append(date_str)
        result['body_fat'].append(round(float(row[1]), 1) if row[1] else None)
        result['muscle_mass'].append(round(float(row[2]), 1) if row[2] else None)
    
    # Обрабатываем данные активности
    for row in activity_data:
        date_str = row[0].strftime('%d.%m')
        result['steps'].append({
            'date': date_str,
            'value': row[1] or 0
        })
        result['sleep'].append({
            'date': date_str,
            'value': round(float(row[2]), 1) if row[2] else 0
        })
    
    # Сортируем шаги и сон по датам
    result['steps'] = sorted(result['steps'], key=lambda x: x['date'])
    result['sleep'] = sorted(result['sleep'], key=lambda x: x['date'])
    
    return result
def save_workout_program(user_id, program_data, days_per_week=3, version=1, is_active=True):
    """Сохранить программу тренировок"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Деактивируем старую активную программу
    cur.execute("""
        UPDATE workout_programs 
        SET is_active = FALSE 
        WHERE user_id = %s AND is_active = TRUE
    """, (user_id,))
    
    # Считаем новую версию
    cur.execute("""
        SELECT COALESCE(MAX(version), 0) + 1 
        FROM workout_programs WHERE user_id = %s
    """, (user_id,))
    new_version = cur.fetchone()[0]
    
    # Сохраняем новую
    cur.execute("""
        INSERT INTO workout_programs (user_id, program_data, days_per_week, version, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, program_data, days_per_week, new_version, is_active))
    conn.commit()
    conn.close()
    
    return new_version

def get_active_workout_program(user_id):
    """Получить активную программу тренировок"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT program_data, version, days_per_week, created_at
        FROM workout_programs
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY version DESC LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return {
            'program_data': row[0],
            'version': row[1],
            'days_per_week': row[2],
            'created_at': row[3]
        }
    return None
def log_user_activity(user_id, action, page=None, details=None):
    """Логирование действий пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO user_activity_logs (user_id, action, page, details)
            VALUES (%s, %s, %s, %s)
        """, (user_id, action, page, details))
        conn.commit()
        print(f"📝 Logged: {user_id} - {action} - {page}")
    except Exception as e:
        print(f"Log error: {e}")
    finally:
        conn.close()