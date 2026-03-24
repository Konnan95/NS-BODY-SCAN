from flask import request, session, redirect, url_for, flash, render_template
from database import get_user_by_id, save_workout_program
from giga_helper import ask_gigachat

def generate_workout_page():
    """Страница генерации новой программы тренировок"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])

    if request.method == 'POST':
        days = int(request.form.get('days', 3))

        prompt = f"""
Составь план тренировок для человека:
- Пол: женщина
- Возраст: {user.get('age', 30)}
- Вес: {user.get('weight', 65)} кг
- Рост: {user.get('height', 165)} см
- Цель: {user.get('goal', 'tone')}
- Дней в неделю: {days}

Напиши программу тренировок на {days} дней в неделю. Для каждого упражнения укажи подходы и повторения.
"""
        workout_plan_text = ask_gigachat(prompt)

        save_workout_program(
            user_id=user['id'],
            program_data=workout_plan_text,
            days_per_week=days,
            is_active=True
        )

        flash(f'✅ Новая программа тренировок ({days} дней/неделю) сгенерирована!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('generate_workout.html', user=user)

def generate_workout_api():
    """API для генерации программы"""
    if 'user_id' not in session:
        return {'error': 'Unauthorized'}, 401

    user = get_user_by_id(session['user_id'])
    days = request.args.get('days', 3, type=int)

    prompt = f"""
Составь план тренировок для человека:
- Пол: женщина
- Возраст: {user.get('age', 30)}
- Вес: {user.get('weight', 65)} кг
- Рост: {user.get('height', 165)} см
- Цель: {user.get('goal', 'tone')}
- Дней в неделю: {days}

Напиши программу тренировок на {days} дней в неделю в формате текста.
"""
    workout_plan_text = ask_gigachat(prompt)

    return {'program': workout_plan_text}