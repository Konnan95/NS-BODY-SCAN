"""
BodyPix анализатор — сегментация тела и расчёт пропорций
Использует OpenCV для упрощённого анализа
"""

import cv2
import numpy as np
import os

class BodyPixAnalyzer:
    def __init__(self):
        print("✅ BodyPix анализатор загружен (упрощённая версия)")
    
    def analyze_from_image(self, image_path):
        """
        Анализ пропорций тела по фото
        Возвращает: соотношение плеч/талии/бёдер, тип фигуры
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return {'success': False, 'error': 'Не удалось загрузить изображение'}
            
            height, width = image.shape[:2]
            
            # Упрощённый расчёт пропорций
            # Делим изображение на вертикальные зоны
            top = height // 6           # плечи
            middle = height // 2        # талия
            bottom = height * 4 // 6    # бёдра
            
            # Находим ширину в каждой зоне (простейший метод)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Увеличиваем контраст для лучшего выделения силуэта
            _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
            
            # Ищем края тела
            def get_body_width(row):
                row_data = binary[row, :]
                non_zero = np.where(row_data > 0)[0]
                if len(non_zero) > 1:
                    return non_zero[-1] - non_zero[0]
                return 0
            
            # Получаем ширину в каждой зоне
            shoulder_width = get_body_width(top)
            waist_width = get_body_width(middle)
            hip_width = get_body_width(bottom)
            
            # Проверяем, что все измерения корректны
            if shoulder_width == 0 or waist_width == 0:
                return {
                    'success': False,
                    'error': 'Не удалось определить контуры тела. Попробуйте фото с лучшим контрастом.'
                }
            
            # Соотношения
            ratio_shoulder_waist = round(shoulder_width / waist_width, 2)
            ratio_hip_waist = round(hip_width / waist_width, 2)
            
            # Определяем тип фигуры
            if ratio_shoulder_waist > 1.2 and ratio_hip_waist > 1.2:
                body_type = "Песочные часы"
            elif ratio_shoulder_waist > ratio_hip_waist + 0.1:
                body_type = "Перевёрнутый треугольник"
            elif ratio_hip_waist > ratio_shoulder_waist + 0.1:
                body_type = "Груша"
            else:
                body_type = "Прямоугольник"
            
            return {
                'shoulder_width': int(shoulder_width),
                'waist_width': int(waist_width),
                'hip_width': int(hip_width),
                'ratio_shoulder_waist': ratio_shoulder_waist,
                'ratio_hip_waist': ratio_hip_waist,
                'body_type': body_type,
                'success': True
            }
            
        except Exception as e:
            print(f"BodyPix ошибка: {e}")
            return {'success': False, 'error': str(e)}


# Глобальный экземпляр
bodypix = BodyPixAnalyzer()