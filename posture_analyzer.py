import cv2
import mediapipe as mp
import math
import os

# Инициализация MediaPipe (один раз при импорте)
mp_pose = mp.solutions.pose

def analyze_posture(image_path):
    """Улучшенный анализ осанки с адаптацией под разные условия"""
    try:
        print(f"📸 Анализируем: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"❌ Файл не существует: {image_path}")
            return None
        
        img = cv2.imread(image_path)
        if img is None:
            print("❌ OpenCV не смог загрузить фото")
            return None
        
        print(f"✅ Фото загружено, размер: {img.shape}")
        
        # ========== ПРЕДОБРАБОТКА ФОТО ==========
        
        # 1. Улучшаем контрастность (помогает на тёмных фото)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        l = clahe.apply(l)
        img = cv2.merge((l, a, b))
        img = cv2.cvtColor(img, cv2.COLOR_LAB2BGR)
        
        # 2. Увеличиваем размер для лучшего распознавания
        scale = min(800 / img.shape[1], 800 / img.shape[0])
        if scale < 1:
            new_width = int(img.shape[1] * scale)
            new_height = int(img.shape[0] * scale)
            img = cv2.resize(img, (new_width, new_height))
        
        # 3. Добавляем небольшое размытие для шумоподавления
        img = cv2.GaussianBlur(img, (3, 3), 0)
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # ========== ПРОБУЕМ РАЗНЫЕ НАСТРОЙКИ MEDIAPIPE ==========
        
        settings_to_try = [
            {"static_image_mode": True, "model_complexity": 2, "min_detection_confidence": 0.5, "min_tracking_confidence": 0.5},
            {"static_image_mode": True, "model_complexity": 2, "min_detection_confidence": 0.3, "min_tracking_confidence": 0.3},
            {"static_image_mode": True, "model_complexity": 1, "min_detection_confidence": 0.2, "min_tracking_confidence": 0.2},
            {"static_image_mode": True, "model_complexity": 0, "min_detection_confidence": 0.4, "min_tracking_confidence": 0.4}
        ]
        
        results = None
        for i, settings in enumerate(settings_to_try):
            print(f"🔄 Пробуем настройки {i+1}")
            pose = mp_pose.Pose(**settings)
            results = pose.process(img_rgb)
            if results and results.pose_landmarks:
                print(f"✅ Настройки {i+1} сработали!")
                break
        
        if not results or not results.pose_landmarks:
            print("❌ Тело не обнаружено ни с какими настройками")
            return None
        
        landmarks = results.pose_landmarks.landmark
        
        left_shoulder = landmarks[11]
        right_shoulder = landmarks[12]
        left_hip = landmarks[23]
        right_hip = landmarks[24]
        nose = landmarks[0]
        left_ear = landmarks[7]
        right_ear = landmarks[8]
        
        print(f"   Видимость плеч: левое={left_shoulder.visibility:.2f}, правое={right_shoulder.visibility:.2f}")
        
        # Наклон плеч
        dx = right_shoulder.x - left_shoulder.x
        dy = right_shoulder.y - left_shoulder.y
        shoulder_slope = math.degrees(math.atan2(dy, dx)) if dx != 0 else 0
        
        # Наклон таза
        dx = right_hip.x - left_hip.x
        dy = right_hip.y - left_hip.y
        hip_slope = math.degrees(math.atan2(dy, dx)) if dx != 0 else 0
        
        # Наклон головы
        ear_center_x = (left_ear.x + right_ear.x) / 2
        ear_center_y = (left_ear.y + right_ear.y) / 2
        head_tilt = math.degrees(math.atan2(nose.y - ear_center_y, nose.x - ear_center_x))
        
        # Оценка осанки
        score = 10.0
        score -= min(abs(shoulder_slope) / 5, 2.5)
        score -= min(abs(hip_slope) / 5, 2.0)
        score -= min(abs(head_tilt) / 10, 1.5)
        score = max(1.0, round(score, 1))
        
        result = {
            "shoulder_slope": round(shoulder_slope, 1),
            "hip_slope": round(hip_slope, 1),
            "head_tilt": round(head_tilt, 1),
            "score": score
        }
        
        print(f"✅ Результат: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()
        return None