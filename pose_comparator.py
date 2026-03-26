"""
Сравнение позы пользователя с эталоном
"""

import cv2
import numpy as np
import mediapipe as mp

class PoseComparator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils
    
    def extract_landmarks(self, image_path):
        """Извлекает ключевые точки из изображения"""
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        if results.pose_landmarks:
            landmarks = []
            for lm in results.pose_landmarks.landmark:
                landmarks.append([lm.x, lm.y])
            return landmarks, image.shape
        return None, None
    
    def draw_skeleton(self, image, landmarks, color=(0, 255, 0), thickness=2):
        """Рисует скелет на изображении"""
        h, w = image.shape[:2]
        
        # Соединения между ключевыми точками (MediaPipe)
        connections = [
            (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # руки
            (23, 24), (23, 25), (25, 27), (24, 26), (26, 28),  # ноги
            (11, 23), (12, 24), (23, 24)  # тело
        ]
        
        # Рисуем точки
        for i, (x, y) in enumerate(landmarks):
            cx, cy = int(x * w), int(y * h)
            cv2.circle(image, (cx, cy), 5, color, -1)
        
        # Рисуем соединения
        for a, b in connections:
            if a < len(landmarks) and b < len(landmarks):
                x1, y1 = int(landmarks[a][0] * w), int(landmarks[a][1] * h)
                x2, y2 = int(landmarks[b][0] * w), int(landmarks[b][1] * h)
                cv2.line(image, (x1, y1), (x2, y2), color, thickness)
        
        return image
    
    def compare_with_template(self, user_image_path, exercise_type):
        """Сравнивает позу пользователя с эталоном"""
        # Извлекаем ключевые точки пользователя
        user_landmarks, shape = self.extract_landmarks(user_image_path)
        if user_landmarks is None:
            return None
        
        # Получаем эталонные точки (упрощённо — идеальные углы)
        ideal_angles = self.get_ideal_angles(exercise_type)
        
        # Создаём изображение для сравнения
        result_img = np.zeros((600, 800, 3), dtype=np.uint8)
        result_img[:] = (240, 240, 240)
        
        # Рисуем скелет пользователя
        user_img = self.draw_skeleton(result_img.copy(), user_landmarks, (0, 0, 255), 2)
        
        # Сравниваем углы
        feedback = self.compare_angles(user_landmarks, ideal_angles, exercise_type)
        
        return {
            'image': user_img,
            'feedback': feedback,
            'user_landmarks': user_landmarks
        }
    
    def get_ideal_angles(self, exercise_type):
        """Идеальные углы для упражнений"""
        ideals = {
            'squat': {
                'knee': 90,
                'hip': 85,
                'back': 170
            },
            'pushup': {
                'elbow': 90,
                'body': 170
            },
            'lunge': {
                'front_knee': 90,
                'back_knee': 90
            }
        }
        return ideals.get(exercise_type, {})
    
    def compare_angles(self, landmarks, ideal_angles, exercise_type):
        """Сравнивает углы пользователя с идеальными"""
        feedback = []
        
        try:
            if exercise_type == 'squat':
                # Вычисляем углы пользователя
                left_hip = landmarks[23]
                left_knee = landmarks[25]
                left_ankle = landmarks[27]
                left_shoulder = landmarks[11]
                
                # Упрощённый расчёт (здесь нужна реальная математика)
                user_knee = 100  # placeholder
                user_hip = 80    # placeholder
                
                if user_knee > ideal_angles.get('knee', 90) + 10:
                    feedback.append("⚠️ Колено согнуто недостаточно. Опуститесь ниже!")
                elif user_knee < ideal_angles.get('knee', 90) - 10:
                    feedback.append("⚠️ Слишком глубоко! Колено не должно выходить за носок.")
                
                if user_hip > ideal_angles.get('hip', 85) + 10:
                    feedback.append("⚠️ Наклоняйтесь больше вперёд!")
                elif user_hip < ideal_angles.get('hip', 85) - 10:
                    feedback.append("⚠️ Спина слишком вертикальна!")
            
            elif exercise_type == 'pushup':
                if 100 > ideal_angles.get('elbow', 90) + 10:  # placeholder
                    feedback.append("⚠️ Опуститесь ниже! Локти должны быть под 90°")
            
            elif exercise_type == 'lunge':
                if 100 > ideal_angles.get('front_knee', 90) + 10:
                    feedback.append("⚠️ Опуститесь ниже! Колено должно быть под 90°")
            
            if not feedback:
                feedback.append("✅ Отличная техника! Так держать!")
                
        except Exception as e:
            feedback.append(f"⚠️ Ошибка сравнения: {e}")
        
        return feedback[:3]

pose_comparator = PoseComparator()