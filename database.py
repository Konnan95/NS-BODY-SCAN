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
                favorite_foods=None, disliked_foods=None, food_budget=None,
                neck=None, chest=None, waist=None, hip=None, thigh=None,
                knee=None, ankle=None, biceps=None, forearm=None, wrist=None,
                specialization=None, experience=None, about=None, certifications=None, price_per_hour=None):
    """Создать нового пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    hashed = generate_password_hash(password)
    
    cur.execute("""
        INSERT INTO users (
            username, password, name, age, height, weight, goal, activity, role, subscription,
            equipment, injuries, chronic_diseases, problem_zones, allergies,
            preferences, wake_time, sleep_time,
            body_type, meals_per_day, eating_schedule,
            favorite_foods, disliked_foods, food_budget,
            neck, chest, waist, hip, thigh, knee, ankle, biceps, forearm, wrist,
            specialization, experience, about, certifications, price_per_hour
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        username, hashed, name, age, height, weight, goal, activity, role, subscription,
        equipment, injuries, chronic_diseases, problem_zones, allergies,
        preferences, wake_time, sleep_time,
        body_type, meals_per_day, eating_schedule,
        favorite_foods, disliked_foods, food_budget,
        neck, chest, waist, hip, thigh, knee, ankle, biceps, forearm, wrist,
        specialization, experience, about, certifications, price_per_hour
    ))
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
            'subscription', 'neck', 'chest', 'waist', 'hip', 'thigh',
            'knee', 'ankle', 'biceps', 'forearm', 'wrist',
            'specialization', 'experience', 'about', 'certifications', 'price_per_hour'
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
            'subscription', 'neck', 'chest', 'waist', 'hip', 'thigh',
            'knee', 'ankle', 'biceps', 'forearm', 'wrist',
            'specialization', 'experience', 'about', 'certifications', 'price_per_hour'
        ]
        return dict(zip(columns, user))
    return None

def update_user_profile(user_id, name, age, height, weight, goal, activity,
                        equipment=None, injuries=None, chronic_diseases=None,
                        problem_zones=None, allergies=None, preferences=None,
                        wake_time=None, sleep_time=None,
                        body_type=None, meals_per_day=None, eating_schedule=None,
                        favorite_foods=None, disliked_foods=None, food_budget=None,
                        neck=None, chest=None, waist=None, hip=None, thigh=None,
                        knee=None, ankle=None, biceps=None, forearm=None, wrist=None):
    """Обновить профиль пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET
            name=%s, age=%s, height=%s, weight=%s, goal=%s, activity=%s,
            equipment=%s, injuries=%s, chronic_diseases=%s, problem_zones=%s,
            allergies=%s, preferences=%s, wake_time=%s, sleep_time=%s,
            body_type=%s, meals_per_day=%s, eating_schedule=%s,
            favorite_foods=%s, disliked_foods=%s, food_budget=%s,
            neck=%s, chest=%s, waist=%s, hip=%s, thigh=%s, knee=%s, ankle=%s, biceps=%s, forearm=%s, wrist=%s
        WHERE id=%s
    """, (name, age, height, weight, goal, activity,
          equipment, injuries, chronic_diseases, problem_zones,
          allergies, preferences, wake_time, sleep_time,
          body_type, meals_per_day, eating_schedule,
          favorite_foods, disliked_foods, food_budget,
          neck, chest, waist, hip, thigh, knee, ankle, biceps, forearm, wrist,
          user_id))
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
    
    cur.execute("""
        SELECT created_at::date, body_fat, muscle_mass
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at ASC
        LIMIT %s
    """, (user_id, days))
    body_data = cur.fetchall()
    
    cur.execute("""
        SELECT date, steps, sleep_hours
        FROM daily_health
        WHERE user_id = %s
        ORDER BY date ASC
        LIMIT %s
    """, (user_id, days))
    activity_data = cur.fetchall()
    
    conn.close()
    
    result = {
        'dates': [],
        'body_fat': [],
        'muscle_mass': [],
        'steps': [],
        'sleep': []
    }
    
    for row in body_data:
        result['dates'].append(row[0].strftime('%d.%m'))
        result['body_fat'].append(round(float(row[1]), 1) if row[1] else None)
        result['muscle_mass'].append(round(float(row[2]), 1) if row[2] else None)
    
    for row in activity_data:
        date_str = row[0].strftime('%d.%m')
        result['steps'].append({'date': date_str, 'value': row[1] or 0})
        result['sleep'].append({'date': date_str, 'value': round(float(row[2]), 1) if row[2] else 0})
    
    result['steps'] = sorted(result['steps'], key=lambda x: x['date'])
    result['sleep'] = sorted(result['sleep'], key=lambda x: x['date'])
    
    return result

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

