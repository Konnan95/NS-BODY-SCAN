from flask import render_template, session, redirect, url_for, request
from database import get_user_by_id, get_today_health, get_daily_health, get_progress_data, log_user_activity, get_active_workout_program, get_active_meal_plan, get_previous_posture_analysis, get_previous_body_composition, get_db_connection

def dashboard_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Получаем последний анализ осанки
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT posture_score FROM posture_analyses 
        WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
    """, (session['user_id'],))
    last_score_row = cur.fetchone()
    last_score = last_score_row[0] if last_score_row else None
    
    # Получаем последний анализ состава тела
    cur.execute("""
        SELECT body_fat FROM body_composition 
        WHERE user_id = %s ORDER BY created_at DESC LIMIT 1
    """, (session['user_id'],))
    last_fat_row = cur.fetchone()
    last_body_fat = last_fat_row[0] if last_fat_row else None
    conn.close()
    
    period = request.args.get('period', '30')
    days_map = {'7': 7, '30': 30, '90': 90, 'all': 365}
    days = days_map.get(period, 30)
    
    today_health = get_today_health(session['user_id'])
    last_week = get_daily_health(session['user_id'], days=7)
    progress = get_progress_data(session['user_id'], days=days)
    workout_program = get_active_workout_program(session['user_id'])
    meal_plan = get_active_meal_plan(session['user_id'])
    prev_posture = get_previous_posture_analysis(session['user_id'])
    prev_composition = get_previous_body_composition(session['user_id'])
    
    log_user_activity(session['user_id'], 'view', '/dashboard')
    
    return render_template('dashboard.html', 
                          user=user,
                          today_health=today_health,
                          last_week=last_week,
                          progress=progress,
                          selected_period=period,
                          workout_program=workout_program,
                          meal_plan=meal_plan,
                          prev_posture=prev_posture,
                          prev_composition=prev_composition,
                          last_score=last_score,
                          last_body_fat=last_body_fat)