"""
Генератор PDF-отчётов с поддержкой русского языка и красивым дизайном
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
import matplotlib.pyplot as plt
import io

# Регистрируем русский шрифт
def register_russian_font():
    """Регистрация шрифта с поддержкой кириллицы (используем системный Arial)"""
    # Путь к шрифту Arial в Windows
    arial_path = "C:\\Windows\\Fonts\\arial.ttf"
    
    if os.path.exists(arial_path):
        try:
            pdfmetrics.registerFont(TTFont('RussianFont', arial_path))
            print("✅ Шрифт Arial загружен (поддерживает кириллицу)")
            return 'RussianFont'
        except Exception as e:
            print(f"⚠️ Ошибка регистрации шрифта: {e}")
    
    # Запасной вариант
    print("⚠️ Шрифт Arial не найден, текст может отображаться некорректно")
    return 'Helvetica'# Получаем имя шрифта
RUSSIAN_FONT = register_russian_font()


def generate_pdf_report(user, posture_data, composition_data, workout_plan, meal_plan):
    """Генерация улучшенного PDF-отчёта с поддержкой русского языка"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"report_{user['username']}_{timestamp}.pdf"
    filepath = os.path.join('static/reports', filename)
    os.makedirs('static/reports', exist_ok=True)
    
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           topMargin=2*cm, bottomMargin=2*cm,
                           leftMargin=2*cm, rightMargin=2*cm)
    
    styles = getSampleStyleSheet()
    
    # Кастомные стили с поддержкой русского языка
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=RUSSIAN_FONT,
        fontSize=24,
        textColor=colors.HexColor('#ff66b5'),
        alignment=1,  # center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName=RUSSIAN_FONT,
        fontSize=16,
        textColor=colors.HexColor('#667eea'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontName=RUSSIAN_FONT,
        fontSize=11,
        leading=14
    )
    
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=normal_style,
        fontName=RUSSIAN_FONT,
        fontSize=11,
        textColor=colors.white,
        alignment=1
    )
    
    story = []
    
    # Заголовок
    story.append(Paragraph("NS Body Scan", title_style))
    story.append(Paragraph("<b>Отчёт по анализу тела</b>", heading_style))
    story.append(Paragraph(f"<i>Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>", normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Информация о пользователе
    story.append(Paragraph("📊 Информация о пользователе", heading_style))
    user_info = [
        ["Имя:", user.get('name', '—')],
        ["Возраст:", f"{user.get('age', '—')} лет"],
        ["Рост:", f"{user.get('height', '—')} см"],
        ["Вес:", f"{user.get('weight', '—')} кг"],
        ["Цель:", user.get('goal', '—')]
    ]
    user_table = Table(user_info, colWidths=[4*cm, 8*cm])
    user_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), RUSSIAN_FONT),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f0f0f0')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(user_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Анализ осанки
    story.append(Paragraph("📐 Анализ осанки", heading_style))
    posture_table = [
        ["Параметр", "Значение", "Норма"],
        ["Наклон плеч", f"{posture_data['shoulder']}%", "< 5%"],
        ["Наклон таза", f"{posture_data['hip']}%", "< 5%"],
        ["Наклон головы", f"{posture_data['head']}°", "0-10°"],
        ["Оценка", f"{posture_data['score']}/10", "> 7/10"]
    ]
    posture_t = Table(posture_table, colWidths=[5*cm, 4*cm, 4*cm])
    posture_t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), RUSSIAN_FONT),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(posture_t)
    story.append(Spacer(1, 0.5*cm))
    
    # Анализ состава тела
    story.append(Paragraph("🧬 Анализ состава тела", heading_style))
    composition_table = [
        ["Параметр", "Значение", "Норма"],
        ["% жира", f"{composition_data['body_fat']}%", "18-28%"],
        ["Мышечная масса", f"{composition_data['muscle_mass']} кг", "25-35 кг"],
        ["Вода", f"{composition_data['water']} кг", "45-60% от веса"],
        ["Висцеральный жир", str(composition_data['visceral_fat']), "1-9"],
        ["Калории", f"{composition_data['calories']} ккал", "1500-2500"],
        ["Белки", f"{composition_data['protein']} г", "80-120"],
        ["Жиры", f"{composition_data['fat']} г", "40-70"],
        ["Углеводы", f"{composition_data['carbs']} г", "150-250"]
    ]
    composition_t = Table(composition_table, colWidths=[5*cm, 4*cm, 4*cm])
    composition_t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), RUSSIAN_FONT),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#ff66b5')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    story.append(composition_t)
    story.append(Spacer(1, 0.5*cm))
    
    # План тренировок
    story.append(Paragraph("🏋️ План тренировок", heading_style))
    # Обрезаем слишком длинный текст
    workout_text = workout_plan[:2000] if len(workout_plan) > 2000 else workout_plan
    story.append(Paragraph(workout_text, normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # План питания
    story.append(Paragraph("🥗 План питания", heading_style))
    meal_text = meal_plan[:2000] if len(meal_plan) > 2000 else meal_plan
    story.append(Paragraph(meal_text, normal_style))
    
    # Построение документа
    doc.build(story)
    
    # Возвращаем URL для скачивания
    return f'/static/reports/{filename}'