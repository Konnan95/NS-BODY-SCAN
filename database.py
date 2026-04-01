"""
Работа с базой данных (SQLAlchemy ORM)
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from config import DB_CONFIG
from models import Base, User, PostureAnalysis, BodyComposition, DailyHealth, WorkoutProgram, MealPlan, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta
import json

# Создаём engine
DATABASE_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
engine = create_engine(DATABASE_URL, poolclass=NullPool)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_db():
    """Получить сессию БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Получить сессию БД (для использования вне запросов)"""
    return SessionLocal()

# ========== ПОЛЬЗОВАТЕЛИ ==========

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
    db = SessionLocal()
    hashed = generate_password_hash(password)
    
    user = User(
        username=username,
        password=hashed,
        name=name,
        age=age,
        height=height,
        weight=weight,
        goal=goal,
        activity=activity,
        role=role,
        subscription=subscription,
        neck=neck,
        chest=chest,
        waist=waist,
        hip=hip,
        thigh=thigh,
        knee=knee,
        ankle=ankle,
        biceps=biceps,
        forearm=forearm,
        wrist=wrist,
        specialization=specialization,
        experience=experience,
        about=about,
        certifications=certifications,
        price_per_hour=price_per_hour
    )
    
    db.add(user)
    db.commit()
    user_id = user.id
    db.close()
    return user_id

def get_user_by_username(username):
    """Получить пользователя по логину"""
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'name': user.name,
            'age': user.age,
            'height': user.height,
            'weight': user.weight,
            'goal': user.goal,
            'activity': user.activity,
            'role': user.role,
            'created_at': user.created_at,
            'subscription': user.subscription,
            'neck': user.neck,
            'chest': user.chest,
            'waist': user.waist,
            'hip': user.hip,
            'thigh': user.thigh,
            'knee': user.knee,
            'ankle': user.ankle,
            'biceps': user.biceps,
            'forearm': user.forearm,
            'wrist': user.wrist,
            'specialization': user.specialization,
            'experience': user.experience,
            'about': user.about,
            'certifications': user.certifications,
            'price_per_hour': user.price_per_hour,
            'equipment': None,
            'injuries': None,
            'chronic_diseases': None,
            'problem_zones': None,
            'allergies': None,
            'preferences': None,
            'wake_time': None,
            'sleep_time': None,
            'body_type': None,
            'meals_per_day': None,
            'eating_schedule': None,
            'favorite_foods': None,
            'disliked_foods': None,
            'food_budget': None
        }
    return None

def get_user_by_id(user_id):
    """Получить пользователя по ID"""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    db.close()
    if user:
        return {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'name': user.name,
            'age': user.age,
            'height': user.height,
            'weight': user.weight,
            'goal': user.goal,
            'activity': user.activity,
            'role': user.role,
            'created_at': user.created_at,
            'subscription': user.subscription,
            'neck': user.neck,
            'chest': user.chest,
            'waist': user.waist,
            'hip': user.hip,
            'thigh': user.thigh,
            'knee': user.knee,
            'ankle': user.ankle,
            'biceps': user.biceps,
            'forearm': user.forearm,
            'wrist': user.wrist,
            'specialization': user.specialization,
            'experience': user.experience,
            'about': user.about,
            'certifications': user.certifications,
            'price_per_hour': user.price_per_hour,
            'equipment': None,
            'injuries': None,
            'chronic_diseases': None,
            'problem_zones': None,
            'allergies': None,
            'preferences': None,
            'wake_time': None,
            'sleep_time': None,
            'body_type': None,
            'meals_per_day': None,
            'eating_schedule': None,
            'favorite_foods': None,
            'disliked_foods': None,
            'food_budget': None
        }
    return None

def update_user_profile(user_id, name, age, height, weight, goal, activity, **kwargs):
    """Обновить профиль пользователя"""
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.name = name
        user.age = age
        user.height = height
        user.weight = weight
        user.goal = goal
        user.activity = activity
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        db.commit()
    db.close()

# ========== АНАЛИЗЫ ОСАНКИ ==========

def save_posture_analysis(user_id, shoulder_slope, hip_slope, head_tilt, posture_score,
                          kyphosis=None, neck_angle=None, knee_valgus=None, symmetry=None,
                          original_photo_path=None, analyzed_photo_path=None,
                          front_photo_path=None, side_photo_path=None):
    """Сохранить анализ осанки"""
    db = SessionLocal()
    analysis = PostureAnalysis(
        user_id=user_id,
        shoulder_slope=shoulder_slope,
        hip_slope=hip_slope,
        head_tilt=head_tilt,
        posture_score=posture_score,
        kyphosis=kyphosis,
        neck_angle=neck_angle,
        knee_valgus=knee_valgus,
        symmetry=symmetry,
        original_photo_path=original_photo_path,
        analyzed_photo_path=analyzed_photo_path,
        front_photo_path=front_photo_path,
        side_photo_path=side_photo_path
    )
    db.add(analysis)
    db.commit()
    db.close()

# ========== АНАЛИЗЫ СОСТАВА ТЕЛА ==========

def save_body_composition(user_id, body_fat, muscle_mass, water, visceral_fat):
    """Сохранить анализ состава тела"""
    db = SessionLocal()
    composition = BodyComposition(
        user_id=user_id,
        body_fat=body_fat,
        muscle_mass=muscle_mass,
        water=water,
        visceral_fat=visceral_fat
    )
    db.add(composition)
    db.commit()
    db.close()

# ========== ШАГИ И СОН ==========

def save_daily_health(user_id, steps, sleep_hours, weight=None):
    """Сохранить данные о шагах и сне"""
    db = SessionLocal()
    today = date.today()
    
    existing = db.query(DailyHealth).filter(
        DailyHealth.user_id == user_id,
        DailyHealth.date == today
    ).first()
    
    if existing:
        existing.steps = steps
        existing.sleep_hours = sleep_hours
        if weight:
            existing.weight = weight
    else:
        health = DailyHealth(
            user_id=user_id,
            date=today,
            steps=steps,
            sleep_hours=sleep_hours,
            weight=weight
        )
        db.add(health)
    
    db.commit()
    db.close()

def get_daily_health(user_id, days=7):
    """Получить историю шагов и сна за последние N дней"""
    db = SessionLocal()
    records = db.query(DailyHealth).filter(
        DailyHealth.user_id == user_id
    ).order_by(DailyHealth.date.desc()).limit(days).all()
    db.close()
    
    result = []
    for r in records:
        result.append({
            'date': r.date.strftime('%d.%m.%Y'),
            'steps': r.steps,
            'sleep_hours': float(r.sleep_hours) if r.sleep_hours else 0,
            'weight': float(r.weight) if r.weight else None
        })
    return result

def get_today_health(user_id):
    """Получить данные за сегодня"""
    db = SessionLocal()
    today = date.today()
    record = db.query(DailyHealth).filter(
        DailyHealth.user_id == user_id,
        DailyHealth.date == today
    ).first()
    db.close()
    
    if record:
        return {
            'steps': record.steps,
            'sleep_hours': float(record.sleep_hours) if record.sleep_hours else 0,
            'weight': float(record.weight) if record.weight else None
        }
    return None

# ========== ПРОГРАММЫ ТРЕНИРОВОК ==========

def save_workout_program(user_id, program_data, days_per_week=3, is_active=True):
    """Сохранить программу тренировок"""
    db = SessionLocal()
    
    db.query(WorkoutProgram).filter(
        WorkoutProgram.user_id == user_id,
        WorkoutProgram.is_active == True
    ).update({"is_active": False})
    
    max_version = db.query(WorkoutProgram.version).filter(
        WorkoutProgram.user_id == user_id
    ).order_by(WorkoutProgram.version.desc()).first()
    new_version = (max_version[0] + 1) if max_version else 1
    
    program = WorkoutProgram(
        user_id=user_id,
        program_data=program_data,
        days_per_week=days_per_week,
        version=new_version,
        is_active=is_active
    )
    db.add(program)
    db.commit()
    db.close()

def get_active_workout_program(user_id):
    """Получить активную программу тренировок"""
    db = SessionLocal()
    program = db.query(WorkoutProgram).filter(
        WorkoutProgram.user_id == user_id,
        WorkoutProgram.is_active == True
    ).order_by(WorkoutProgram.version.desc()).first()
    db.close()
    
    if program:
        return {
            'program_data': program.program_data,
            'version': program.version,
            'days_per_week': program.days_per_week,
            'created_at': program.created_at
        }
    return None

# ========== ПЛАНЫ ПИТАНИЯ ==========

def save_meal_plan(user_id, plan_data, is_active=True):
    """Сохранить план питания"""
    db = SessionLocal()
    
    db.query(MealPlan).filter(
        MealPlan.user_id == user_id,
        MealPlan.is_active == True
    ).update({"is_active": False})
    
    max_version = db.query(MealPlan.version).filter(
        MealPlan.user_id == user_id
    ).order_by(MealPlan.version.desc()).first()
    new_version = (max_version[0] + 1) if max_version else 1
    
    plan = MealPlan(
        user_id=user_id,
        plan_data=plan_data,
        version=new_version,
        is_active=is_active
    )
    db.add(plan)
    db.commit()
    db.close()

def get_active_meal_plan(user_id):
    """Получить активный план питания"""
    db = SessionLocal()
    plan = db.query(MealPlan).filter(
        MealPlan.user_id == user_id,
        MealPlan.is_active == True
    ).order_by(MealPlan.version.desc()).first()
    db.close()
    
    if plan:
        return {
            'plan_data': plan.plan_data,
            'version': plan.version,
            'created_at': plan.created_at
        }
    return None

# ========== СООБЩЕНИЯ ==========

def send_message(sender_id, receiver_id, message):
    """Отправить сообщение"""
    db = SessionLocal()
    msg = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message
    )
    db.add(msg)
    db.commit()
    db.close()

def get_messages(user1_id, user2_id, limit=50):
    """Получить переписку между двумя пользователями"""
    db = SessionLocal()
    messages = db.query(Message).filter(
        ((Message.sender_id == user1_id) & (Message.receiver_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.receiver_id == user1_id))
    ).order_by(Message.created_at.asc()).limit(limit).all()
    db.close()
    
    result = []
    for m in messages:
        result.append({
            'sender_id': m.sender_id,
            'receiver_id': m.receiver_id,
            'message': m.message,
            'created_at': m.created_at
        })
    return result

def get_unread_count(user_id):
    """Получить количество непрочитанных сообщений"""
    db = SessionLocal()
    count = db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.is_read == False
    ).count()
    db.close()
    return count

def mark_as_read(user_id, sender_id):
    """Отметить сообщения как прочитанные"""
    db = SessionLocal()
    db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.sender_id == sender_id
    ).update({"is_read": True})
    db.commit()
    db.close()

# ========== ПРЕДЫДУЩИЕ АНАЛИЗЫ ==========

def get_previous_posture_analysis(user_id):
    """Получить предыдущий анализ осанки (не последний)"""
    db = SessionLocal()
    analysis = db.query(PostureAnalysis).filter(
        PostureAnalysis.user_id == user_id
    ).order_by(PostureAnalysis.created_at.desc()).offset(1).first()
    db.close()
    
    if analysis:
        return {
            'shoulder': analysis.shoulder_slope,
            'hip': analysis.hip_slope,
            'head': analysis.head_tilt,
            'score': analysis.posture_score,
            'date': analysis.created_at
        }
    return None

def get_previous_body_composition(user_id):
    """Получить предыдущий анализ состава тела"""
    db = SessionLocal()
    composition = db.query(BodyComposition).filter(
        BodyComposition.user_id == user_id
    ).order_by(BodyComposition.created_at.desc()).offset(1).first()
    db.close()
    
    if composition:
        return {
            'body_fat': composition.body_fat,
            'muscle_mass': composition.muscle_mass,
            'visceral_fat': composition.visceral_fat,
            'date': composition.created_at
        }
    return None

# ========== ПРОГНОЗ ПРОГРЕССА ==========

def predict_progress(user_id):
    """Прогноз прогресса на основе истории анализов"""
    db = SessionLocal()
    
    body_fat_history = db.query(BodyComposition).filter(
        BodyComposition.user_id == user_id
    ).order_by(BodyComposition.created_at.asc()).all()
    
    weight_history = db.query(DailyHealth).filter(
        DailyHealth.user_id == user_id,
        DailyHealth.weight.isnot(None)
    ).order_by(DailyHealth.date.asc()).all()
    db.close()
    
    result = {}
    
    if len(body_fat_history) >= 2:
        changes = []
        for i in range(1, len(body_fat_history)):
            if body_fat_history[i-1].body_fat and body_fat_history[i].body_fat:
                diff = body_fat_history[i-1].body_fat - body_fat_history[i].body_fat
                changes.append(diff)
        if changes:
            avg_change = sum(changes) / len(changes)
            last_fat = body_fat_history[-1].body_fat if body_fat_history[-1].body_fat else 25
            predicted_fat = last_fat - (avg_change * 4)
            result['body_fat'] = round(max(10, min(45, predicted_fat)), 1)
            result['body_fat_trend'] = '⬇️ снижается' if avg_change > 0 else '⬆️ растёт'
    
    if len(weight_history) >= 2:
        changes = []
        for i in range(1, len(weight_history)):
            if weight_history[i-1].weight and weight_history[i].weight:
                diff = weight_history[i-1].weight - weight_history[i].weight
                changes.append(diff)
        if changes:
            avg_change = sum(changes) / len(changes)
            last_weight = weight_history[-1].weight if weight_history[-1].weight else 70
            predicted_weight = last_weight - (avg_change * 4)
            result['weight'] = round(max(40, min(150, predicted_weight)), 1)
    
    return result

# ========== ДОСТИЖЕНИЯ ==========

def check_achievements(user_id):
    """Проверяет и выдаёт достижения"""
    return []

# ========== КЛИЕНТЫ ТРЕНЕРА ==========

def get_trainer_clients(trainer_id):
    """Получить список клиентов тренера"""
    db = SessionLocal()
    clients = db.query(User).filter(User.role == 'user').limit(20).all()
    db.close()
    
    result = []
    for c in clients:
        result.append({
            'id': c.id,
            'username': c.username,
            'name': c.name,
            'age': c.age,
            'height': c.height,
            'weight': c.weight,
            'goal': c.goal,
            'since': c.created_at
        })
    return result

def get_client_progress(client_id, trainer_id=None):
    """Получить прогресс клиента для тренера"""
    db = SessionLocal()
    
    posture = db.query(PostureAnalysis).filter(
        PostureAnalysis.user_id == client_id
    ).order_by(PostureAnalysis.created_at.desc()).first()
    
    composition = db.query(BodyComposition).filter(
        BodyComposition.user_id == client_id
    ).order_by(BodyComposition.created_at.desc()).first()
    
    week_ago = date.today() - timedelta(days=7)
    health_stats = db.query(DailyHealth).filter(
        DailyHealth.user_id == client_id,
        DailyHealth.date >= week_ago
    ).all()
    db.close()
    
    avg_steps = 0
    avg_sleep = 0
    if health_stats:
        steps_sum = sum(h.steps for h in health_stats if h.steps)
        sleep_sum = sum(h.sleep_hours for h in health_stats if h.sleep_hours)
        avg_steps = steps_sum / len(health_stats) if health_stats else 0
        avg_sleep = sleep_sum / len(health_stats) if health_stats else 0
    
    return {
        'last_posture': {
            'score': posture.posture_score if posture else None,
            'shoulder': posture.shoulder_slope if posture else None,
            'hip': posture.hip_slope if posture else None,
            'head': posture.head_tilt if posture else None,
            'date': posture.created_at if posture else None
        } if posture else None,
        'last_composition': {
            'body_fat': composition.body_fat if composition else None,
            'muscle_mass': composition.muscle_mass if composition else None,
            'visceral_fat': composition.visceral_fat if composition else None,
            'date': composition.created_at if composition else None
        } if composition else None,
        'avg_steps': round(avg_steps, 0),
        'avg_sleep': round(avg_sleep, 1)
    }

def get_trainer_stats(trainer_id):
    """Получить статистику тренера"""
    db = SessionLocal()
    clients_count = db.query(User).filter(User.role == 'user').count()
    db.close()
    
    return {
        'clients_count': clients_count,
        'avg_rating': 0,
        'reviews_count': 0,
        'total_earnings': 0
    }

def get_client_trainer(client_id):
    """Получить тренера клиента"""
    return None

def get_all_trainers():
    """Получить всех тренеров для маркетплейса"""
    db = SessionLocal()
    trainers = db.query(User).filter(User.role == 'trainer').all()
    db.close()
    
    result = []
    for t in trainers:
        result.append({
            'id': t.id,
            'username': t.username,
            'name': t.name,
            'specialization': t.specialization,
            'experience': t.experience,
            'about': t.about,
            'price_per_hour': t.price_per_hour,
            'avg_rating': 0,
            'reviews_count': 0
        })
    return result

def select_trainer(client_id, trainer_id):
    """Выбрать тренера"""
    pass

def get_system_stats():
    """Получить статистику системы для админки"""
    db = SessionLocal()
    
    total_users = db.query(User).count()
    total_trainers = db.query(User).filter(User.role == 'trainer').count()
    total_clients = db.query(User).filter(User.role == 'user').count()
    total_posture = db.query(PostureAnalysis).count()
    total_composition = db.query(BodyComposition).count()
    total_workouts = db.query(WorkoutProgram).count()
    total_meals = db.query(MealPlan).count()
    total_messages = db.query(Message).count()
    
    db.close()
    
    return {
        'total_users': total_users,
        'total_trainers': total_trainers,
        'total_clients': total_clients,
        'total_posture': total_posture,
        'total_composition': total_composition,
        'total_workouts': total_workouts,
        'total_meals': total_meals,
        'total_messages': total_messages,
        'total_reviews': 0
    }

def get_admin_metrics():
    """Получить расширенные метрики для админки"""
    db = SessionLocal()
    
    total_users = db.query(User).count()
    week_ago = date.today() - timedelta(days=7)
    new_week = db.query(User).filter(User.created_at >= week_ago).count()
    
    month_ago = date.today() - timedelta(days=30)
    new_month = db.query(User).filter(User.created_at >= month_ago).count()
    
    active_users = db.query(PostureAnalysis.user_id).distinct().count()
    
    subscriptions = {
        'free': db.query(User).filter(User.subscription == 'free').count(),
        'ai_assistant': db.query(User).filter(User.subscription == 'ai_assistant').count(),
        'ai_trainer': db.query(User).filter(User.subscription == 'ai_trainer').count(),
        'human_trainer': db.query(User).filter(User.subscription == 'human_trainer').count()
    }
    
    total_paid = subscriptions['ai_assistant'] + subscriptions['ai_trainer'] + subscriptions['human_trainer']
    conversion = round(total_paid / total_users * 100, 1) if total_users > 0 else 0
    
    total_posture = db.query(PostureAnalysis).count()
    total_composition = db.query(BodyComposition).count()
    total_trainers = db.query(User).filter(User.role == 'trainer').count()
    
    daily_activity = []
    for i in range(7, 0, -1):
        day = date.today() - timedelta(days=i)
        count = db.query(PostureAnalysis).filter(PostureAnalysis.created_at >= day).count()
        daily_activity.append({
            'date': day.strftime('%d.%m'),
            'users': count
        })
    
    db.close()
    
    return {
        'total_users': total_users,
        'new_week': new_week,
        'new_month': new_month,
        'active_users': active_users,
        'subscriptions': subscriptions,
        'conversion': conversion,
        'total_posture': total_posture,
        'total_composition': total_composition,
        'total_exercise': 0,
        'total_trainers': total_trainers,
        'avg_rating': 0,
        'top_trainers': [],
        'daily_activity': daily_activity
    }

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

def get_db_connection():
    """Для совместимости со старым кодом"""
    return engine.connect()

def get_user_history(user_id):
    """Получить историю анализов пользователя"""
    db = SessionLocal()
    posture = db.query(PostureAnalysis).filter(
        PostureAnalysis.user_id == user_id
    ).order_by(PostureAnalysis.created_at.desc()).limit(10).all()
    
    composition = db.query(BodyComposition).filter(
        BodyComposition.user_id == user_id
    ).order_by(BodyComposition.created_at.desc()).limit(10).all()
    db.close()
    
    posture_list = [(p.id, p.user_id, p.shoulder_slope, p.hip_slope, p.head_tilt, 
                     p.posture_score, p.created_at, p.kyphosis, p.neck_angle, 
                     p.knee_valgus, p.symmetry, p.original_photo_path, p.analyzed_photo_path,
                     p.front_photo_path, p.side_photo_path) for p in posture]
    
    composition_list = [(c.id, c.user_id, c.body_fat, c.muscle_mass, c.water, 
                         c.visceral_fat, c.created_at) for c in composition]
    
    return posture_list, composition_list

def get_progress_data(user_id, days=30):
    """Получить данные для графиков прогресса"""
    db = SessionLocal()
    
    body_data = db.query(BodyComposition).filter(
        BodyComposition.user_id == user_id
    ).order_by(BodyComposition.created_at.asc()).limit(days).all()
    
    health_data = db.query(DailyHealth).filter(
        DailyHealth.user_id == user_id
    ).order_by(DailyHealth.date.asc()).limit(days).all()
    db.close()
    
    result = {
        'dates': [],
        'body_fat': [],
        'muscle_mass': [],
        'steps': [],
        'sleep': []
    }
    
    for b in body_data:
        result['dates'].append(b.created_at.strftime('%d.%m'))
        result['body_fat'].append(round(float(b.body_fat), 1) if b.body_fat else None)
        result['muscle_mass'].append(round(float(b.muscle_mass), 1) if b.muscle_mass else None)
    
    for h in health_data:
        date_str = h.date.strftime('%d.%m')
        result['steps'].append({'date': date_str, 'value': h.steps or 0})
        result['sleep'].append({'date': date_str, 'value': round(float(h.sleep_hours), 1) if h.sleep_hours else 0})
    
    result['steps'] = sorted(result['steps'], key=lambda x: x['date'])
    result['sleep'] = sorted(result['sleep'], key=lambda x: x['date'])
    
    return result

# ========== КАЛЕНДАРЬ ТРЕНИРОВОК ==========

def add_calendar_workout(user_id, date, exercise_name, sets, reps):
    """Добавить тренировку в календарь"""
    db = SessionLocal()
    
    # Создаём таблицу, если её нет
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS calendar_workouts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            workout_date DATE NOT NULL,
            exercise_name VARCHAR(200),
            sets INTEGER,
            reps INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    db.commit()
    
    # Вставляем запись
    db.execute(text("""
        INSERT INTO calendar_workouts (user_id, workout_date, exercise_name, sets, reps)
        VALUES (:user_id, :date, :exercise_name, :sets, :reps)
    """), {"user_id": user_id, "date": date, "exercise_name": exercise_name, "sets": sets, "reps": reps})
    db.commit()
    db.close()

def get_calendar_workouts(user_id, year, month):
    """Получить тренировки на месяц"""
    db = SessionLocal()
    
    # Создаём таблицу, если её нет
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS calendar_workouts (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            workout_date DATE NOT NULL,
            exercise_name VARCHAR(200),
            sets INTEGER,
            reps INTEGER,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    db.commit()
    
    # Получаем тренировки
    result = db.execute(text("""
        SELECT workout_date, exercise_name, sets, reps, completed, id
        FROM calendar_workouts
        WHERE user_id = :user_id 
        AND EXTRACT(YEAR FROM workout_date) = :year
        AND EXTRACT(MONTH FROM workout_date) = :month
        ORDER BY workout_date ASC
    """), {"user_id": user_id, "year": year, "month": month})
    
    rows = result.fetchall()
    db.close()
    
    workouts = {}
    for row in rows:
        date_str = row[0].strftime('%Y-%m-%d')
        if date_str not in workouts:
            workouts[date_str] = []
        workouts[date_str].append({
            'exercise': row[1],
            'sets': row[2],
            'reps': row[3],
            'completed': row[4],
            'id': row[5]
        })
    return workouts

def toggle_workout_completed(workout_id):
    """Отметить тренировку как выполненную/невыполненную"""
    db = SessionLocal()
    db.execute(text("""
        UPDATE calendar_workouts 
        SET completed = NOT completed 
        WHERE id = :workout_id
    """), {"workout_id": workout_id})
    db.commit()
    db.close()

# ========== ДНЕВНИК ПИТАНИЯ ==========

def get_food_logs(user_id, date=None):
    """Получить записи дневника питания за день"""
    db = SessionLocal()
    
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS food_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            food_name VARCHAR(200),
            serving_size DECIMAL(10,2),
            calories DECIMAL(10,2),
            protein DECIMAL(10,2),
            fat DECIMAL(10,2),
            carbs DECIMAL(10,2),
            meal_type VARCHAR(20),
            logged_date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    db.commit()
    
    if date:
        result = db.execute(text("""
            SELECT id, food_name, serving_size, calories, protein, fat, carbs, meal_type, created_at
            FROM food_logs
            WHERE user_id = :user_id AND logged_date = :date
            ORDER BY created_at ASC
        """), {"user_id": user_id, "date": date})
    else:
        result = db.execute(text("""
            SELECT id, food_name, serving_size, calories, protein, fat, carbs, meal_type, created_at
            FROM food_logs
            WHERE user_id = :user_id AND logged_date = CURRENT_DATE
            ORDER BY created_at ASC
        """), {"user_id": user_id})
    
    rows = result.fetchall()
    db.close()
    
    logs = []
    for row in rows:
        logs.append({
            'id': row[0],
            'food_name': row[1],
            'serving_size': row[2],
            'calories': row[3],
            'protein': row[4],
            'fat': row[5],
            'carbs': row[6],
            'meal_type': row[7],
            'created_at': row[8]
        })
    return logs

def add_food_log(user_id, food_name, serving_size, calories, protein, fat, carbs, meal_type):
    """Добавить запись в дневник питания"""
    db = SessionLocal()
    db.execute(text("""
        INSERT INTO food_logs (user_id, food_name, serving_size, calories, protein, fat, carbs, meal_type)
        VALUES (:user_id, :food_name, :serving_size, :calories, :protein, :fat, :carbs, :meal_type)
    """), {
        "user_id": user_id,
        "food_name": food_name,
        "serving_size": serving_size,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "meal_type": meal_type
    })
    db.commit()
    db.close()

def delete_food_log(log_id, user_id):
    """Удалить запись из дневника питания"""
    db = SessionLocal()
    db.execute(text("DELETE FROM food_logs WHERE id = :log_id AND user_id = :user_id"), 
               {"log_id": log_id, "user_id": user_id})
    db.commit()
    db.close()

# ========== АДМИНКА ==========

def get_all_users(limit=100):
    """Получить всех пользователей для админки"""
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    db.close()
    
    result = []
    for u in users:
        result.append({
            'id': u.id,
            'username': u.username,
            'name': u.name,
            'role': u.role,
            'subscription': u.subscription,
            'created_at': u.created_at
        })
    return result

def update_user_role(user_id, new_role):
    """Изменить роль пользователя"""
    db = SessionLocal()
    db.query(User).filter(User.id == user_id).update({"role": new_role})
    db.commit()
    db.close()

def delete_user(user_id):
    """Удалить пользователя"""
    db = SessionLocal()
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
    db.close()

def get_workout_program_history(user_id, limit=10):
    """Получить историю программ тренировок"""
    db = SessionLocal()
    programs = db.query(WorkoutProgram).filter(
        WorkoutProgram.user_id == user_id
    ).order_by(WorkoutProgram.created_at.desc()).limit(limit).all()
    db.close()
    
    result = []
    for p in programs:
        result.append({
            'id': p.id,
            'program_data': p.program_data,
            'version': p.version,
            'days_per_week': p.days_per_week,
            'created_at': p.created_at,
            'is_active': p.is_active
        })
    return result

def get_meal_plan_history(user_id, limit=10):
    """Получить историю планов питания"""
    db = SessionLocal()
    plans = db.query(MealPlan).filter(
        MealPlan.user_id == user_id
    ).order_by(MealPlan.created_at.desc()).limit(limit).all()
    db.close()
    
    result = []
    for p in plans:
        result.append({
            'id': p.id,
            'plan_data': p.plan_data,
            'version': p.version,
            'created_at': p.created_at,
            'is_active': p.is_active
        })
    return result

def log_user_activity(user_id, action, page=None, details=None):
    """Логирование действий пользователя"""
    print(f"📝 Logged: {user_id} - {action} - {page}")