"""
Генерация PDF-отчёта
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
from datetime import datetime

def generate_pdf_report(user, posture, body, workout_plan, meal_plan):
    """Сгенерировать PDF-отчёт"""
    filename = f"report_{user['username']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join('static', 'reports', filename)
    
    # Создаём папку, если её нет
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    y = height - 50
    
    # Заголовок
    c.setFont("Helvetica-Bold", 24)
    c.drawString(50, y, "NS Body Scan")
    y -= 40
    
    # Информация о пользователе
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Отчёт для: {user.get('name', user['username'])}")
    y -= 20
    c.drawString(50, y, f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    y -= 40
    
    # Анализ осанки
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Результаты анализа осанки")
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Наклон плеч: {posture['shoulder']}°")
    y -= 15
    c.drawString(50, y, f"Наклон таза: {posture['hip']}°")
    y -= 15
    c.drawString(50, y, f"Наклон головы: {posture['head']}°")
    y -= 15
    c.drawString(50, y, f"Оценка осанки: {posture['score']}/10")
    y -= 30
    
    # Состав тела
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Анализ состава тела")
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"% жира: {body['body_fat']}% (норма 18-28%)")
    y -= 15
    c.drawString(50, y, f"Мышечная масса: {body['muscle_mass']} кг")
    y -= 15
    c.drawString(50, y, f"Вода: {body['water']} кг")
    y -= 15
    c.drawString(50, y, f"Висцеральный жир: {body['visceral_fat']} (уровень)")
    y -= 30
    
    # Рекомендации по питанию
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Рекомендации по питанию")
    y -= 25
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Калории: {body['calories']} ккал/день")
    y -= 15
    c.drawString(50, y, f"Белки: {body['protein']} г, Жиры: {body['fat']} г, Углеводы: {body['carbs']} г")
    y -= 30
    
    # План тренировок
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "План тренировок")
    y -= 25
    c.setFont("Helvetica", 9)
    
    # Разбиваем длинный текст на строки
    lines = workout_plan.split('\n')
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)
        # Обрезаем слишком длинные строки
        if len(line) > 90:
            line = line[:87] + "..."
        c.drawString(50, y, line)
        y -= 15
    
    # Если места мало — новая страница
    if y < 100:
        c.showPage()
        y = height - 50
    else:
        y -= 20
    
    # План питания
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "План питания (на день)")
    y -= 25
    c.setFont("Helvetica", 9)
    
    lines = meal_plan.split('\n')
    for line in lines:
        if y < 50:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)
        if len(line) > 90:
            line = line[:87] + "..."
        c.drawString(50, y, line)
        y -= 15
    
    c.save()
    return f"/static/reports/{filename}"