"""
Body Fat Prediction — улучшенные формулы (US Navy, YMCA, BMI)
"""

import numpy as np
import os

class BodyFatPredictor:
    def __init__(self, model_path=None):
        self.model = None
        print("✅ Используем улучшенные формулы (US Navy + YMCA + BMI)")
    
    def predict(self, measurements):
        """
        Предсказать % жира по измерениям
        measurements: словарь с ключами: neck, waist, hip, height, weight, age
        """
        try:
            neck = measurements.get('neck', 35)
            waist = measurements.get('waist', 80)
            hip = measurements.get('hip', 95)
            height = measurements.get('height', 170)
            weight = measurements.get('weight', 70)
            age = measurements.get('age', 30)
            
            # ========== 1. Метод US Navy ==========
            try:
                # Формула для женщин
                body_density = 1.097 - 0.00046971 * (waist - neck) + 0.00000056 * (waist - neck)**2 - 0.00012828 * (hip - neck)
                fat_navy = (495 / body_density) - 450
                fat_navy = max(10, min(45, fat_navy))
            except:
                fat_navy = 25
            
            # ========== 2. Метод YMCA ==========
            # По обхвату талии, весу и возрасту
            fat_ymca = (0.439 * waist) + (0.221 * age) - (0.009 * weight) - 9.0
            fat_ymca = max(10, min(45, fat_ymca))
            
            # ========== 3. Метод BMI ==========
            bmi = weight / ((height/100) ** 2)
            fat_bmi = (1.20 * bmi) + (0.23 * age) - 5.4
            fat_bmi = max(10, min(45, fat_bmi))
            
            # ========== Усредняем ==========
            fats = [fat_navy, fat_ymca, fat_bmi]
            fats = [f for f in fats if 10 < f < 45]
            
            if fats:
                body_fat = sum(fats) / len(fats)
            else:
                body_fat = fat_bmi
            
            body_fat = round(body_fat, 1)
            
            # ========== Рассчитываем мышечную массу ==========
            muscle_mass = weight * (100 - body_fat) / 100 * 0.45
            
            # ========== Висцеральный жир ==========
            visceral_fat = max(1, min(30, int((bmi - 18.5) * 2)))
            
            return {
                'body_fat': body_fat,
                'muscle_mass': round(muscle_mass, 1),
                'visceral_fat': visceral_fat,
                'method': 'averaged_formulas',
                'details': {
                    'US Navy': round(fat_navy, 1),
                    'YMCA': round(fat_ymca, 1),
                    'BMI': round(fat_bmi, 1)
                }
            }
        except Exception as e:
            print(f"Ошибка предсказания: {e}")
            return None

# Глобальный экземпляр
body_fat_predictor = BodyFatPredictor()