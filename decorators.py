from functools import wraps
from flask import session, redirect, url_for, flash
from database import get_user_by_id

# Уровни подписок
SUBSCRIPTION_LEVELS = {
    'free': 0,
    'ai_assistant': 1,
    'ai_trainer': 2,
    'human_trainer': 3
}

def require_subscription(min_level):
    """
    Декоратор для проверки уровня подписки
    min_level: 'free', 'ai_assistant', 'ai_trainer', 'human_trainer'
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = get_user_by_id(session['user_id'])
            current_level = user.get('subscription', 'free')
            
            if SUBSCRIPTION_LEVELS.get(current_level, 0) < SUBSCRIPTION_LEVELS.get(min_level, 0):
                flash(f'🔒 Эта функция доступна на тарифе "{min_level}". Повысьте подписку!', 'warning')
                return redirect(url_for('pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_user_limit(user_id):
    """Получить лимиты пользователя по подписке"""
    user = get_user_by_id(user_id)
    subscription = user.get('subscription', 'free')
    
    limits = {
        'free': {
            'posture_analyses_per_month': 1,
            'has_graphs': False,
            'has_exercises_library': False,
            'has_ai_plans': False
        },
        'ai_assistant': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True
        },
        'ai_trainer': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True,
            'has_voice': True
        },
        'human_trainer': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True,
            'has_voice': True,
            'has_live_trainer': True
        }
    }
    
    return limits.get(subscription, limits['free'])