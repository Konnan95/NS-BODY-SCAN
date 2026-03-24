from flask import request, session, redirect, url_for, flash, render_template
from database import get_user_by_id, save_meal_plan
from giga_helper import ask_gigachat

def generate_meal_page():
    """Страница генерации нового плана питания"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    
    if request.method == 'POST':
        prompt = f"""
Составь примерный план питания на день для человека:
- Цель: {user.get('goal', 'tone')}
- Возраст: {user.get('age', 30)}
- Вес: {user.get('weight', 65)} кг
- Рост: {user.get('height', 165)} см
- Аллергии: {user.get('allergies', 'нет')}
- Предпочтения: {user.get('preferences', 'нет')}

Напиши план питания на день с граммовками продуктов.
"""
        meal_plan = ask_gigachat(prompt)
        
        save_meal_plan(
            user_id=user['id'],
            plan_data=meal_plan,
            is_active=True
        )
        
        flash('✅ Новый план питания сгенерирован!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('generate_meal.html', user=user)