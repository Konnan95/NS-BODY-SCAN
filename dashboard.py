from flask import render_template, session, redirect, url_for
from database import get_user_by_id, get_today_health, get_daily_health

def dashboard_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Получаем данные о шагах и сне
    today_health = get_today_health(session['user_id'])
    last_week = get_daily_health(session['user_id'], days=7)
    
    # Рассчитываем рекомендации
    steps_recommendation = None
    sleep_recommendation = None
    
    if today_health:
        steps = today_health.get('steps', 0)
        sleep = today_health.get('sleep_hours', 0)
        
        # Рекомендации по шагам
        if steps < 5000:
            steps_recommendation = '⚠️ Низкая активность. Постарайтесь проходить больше 5000 шагов в день.'
        elif steps < 8000:
            steps_recommendation = '📈 Хорошо! Попробуйте увеличить до 8000-10000 шагов.'
        elif steps >= 8000:
            steps_recommendation = '🎉 Отлично! Вы достигаете нормы активности.'
        
        # Рекомендации по сну
        if sleep < 6:
            sleep_recommendation = '⚠️ Вы спите недостаточно. Старайтесь спать 7-9 часов для восстановления.'
        elif sleep < 7:
            sleep_recommendation = '😴 Норма сна немного ниже рекомендуемой. Постарайтесь добавить 1 час.'
        elif sleep <= 9:
            sleep_recommendation = '💪 Отличный сон! Это помогает восстановлению мышц и гормональному балансу.'
        elif sleep > 9:
            sleep_recommendation = '😊 Вы спите достаточно, но слишком долгий сон может снижать продуктивность.'
    
    return render_template('dashboard.html', 
                          user=user,
                          today_health=today_health,
                          last_week=last_week,
                          steps_recommendation=steps_recommendation,
                          sleep_recommendation=sleep_recommendation)