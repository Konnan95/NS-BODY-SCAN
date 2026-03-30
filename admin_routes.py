from flask import render_template, session, redirect, url_for, flash, request
from database import get_user_by_id, get_all_users, get_system_stats, update_user_role, delete_user

def admin_dashboard():
    """Дашборд администратора"""
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Проверяем, что пользователь — администратор
    if user.get('role') != 'admin':
        flash('Доступ только для администраторов', 'danger')
        return redirect(url_for('dashboard'))
    
    stats = get_system_stats()
    users = get_all_users(limit=50)
    
    return render_template('admin_dashboard.html', 
                          user=user,
                          stats=stats,
                          users=users)

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