from flask import render_template, session, redirect, url_for, request
from database import get_user_by_id, get_today_health, get_daily_health, get_progress_data, log_user_activity, get_active_workout_program
from database import get_active_meal_plan

def dashboard_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Принудительно получаем свежие данные из БД
    user = get_user_by_id(session['user_id'])
    
    # Проверяем в консоли
    print(f"=== USER DATA ===")
    print(f"ID: {user['id']}")
    print(f"Username: {user['username']}")
    print(f"Subscription: {user.get('subscription', 'free')}")
    print(f"=================")
    
    period = request.args.get('period', '30')
    days_map = {'7': 7, '30': 30, '90': 90, 'all': 365}
    days = days_map.get(period, 30)
    
    today_health = get_today_health(session['user_id'])
    last_week = get_daily_health(session['user_id'], days=7)
    progress = get_progress_data(session['user_id'], days=days)
    
    # Получаем активную программу тренировок
    workout_program = get_active_workout_program(session['user_id'])
    # Получаем активный план питания
    meal_plan = get_active_meal_plan(session['user_id'])
    
    log_user_activity(session['user_id'], 'view', '/dashboard')
    
    return render_template('dashboard.html', 
                          user=user,
                          today_health=today_health,
                          last_week=last_week,
                          progress=progress,
                          selected_period=period,
                          workout_program=workout_program,
                          meal_plan=meal_plan)