def save_workout_program(user_id, program_data, days_per_week=3, version=1, is_active=True):
    """Сохранить программу тренировок"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE workout_programs 
        SET is_active = FALSE 
        WHERE user_id = %s AND is_active = TRUE
    """, (user_id,))
    
    cur.execute("""
        SELECT COALESCE(MAX(version), 0) + 1 
        FROM workout_programs WHERE user_id = %s
    """, (user_id,))
    new_version = cur.fetchone()[0]
    
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

def save_meal_plan(user_id, plan_data, version=1, is_active=True):
    """Сохранить план питания"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE meal_plans 
        SET is_active = FALSE 
        WHERE user_id = %s AND is_active = TRUE
    """, (user_id,))
    
    cur.execute("""
        SELECT COALESCE(MAX(version), 0) + 1 
        FROM meal_plans WHERE user_id = %s
    """, (user_id,))
    new_version = cur.fetchone()[0]
    
    cur.execute("""
        INSERT INTO meal_plans (user_id, plan_data, version, is_active)
        VALUES (%s, %s, %s, %s)
    """, (user_id, plan_data, new_version, is_active))
    conn.commit()
    conn.close()
    
    return new_version

def get_active_meal_plan(user_id):
    """Получить активный план питания"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT plan_data, version, created_at
        FROM meal_plans
        WHERE user_id = %s AND is_active = TRUE
        ORDER BY version DESC LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return {
            'plan_data': row[0],
            'version': row[1],
            'created_at': row[2]
        }
    return None

def get_meal_plan_history(user_id, limit=10):
    """Получить историю планов питания"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT plan_data, version, created_at, is_active
        FROM meal_plans
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    
    result = []
    for row in rows:
        result.append({
            'plan_data': row[0],
            'version': row[1],
            'created_at': row[2],
            'is_active': row[3]
        })
    return result

def get_previous_posture_analysis(user_id):
    """Получить предыдущий анализ осанки (не последний)"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT shoulder_slope, hip_slope, head_tilt, posture_score, created_at
        FROM posture_analyses
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1 OFFSET 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'shoulder': row[0],
            'hip': row[1],
            'head': row[2],
            'score': row[3],
            'date': row[4]
        }
    return None

def get_previous_body_composition(user_id):
    """Получить предыдущий анализ состава тела"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT body_fat, muscle_mass, visceral_fat, created_at
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 1 OFFSET 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'body_fat': row[0],
            'muscle_mass': row[1],
            'visceral_fat': row[2],
            'date': row[3]
        }
    return None

def predict_progress(user_id):
    """Прогноз прогресса на основе истории анализов"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT created_at, body_fat
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at ASC
    """, (user_id,))
    body_fat_history = cur.fetchall()
    
    cur.execute("""
        SELECT date, weight
        FROM daily_health
        WHERE user_id = %s AND weight IS NOT NULL
        ORDER BY date ASC
    """, (user_id,))
    weight_history = cur.fetchall()
    
    conn.close()
    
    result = {}
    
    if len(body_fat_history) >= 2:
        changes = []
        for i in range(1, len(body_fat_history)):
            if body_fat_history[i-1][1] and body_fat_history[i][1]:
                diff = body_fat_history[i-1][1] - body_fat_history[i][1]
                changes.append(diff)
        if changes:
            avg_change = sum(changes) / len(changes)
            last_fat = body_fat_history[-1][1] if body_fat_history[-1][1] else 25
            predicted_fat = last_fat - (avg_change * 4)
            result['body_fat'] = round(max(10, min(45, predicted_fat)), 1)
            result['body_fat_trend'] = '⬇️ снижается' if avg_change > 0 else '⬆️ растёт'
    
    if len(weight_history) >= 2:
        changes = []
        for i in range(1, len(weight_history)):
            if weight_history[i-1][1] and weight_history[i][1]:
                diff = weight_history[i-1][1] - weight_history[i][1]
                changes.append(diff)
        if changes:
            avg_change = sum(changes) / len(changes)
            last_weight = weight_history[-1][1] if weight_history[-1][1] else 70
            predicted_weight = last_weight - (avg_change * 4)
            result['weight'] = round(max(40, min(150, predicted_weight)), 1)
    
    return result

