"""
Модуль анализа осанки и состава тела
"""

import cv2
import mediapipe as mp
import math
import os

mp_pose = mp.solutions.pose

def analyze_posture(image_path):
    """Анализ осанки по фото с подробной отладкой и всеми метриками"""
    try:
        print(f"📸 Анализируем: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ Файл не существует: {image_path}")
            return None
        
        img = cv2.imread(image_path)
        if img is None:
            print("❌ OpenCV не смог загрузить фото")
            return None
        
        # ========== ПРЕДОБРАБОТКА ==========
        # Улучшаем контрастность
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        img = cv2.merge((l, a, b))
        img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
        
        # Нормализуем размер
        scale = min(800 / img.shape[1], 800 / img.shape[0])
        if scale < 1:
            new_width = int(img.shape[1] * scale)
            new_height = int(img.shape[0] * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        # Убираем шум
        img = cv2.GaussianBlur(img, (3, 3), 0)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # ========== ПРОБУЕМ РАЗНЫЕ НАСТРОЙКИ ==========
        settings_to_try = [
            {"static_image_mode": True, "model_complexity": 2, "min_detection_confidence": 0.5},
            {"static_image_mode": True, "model_complexity": 2, "min_detection_confidence": 0.3},
            {"static_image_mode": True, "model_complexity": 1, "min_detection_confidence": 0.2},
            {"static_image_mode": True, "model_complexity": 1, "min_detection_confidence": 0.4},
            {"static_image_mode": True, "model_complexity": 0, "min_detection_confidence": 0.3},
        ]
        
        results = None
        for settings in settings_to_try:
            pose = mp_pose.Pose(**settings)
            results = pose.process(img_rgb)
            if results and results.pose_landmarks:
                print(f"✅ Настройки сработали: {settings}")
                break
        
        if not results or not results.pose_landmarks:
            print("❌ Тело не обнаружено ни с какими настройками")
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        # ========== ВСЕ МЕТРИКИ ==========
        
        # 1. Плечи (наклон и асимметрия)
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        dx = right_shoulder.x - left_shoulder.x
        dy = right_shoulder.y - left_shoulder.y
        shoulder_slope = math.degrees(math.atan2(dy, dx)) if dx != 0 else 0
        shoulder_asymmetry = abs(left_shoulder.y - right_shoulder.y) * 100
        
        # 2. Таз (перекос)
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        dx = right_hip.x - left_hip.x
        dy = right_hip.y - left_hip.y
        hip_slope = math.degrees(math.atan2(dy, dx)) if dx != 0 else 0
        hip_asymmetry = abs(left_hip.y - right_hip.y) * 100
        
        # 3. Голова (наклон)
        nose = landmarks[0]
        left_ear = landmarks[7]
        right_ear = landmarks[8]
        ear_center_x = (left_ear.x + right_ear.x) / 2
        ear_center_y = (left_ear.y + right_ear.y) / 2
        head_tilt = math.degrees(math.atan2(nose.y - ear_center_y, nose.x - ear_center_x))
        
        # 4. Колени (вальгус/варус)
        left_knee = landmarks[25]
        right_knee = landmarks[26]
        knee_distance = abs(left_knee.x - right_knee.x) * 100
        knee_valgus = knee_distance  # упрощённо, чем больше расстояние, тем сильнее вальгус
        
        # 5. Спина (сутулость) — расстояние между ушами и плечами
        ear_y = (left_ear.y + right_ear.y) / 2
        shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
        back_curve = (ear_y - shoulder_y) * 100  # положительное = сутулость
        
        # 6. Стопы (положение) — если видны
        left_ankle = landmarks[27]
        right_ankle = landmarks[28]
        if left_ankle and right_ankle:
            foot_angle = math.degrees(math.atan2(right_ankle.y - left_ankle.y, right_ankle.x - left_ankle.x))
        else:
            foot_angle = 0
        
        # 7. Общая оценка осанки
        score = 10.0
        score -= min(abs(shoulder_slope) / 5, 2.5)
        score -= min(abs(hip_slope) / 5, 2.0)
        score -= min(abs(head_tilt) / 10, 1.5)
        score -= min(knee_valgus / 20, 1.5)
        score -= min(abs(back_curve) / 10, 1.5)
        score = max(1.0, round(score, 1))
        
        # 8. Статус каждой зоны
        zones = {
            'shoulders': {
                'value': round(shoulder_slope, 1),
                'status': 'normal' if abs(shoulder_slope) < 3 else 'need_correction',
                'name': 'Плечи'
            },
            'hips': {
                'value': round(hip_slope, 1),
                'status': 'normal' if abs(hip_slope) < 3 else 'need_correction',
                'name': 'Таз'
            },
            'head': {
                'value': round(head_tilt, 1),
                'status': 'normal' if abs(head_tilt) < 5 else 'need_correction',
                'name': 'Голова/шея'
            },
            'knees': {
                'value': round(knee_valgus, 1),
                'status': 'normal' if knee_valgus < 15 else 'need_correction',
                'name': 'Колени'
            },
            'back': {
                'value': round(back_curve, 1),
                'status': 'normal' if back_curve < 5 else 'need_correction',
                'name': 'Спина'
            },
            'feet': {
                'value': round(foot_angle, 1),
                'status': 'normal' if abs(foot_angle) < 10 else 'need_correction',
                'name': 'Стопы'
            }
        }
        
        result = {
            'shoulder_slope': round(shoulder_slope, 1),
            'shoulder_asymmetry': round(shoulder_asymmetry, 1),
            'hip_slope': round(hip_slope, 1),
            'hip_asymmetry': round(hip_asymmetry, 1),
            'head_tilt': round(head_tilt, 1),
            'knee_valgus': round(knee_valgus, 1),
            'back_curve': round(back_curve, 1),
            'foot_angle': round(foot_angle, 1),
            'posture_score': score,
            'zones': zones
        }
        
        print(f"✅ Результат: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_body_composition(bmi, age, gender='female', weight=65):
    """
    Расчёт состава тела по формулам
    bmi: индекс массы тела
    age: возраст
    gender: 'male' или 'female'
    weight: вес в кг
    """
    # Процент жира (формула на основе BMI и возраста)
    if gender == 'female':
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    else:
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    
    body_fat = max(5, min(50, round(body_fat, 1)))
    
    # Мышечная масса (упрощённо)
    muscle_mass = round(weight * (100 - body_fat) / 100 * 0.45, 1)
    
    # Вода (около 60% веса)
    water = round(weight * 0.6, 1)
    
    # Висцеральный жир (уровень от 1 до 30)
    visceral_fat = min(30, max(1, int(bmi - 18.5) * 2))
    
    return {
        'body_fat': body_fat,
        'muscle_mass': muscle_mass,
        'water': water,
        'visceral_fat': visceral_fat
    }


def get_body_composition(weight, height, age, gender='female'):
    """
    Рассчитать состав тела на основе антропометрии
    weight: вес в кг
    height: рост в см
    age: возраст
    gender: 'male' или 'female'
    """
    bmi = weight / ((height/100) ** 2)
    return analyze_body_composition(bmi, age, gender, weight)