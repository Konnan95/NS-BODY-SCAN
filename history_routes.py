from flask import render_template, session, redirect, url_for
from database import get_user_by_id, get_user_history

def history_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    posture_history, composition_history = get_user_history(user['id'])
    
    # Конвертируем кортежи в словари для удобства в шаблоне
    posture_list = []
    for p in posture_history:
        posture_list.append({
            'id': p[0],
            'user_id': p[1],
            'shoulder_slope': p[2],
            'hip_slope': p[3],
            'head_tilt': p[4],
            'posture_score': p[5],
            'created_at': p[6].strftime('%d.%m.%Y %H:%M') if p[6] else 'Дата неизвестна'
        })
    
    composition_list = []
    for c in composition_history:
        composition_list.append({
            'id': c[0],
            'user_id': c[1],
            'body_fat': c[2],
            'muscle_mass': c[3],
            'water': c[4],
            'visceral_fat': c[5],
            'created_at': c[6].strftime('%d.%m.%Y %H:%M') if c[6] else 'Дата неизвестна'
        })
    
    return render_template('history.html', 
                          user=user,
                          posture=posture_list,
                          composition=composition_list)