def check_achievements(user_id):
    """Проверяет и выдаёт достижения"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT achievement_type FROM achievements WHERE user_id = %s", (user_id,))
    existing = {row[0] for row in cur.fetchall()}
    
    new_achievements = []
    
    if 'first_analysis' not in existing:
        cur.execute("SELECT COUNT(*) FROM posture_analyses WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        if count >= 1:
            cur.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (%s, 'first_analysis')", (user_id,))
            new_achievements.append('🏆 Первый анализ осанки!')
    
    if 'first_chat' not in existing:
        cur.execute("SELECT COUNT(*) FROM user_activity_logs WHERE user_id = %s AND action = 'chat'", (user_id,))
        count = cur.fetchone()[0]
        if count >= 1:
            cur.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (%s, 'first_chat')", (user_id,))
            new_achievements.append('💬 Первый диалог с AI-тренером!')
    
    if 'steps_7_days' not in existing:
        cur.execute("""
            SELECT COUNT(DISTINCT date) FROM daily_health 
            WHERE user_id = %s AND steps > 5000 AND date >= CURRENT_DATE - INTERVAL '7 days'
        """, (user_id,))
        count = cur.fetchone()[0]
        if count >= 7:
            cur.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (%s, 'steps_7_days')", (user_id,))
            new_achievements.append('👣 7 дней активности подряд!')
    
    if 'first_video_analysis' not in existing:
        cur.execute("SELECT COUNT(*) FROM exercise_analyses WHERE user_id = %s", (user_id,))
        count = cur.fetchone()[0]
        if count >= 1:
            cur.execute("INSERT INTO achievements (user_id, achievement_type) VALUES (%s, 'first_video_analysis')", (user_id,))
            new_achievements.append('🎥 Первый анализ техники!')
    
    conn.commit()
    conn.close()
    
    return new_achievements

def get_trainer_clients(trainer_id):
    """Получить список клиентов тренера"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.name, u.age, u.height, u.weight, u.goal, tc.created_at
        FROM trainer_clients tc
        JOIN users u ON tc.client_id = u.id
        WHERE tc.trainer_id = %s AND tc.is_active = TRUE
        ORDER BY tc.created_at DESC
    """, (trainer_id,))
    rows = cur.fetchall()
    conn.close()
    
    clients = []
    for row in rows:
        clients.append({
            'id': row[0],
            'username': row[1],
            'name': row[2],
            'age': row[3],
            'height': row[4],
            'weight': row[5],
            'goal': row[6],
            'since': row[7]
        })
    return clients

def get_client_progress(client_id, trainer_id=None):
    """Получить прогресс клиента для тренера"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT posture_score, shoulder_slope, hip_slope, head_tilt, created_at
        FROM posture_analyses
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (client_id,))
    posture = cur.fetchone()
    
    cur.execute("""
        SELECT body_fat, muscle_mass, visceral_fat, created_at
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at DESC LIMIT 1
    """, (client_id,))
    composition = cur.fetchone()
    
    cur.execute("""
        SELECT AVG(steps), AVG(sleep_hours)
        FROM daily_health
        WHERE user_id = %s AND date >= CURRENT_DATE - INTERVAL '7 days'
    """, (client_id,))
    health = cur.fetchone()
    
    conn.close()
    
    return {
        'last_posture': {
            'score': posture[0] if posture else None,
            'shoulder': posture[1] if posture else None,
            'hip': posture[2] if posture else None,
            'head': posture[3] if posture else None,
            'date': posture[4] if posture else None
        } if posture else None,
        'last_composition': {
            'body_fat': composition[0] if composition else None,
            'muscle_mass': composition[1] if composition else None,
            'visceral_fat': composition[2] if composition else None,
            'date': composition[3] if composition else None
        } if composition else None,
        'avg_steps': round(health[0], 0) if health and health[0] else 0,
        'avg_sleep': round(health[1], 1) if health and health[1] else 0
    }

