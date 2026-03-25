"""
Декораторы для проверки подписки и лимитов
"""

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
    
    Использование:
    @require_subscription('ai_assistant')
    def some_route():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            
            user = get_user_by_id(session['user_id'])
            current_level = user.get('subscription', 'free')
            
            if SUBSCRIPTION_LEVELS.get(current_level, 0) < SUBSCRIPTION_LEVELS.get(min_level, 0):
                plan_names = {
                    'free': 'Бесплатный',
                    'ai_assistant': 'AI-помощник',
                    'ai_trainer': 'AI+тренер',
                    'human_trainer': 'Живой тренер'
                }
                flash(f'🔒 Эта функция доступна на тарифе "{plan_names.get(min_level, min_level)}". Повысьте подписку!', 'warning')
                return redirect(url_for('pricing'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_user_limit(user_id):
    """
    Получить лимиты пользователя по подписке
    Возвращает словарь с лимитами
    """
    user = get_user_by_id(user_id)
    subscription = user.get('subscription', 'free')
    
    limits = {
        'free': {
            'posture_analyses_per_month': 1,
            'has_graphs': False,
            'has_exercises_library': False,
            'has_ai_plans': False,
            'has_video_analysis': False,
            'has_workout_history': False,
            'has_meal_history': False
        },
        'ai_assistant': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True,
            'has_video_analysis': True,
            'has_workout_history': True,
            'has_meal_history': True
        },
        'ai_trainer': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True,
            'has_video_analysis': True,
            'has_workout_history': True,
            'has_meal_history': True,
            'has_voice': True,
            'has_realtime_correction': True
        },
        'human_trainer': {
            'posture_analyses_per_month': 999,
            'has_graphs': True,
            'has_exercises_library': True,
            'has_ai_plans': True,
            'has_video_analysis': True,
            'has_workout_history': True,
            'has_meal_history': True,
            'has_voice': True,
            'has_realtime_correction': True,
            'has_live_trainer': True,
            'has_reviews': True
        }
    }
    
    return limits.get(subscription, limits['free'])


def check_analytics_limit(user_id):
    """
    Проверяет, может ли пользователь смотреть графики и аналитику
    Возвращает (bool, message)
    """
    limits = get_user_limit(user_id)
    
    if not limits.get('has_graphs', False):
        return False, "📊 Графики прогресса доступны на тарифе 'AI-помощник'. Повысьте подписку!"
    
    return True, None


def check_exercises_library_limit(user_id):
    """
    Проверяет, может ли пользователь пользоваться библиотекой упражнений
    """
    limits = get_user_limit(user_id)
    
    if not limits.get('has_exercises_library', False):
        return False, "📚 Библиотека упражнений доступна на тарифе 'AI-помощник'. Повысьте подписку!"
    
    return True, None


def check_video_analysis_limit(user_id):
    """
    Проверяет, может ли пользователь анализировать технику по видео
    """
    limits = get_user_limit(user_id)
    
    if not limits.get('has_video_analysis', False):
        return False, "🎥 Анализ техники упражнений доступен на тарифе 'AI-помощник'. Повысьте подписку!"
    
    return True, None


def check_ai_plans_limit(user_id):
    """
    Проверяет, может ли пользователь генерировать AI-планы
    """
    limits = get_user_limit(user_id)
    
    if not limits.get('has_ai_plans', False):
        return False, "🤖 AI-планы тренировок и питания доступны на тарифе 'AI-помощник'. Повысьте подписку!"
    
    return True, None