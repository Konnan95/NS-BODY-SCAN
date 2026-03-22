from flask import request, session, redirect, url_for, flash, render_template
from database import save_daily_health, get_today_health, get_user_by_id

def save_health():
    """Сохранить данные о шагах и сне"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        steps = request.form.get('steps', 0, type=int)
        sleep_hours = request.form.get('sleep_hours', 0, type=float)
        weight = request.form.get('weight', None, type=float)
        
        if steps < 0 or sleep_hours < 0 or (weight and weight < 0):
            flash('Пожалуйста, введите корректные значения', 'danger')
        else:
            save_daily_health(session['user_id'], steps, sleep_hours, weight)
            flash('Данные сохранены!', 'success')
    
    return redirect(url_for('dashboard'))

def health_page():
    """Страница с формой для ввода шагов и сна"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    today_data = get_today_health(session['user_id'])
    
    return render_template('health.html', 
                          user=user,
                          today=today_data)