def get_trainer_stats(trainer_id):
    """Получить статистику тренера"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT COUNT(*) FROM trainer_clients
        WHERE trainer_id = %s AND is_active = TRUE
    """, (trainer_id,))
    clients_count = cur.fetchone()[0]
    
    try:
        cur.execute("""
            SELECT COALESCE(AVG(rating), 0), COUNT(*) FROM reviews
            WHERE trainer_id = %s
        """, (trainer_id,))
        rating_row = cur.fetchone()
        avg_rating = round(rating_row[0], 1) if rating_row and rating_row[0] else 0
        reviews_count = rating_row[1] if rating_row and rating_row[1] else 0
    except Exception:
        avg_rating = 0
        reviews_count = 0
    
    cur.execute("""
        SELECT COALESCE(SUM(amount), 0) FROM trainer_earnings
        WHERE trainer_id = %s AND status = 'paid'
    """, (trainer_id,))
    earnings = cur.fetchone()[0] or 0
    
    conn.close()
    
    return {
        'clients_count': clients_count,
        'avg_rating': avg_rating,
        'reviews_count': reviews_count,
        'total_earnings': float(earnings)
    }

def send_message(sender_id, receiver_id, message):
    """Отправить сообщение"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO messages (sender_id, receiver_id, message)
        VALUES (%s, %s, %s)
    """, (sender_id, receiver_id, message))
    conn.commit()
    conn.close()

def get_messages(user1_id, user2_id, limit=50):
    """Получить переписку между двумя пользователями"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sender_id, receiver_id, message, created_at
        FROM messages
        WHERE (sender_id = %s AND receiver_id = %s)
           OR (sender_id = %s AND receiver_id = %s)
        ORDER BY created_at ASC
        LIMIT %s
    """, (user1_id, user2_id, user2_id, user1_id, limit))
    rows = cur.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        messages.append({
            'sender_id': row[0],
            'receiver_id': row[1],
            'message': row[2],
            'created_at': row[3]
        })
    return messages

def get_unread_count(user_id):
    """Получить количество непрочитанных сообщений"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM messages WHERE receiver_id = %s AND is_read = FALSE", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count

def mark_as_read(user_id, sender_id):
    """Отметить сообщения как прочитанные"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE messages SET is_read = TRUE
        WHERE receiver_id = %s AND sender_id = %s
    """, (user_id, sender_id))
    conn.commit()
    conn.close()
def save_review(client_id, trainer_id, rating, comment):
    """Сохранить отзыв"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reviews (client_id, trainer_id, rating, comment)
        VALUES (%s, %s, %s, %s)
    """, (client_id, trainer_id, rating, comment))
    conn.commit()
    conn.close()
def get_client_trainer(client_id):
    """Получить тренера клиента"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT u.id, u.username, u.name, u.specialization, u.experience, u.about
        FROM trainer_clients tc
        JOIN users u ON tc.trainer_id = u.id
        WHERE tc.client_id = %s AND tc.is_active = TRUE
    """, (client_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'username': row[1],
            'name': row[2],
            'specialization': row[3],
            'experience': row[4],
            'about': row[5]
        }
    return None
def get_all_users(limit=100):
    """Получить всех пользователей для админки"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, username, name, role, subscription, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    
    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'username': row[1],
            'name': row[2],
            'role': row[3],
            'subscription': row[4],
            'created_at': row[5]
        })
    return users

def get_system_stats():
    """Получить статистику системы"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Всего пользователей
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Тренеров
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'trainer'")
    total_trainers = cur.fetchone()[0]
    
    # Клиентов
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'user'")
    total_clients = cur.fetchone()[0]
    
    # Всего анализов осанки
    cur.execute("SELECT COUNT(*) FROM posture_analyses")
    total_posture = cur.fetchone()[0]
    
    # Всего анализов состава тела
    cur.execute("SELECT COUNT(*) FROM body_composition")
    total_composition = cur.fetchone()[0]
    
    # Всего программ тренировок
    cur.execute("SELECT COUNT(*) FROM workout_programs")
    total_workouts = cur.fetchone()[0]
    
    # Всего планов питания
    cur.execute("SELECT COUNT(*) FROM meal_plans")
    total_meals = cur.fetchone()[0]
    
    # Всего сообщений
    cur.execute("SELECT COUNT(*) FROM messages")
    total_messages = cur.fetchone()[0]
    
    # Всего отзывов
    cur.execute("SELECT COUNT(*) FROM reviews")
    total_reviews = cur.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'total_trainers': total_trainers,
        'total_clients': total_clients,
        'total_posture': total_posture,
        'total_composition': total_composition,
        'total_workouts': total_workouts,
        'total_meals': total_meals,
        'total_messages': total_messages,
        'total_reviews': total_reviews
    }

def update_user_role(user_id, new_role):
    """Изменить роль пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Удалить пользователя"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    conn.close()
