import csv
import io
from flask import send_file, session, redirect, url_for
from database import get_db_connection

def export_posture_csv():
    """Экспорт анализов осанки в CSV"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT created_at, shoulder_slope, hip_slope, head_tilt, posture_score, kyphosis, neck_angle, symmetry
        FROM posture_analyses
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Дата', 'Наклон плеч (%)', 'Наклон таза (%)', 'Наклон головы (°)', 'Оценка', 'Кифоз (%)', 'Угол шеи (°)', 'Симметрия (%)'])
    for row in rows:
        writer.writerow(row)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='posture_analyses.csv'
    )

def export_body_composition_csv():
    """Экспорт анализов состава тела в CSV"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT created_at, body_fat, muscle_mass, water, visceral_fat
        FROM body_composition
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    rows = cur.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Дата', '% жира', 'Мышечная масса (кг)', 'Вода (кг)', 'Висцеральный жир'])
    for row in rows:
        writer.writerow(row)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='body_composition.csv'
    )