from flask import render_template, session, redirect, url_for, flash
from database import get_user_by_id, get_db_connection, log_user_activity

def pricing_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    return render_template('pricing.html', user=user)

def subscribe(plan):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    valid_plans = ['free', 'ai_assistant', 'ai_trainer', 'human_trainer']
    if plan not in valid_plans:
        flash('Неверный тариф', 'danger')
        return redirect(url_for('pricing'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET subscription = %s WHERE id = %s", (plan, session['user_id']))
    conn.commit()
    conn.close()
    
    # Логируем смену подписки
    log_user_activity(session['user_id'], 'subscription_change', '/subscribe', f"new_plan={plan}")
    
    # Получаем обновленного пользователя для сообщения
    user = get_user_by_id(session['user_id'])
    plan_names = {
        'free': 'Бесплатный',
        'ai_assistant': 'AI-помощник',
        'ai_trainer': 'AI+тренер',
        'human_trainer': 'Живой тренер'
    }
    flash(f'Тариф изменён на {plan_names.get(plan, plan)}!', 'success')
    return redirect(url_for('dashboard'))