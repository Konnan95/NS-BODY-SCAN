"""
Модуль личного кабинета
"""

from flask import session, redirect, url_for, render_template
from database import get_user_by_id


def dashboard_page():
    """Страница личного кабинета"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)