def get_admin_metrics():
    """Получить расширенные метрики для админки"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Всего пользователей
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Новых за неделю
    cur.execute("""
        SELECT COUNT(*) FROM users 
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    """)
    new_week = cur.fetchone()[0]
    
    # Новых за месяц
    cur.execute("""
        SELECT COUNT(*) FROM users 
        WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    """)
    new_month = cur.fetchone()[0]
    
    # Активные пользователи (заходили за 7 дней)
    cur.execute("""
        SELECT COUNT(DISTINCT user_id) FROM user_activity_logs 
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
    """)
    active_users = cur.fetchone()[0] or 0
    
    # Распределение по подпискам
    cur.execute("""
        SELECT subscription, COUNT(*) FROM users 
        GROUP BY subscription
    """)
    subscriptions = dict(cur.fetchall())
    
    # Конверсия в платные
    total_paid = subscriptions.get('ai_assistant', 0) + subscriptions.get('ai_trainer', 0) + subscriptions.get('human_trainer', 0)
    conversion = round(total_paid / total_users * 100, 1) if total_users > 0 else 0
    
    # Всего анализов осанки
    cur.execute("SELECT COUNT(*) FROM posture_analyses")
    total_posture = cur.fetchone()[0]
    
    # Всего анализов состава тела
    cur.execute("SELECT COUNT(*) FROM body_composition")
    total_composition = cur.fetchone()[0]
    
    # Всего анализов техники
    cur.execute("SELECT COUNT(*) FROM exercise_analyses")
    total_exercise = cur.fetchone()[0]
    
    # Всего тренеров
    cur.execute("SELECT COUNT(*) FROM users WHERE role = 'trainer'")
    total_trainers = cur.fetchone()[0]
    
    # Средний рейтинг тренеров
    cur.execute("SELECT AVG(rating) FROM reviews")
    avg_rating = cur.fetchone()[0] or 0
    
    # Топ-тренеры по клиентам
    cur.execute("""
        SELECT u.name, u.username, COUNT(tc.client_id) as clients_count
        FROM trainer_clients tc
        JOIN users u ON tc.trainer_id = u.id
        GROUP BY u.id
        ORDER BY clients_count DESC
        LIMIT 5
    """)
    top_trainers = cur.fetchall()
    
    # Активность по дням (за последние 7 дней)
    cur.execute("""
        SELECT DATE(created_at) as date, COUNT(DISTINCT user_id)
        FROM user_activity_logs
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    daily_activity = cur.fetchall()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'new_week': new_week,
        'new_month': new_month,
        'active_users': active_users,
        'subscriptions': subscriptions,
        'conversion': conversion,
        'total_posture': total_posture,
        'total_composition': total_composition,
        'total_exercise': total_exercise,
        'total_trainers': total_trainers,
        'avg_rating': round(avg_rating, 1),
        'top_trainers': [{'name': t[0] or t[1], 'clients': t[2]} for t in top_trainers],
        'daily_activity': [{'date': d[0].strftime('%d.%m'), 'users': d[1]} for d in daily_activity]
    }
def get_calendar_workouts(user_id, year, month):
    """Получить тренировки на месяц"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT workout_date, exercise_name, sets, reps, completed, id
        FROM calendar_workouts
        WHERE user_id = %s 
        AND EXTRACT(YEAR FROM workout_date) = %s
        AND EXTRACT(MONTH FROM workout_date) = %s
        ORDER BY workout_date ASC
    """, (user_id, year, month))
    rows = cur.fetchall()
    conn.close()
    
    workouts = {}
    for row in rows:
        date = row[0].strftime('%Y-%m-%d')
        if date not in workouts:
            workouts[date] = []
        workouts[date].append({
            'exercise': row[1],
            'sets': row[2],
            'reps': row[3],
            'completed': row[4],
            'id': row[5]
        })
    return workouts

def add_calendar_workout(user_id, date, exercise_name, sets, reps):
    """Добавить тренировку в календарь"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO calendar_workouts (user_id, workout_date, exercise_name, sets, reps)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, date, exercise_name, sets, reps))
    conn.commit()
    conn.close()

def toggle_workout_completed(workout_id):
    """Отметить тренировку как выполненную/невыполненную"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE calendar_workouts 
        SET completed = NOT completed 
        WHERE id = %s
    """, (workout_id,))
    conn.commit()
    conn.close()