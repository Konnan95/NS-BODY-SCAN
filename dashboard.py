from flask import render_template, session, redirect, url_for, request
from database import get_user_by_id, get_today_health, get_daily_health, get_progress_data
from database import log_user_activity

def get_recommendations(user, today_health):
    """Персонализированные рекомендации по шагам и сну"""
    recommendations = []
    
    # Рекомендации по шагам
    if today_health and today_health.get('steps'):
        steps = today_health['steps']
        # Рекомендация зависит от возраста и цели
        age = user.get('age', 30)
        goal = user.get('goal', 'tone')
        
        # Базовая норма шагов
        if age < 18:
            norm_steps = 10000
        elif age < 50:
            norm_steps = 8000
        else:
            norm_steps = 6000
        
        # Корректировка по цели
        if goal in ['lose', 'weight_loss']:
            norm_steps += 2000
        elif goal == 'gain':
            norm_steps -= 1000
        
        if steps < norm_steps * 0.5:
            recommendations.append({
                'type': 'steps',
                'title': '👣 Низкая активность',
                'message': f'Сегодня {steps} шагов. Рекомендуемая норма: {norm_steps} шагов. Начните с прогулки 15-20 минут!',
                'priority': 'high'
            })
        elif steps < norm_steps:
            recommendations.append({
                'type': 'steps',
                'title': '👣 Хороший старт!',
                'message': f'Сегодня {steps} шагов. До нормы {norm_steps - steps} шагов. Добавьте вечернюю прогулку!',
                'priority': 'medium'
            })
        else:
            recommendations.append({
                'type': 'steps',
                'title': '👣 Отлично!',
                'message': f'Вы прошли {steps} шагов — это выше нормы! Так держать! 🎉',
                'priority': 'success'
            })
    else:
        recommendations.append({
            'type': 'steps',
            'title': '👣 Добавьте шаги',
            'message': 'Заполните данные о шагах на странице "Шаги/Сон", чтобы получать персонализированные рекомендации.',
            'priority': 'info'
        })
    
    # Рекомендации по сну
    if today_health and today_health.get('sleep_hours'):
        sleep = today_health['sleep_hours']
        age = user.get('age', 30)
        
        # Норма сна по возрасту
        if age < 18:
            norm_sleep = 9
        elif age < 65:
            norm_sleep = 8
        else:
            norm_sleep = 7.5
        
        if sleep < norm_sleep - 1:
            recommendations.append({
                'type': 'sleep',
                'title': '😴 Недостаток сна',
                'message': f'Вы спали {sleep} часов. Рекомендуется {norm_sleep} часов. Ложитесь спать на {norm_sleep - sleep:.0f} часов раньше!',
                'priority': 'high'
            })
        elif sleep < norm_sleep:
            recommendations.append({
                'type': 'sleep',
                'title': '😴 Мало сна',
                'message': f'Вы спали {sleep} часов. До нормы {norm_sleep - sleep:.0f} часов. Попробуйте отключить гаджеты за час до сна.',
                'priority': 'medium'
            })
        elif sleep <= norm_sleep + 1:
            recommendations.append({
                'type': 'sleep',
                'title': '😴 Отличный сон!',
                'message': f'Вы спали {sleep} часов — это идеально для восстановления!',
                'priority': 'success'
            })
        else:
            recommendations.append({
                'type': 'sleep',
                'title': '😴 Много сна',
                'message': f'Вы спали {sleep} часов. Слишком долгий сон может снижать энергию. Попробуйте спать {norm_sleep} часов.',
                'priority': 'info'
            })
    else:
        recommendations.append({
            'type': 'sleep',
            'title': '😴 Добавьте сон',
            'message': 'Заполните данные о сне на странице "Шаги/Сон", чтобы получать персонализированные рекомендации.',
            'priority': 'info'
        })
    
    return recommendations

def dashboard_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    log_user_activity(session['user_id'], 'view', '/dashboard')
    
    # Получаем выбранный период (по умолчанию 30 дней)
    period = request.args.get('period', '30')
    days_map = {'7': 7, '30': 30, '90': 90, 'all': 365}
    days = days_map.get(period, 30)
    
    # Получаем данные о шагах и сне
    today_health = get_today_health(session['user_id'])
    last_week = get_daily_health(session['user_id'], days=7)
    
    # Получаем данные для графиков с выбранным периодом
    progress = get_progress_data(session['user_id'], days=days)
    
    # Получаем персонализированные рекомендации
    recommendations = get_recommendations(user, today_health)
    
    return render_template('dashboard.html', 
                          user=user,
                          today_health=today_health,
                          last_week=last_week,
                          progress=progress,
                          selected_period=period,
                          recommendations=recommendations)