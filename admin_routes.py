from flask import render_template, session, redirect, url_for, flash, request
from database import get_user_by_id, get_all_users, get_system_stats, update_user_role, delete_user

def admin_dashboard():
    """Дашборд администратора с расширенной статистикой"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'admin':
        flash('Доступ только для администраторов', 'danger')
        return redirect(url_for('dashboard'))
    
    from database import get_system_stats, get_admin_metrics
    stats = get_system_stats()
    metrics = get_admin_metrics()
    
    return render_template('admin_dashboard.html', 
                          user=user,
                          stats=stats,
                          metrics=metrics)

def admin_users():
    """Управление пользователями"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'admin':
        flash('Доступ только для администраторов', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        user_id = request.form.get('user_id', type=int)
        action = request.form.get('action')
        
        if action == 'make_trainer':
            update_user_role(user_id, 'trainer')
            flash('Пользователь назначен тренером', 'success')
        elif action == 'make_admin':
            update_user_role(user_id, 'admin')
            flash('Пользователь назначен администратором', 'success')
        elif action == 'make_user':
            update_user_role(user_id, 'user')
            flash('Пользователь назначен клиентом', 'success')
        elif action == 'delete':
            delete_user(user_id)
            flash('Пользователь удалён', 'success')
        
        return redirect(url_for('admin_users'))
    
    users = get_all_users(limit=100)
    
    return render_template('admin_users.html', 
                          user=user,
                          users=users)
def export_admin_stats():
    """Экспорт статистики в CSV"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = get_user_by_id(session['user_id'])
    if user.get('role') != 'admin':
        flash('Доступ только для администраторов', 'danger')
        return redirect(url_for('dashboard'))
    
    from database import get_admin_metrics
    metrics = get_admin_metrics()
    
    import csv
    import io
    from flask import send_file
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Метрика', 'Значение'])
    writer.writerow(['Всего пользователей', metrics['total_users']])
    writer.writerow(['Новых за неделю', metrics['new_week']])
    writer.writerow(['Новых за месяц', metrics['new_month']])
    writer.writerow(['Активных пользователей (7 дней)', metrics['active_users']])
    writer.writerow(['Конверсия в платные', f"{metrics['conversion']}%"])
    writer.writerow(['Средний рейтинг тренеров', metrics['avg_rating']])
    writer.writerow(['Анализов осанки', metrics['total_posture']])
    writer.writerow(['Анализов состава тела', metrics['total_composition']])
    writer.writerow(['Анализов техники', metrics['total_exercise']])
    writer.writerow(['Тренеров', metrics['total_trainers']])
    writer.writerow(['Бесплатных', metrics['subscriptions'].get('free', 0)])
    writer.writerow(['AI-помощник', metrics['subscriptions'].get('ai_assistant', 0)])
    writer.writerow(['AI+тренер', metrics['subscriptions'].get('ai_trainer', 0)])
    writer.writerow(['Живой тренер', metrics['subscriptions'].get('human_trainer', 0)])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='admin_stats.csv'
    )