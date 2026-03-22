from flask import render_template, session, redirect, url_for
from database import get_user_by_id, get_user_history

def history_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    posture_history, composition_history = get_user_history(user['id'])
    
    return render_template('history.html', 
                          user=user,
                          posture=posture_history,
                          composition=composition_history)