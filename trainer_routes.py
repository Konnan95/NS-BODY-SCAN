from flask import render_template, session, redirect, url_for, flash, request
from database import get_user_by_id, get_trainer_clients, get_client_progress, get_trainer_stats, get_active_workout_program, save_workout_program

def trainer_dashboard():
    """Дашборд тренера"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Проверяем, что пользователь — тренер
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    clients = get_trainer_clients(session['user_id'])
    stats = get_trainer_stats(session['user_id'])
    
    return render_template('trainer_dashboard.html', 
                          user=user,
                          clients=clients,
                          stats=stats)

def trainer_client(client_id):
    """Просмотр клиента тренером"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_user_by_id(client_id)
    progress = get_client_progress(client_id, session['user_id'])
    
    return render_template('trainer_client.html', 
                          user=user,
                          client=client,
                          progress=progress)

def edit_client_program(client_id):
    """Редактирование программы тренировок клиента"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_user_by_id(client_id)
    
    if request.method == 'POST':
        program_data = request.form.get('program_data', '')
        
        # Сохраняем программу
        save_workout_program(
            user_id=client_id,
            program_data=program_data,
            days_per_week=3,
            is_active=True
        )
        
        flash('Программа тренировок обновлена!', 'success')
        return redirect(url_for('trainer_client', client_id=client_id))
    
    # Получаем текущую активную программу
    current_program = get_active_workout_program(client_id)
    
    return render_template('trainer_edit_program.html', 
                          user=user,
                          client=client,
                          current_program=current_program)

def edit_client_meal(client_id):
    """Редактирование плана питания клиента"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if user.get('role') != 'trainer':
        flash('Доступ только для тренеров', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_user_by_id(client_id)
    
    if request.method == 'POST':
        plan_data = request.form.get('plan_data', '')
        
        from database import save_meal_plan
        save_meal_plan(
            user_id=client_id,
            plan_data=plan_data,
            is_active=True
        )
        
        flash('План питания обновлён!', 'success')
        return redirect(url_for('trainer_client', client_id=client_id))
    
    # Получаем текущий активный план
    from database import get_active_meal_plan
    current_meal = get_active_meal_plan(client_id)
    
    return render_template('trainer_edit_meal.html', 
                          user=user,
                          client=client,
                          current_meal=current_meal)
def leave_review(client_id, trainer_id):
    """Клиент оставляет отзыв тренеру"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    # Проверяем, что клиент оставляет отзыв именно своему тренеру
    if user.get('role') != 'user':
        flash('Только клиенты могут оставлять отзывы', 'danger')
        return redirect(url_for('dashboard'))
    
    client = get_user_by_id(client_id)
    trainer = get_user_by_id(trainer_id)
    
    if request.method == 'POST':
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '')
        
        from database import save_review
        save_review(client_id, trainer_id, rating, comment)
        
        flash('Спасибо за отзыв!', 'success')
        return redirect(url_for('trainer_client', client_id=client_id))
    
    return render_template('leave_review.html', 
                          user=user, 
                          client=client, 
                          trainer=trainer)