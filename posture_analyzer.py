"""
Модуль анализа осанки с MediaPipe Pose (33 точки)
"""

import cv2
import numpy as np
import mediapipe as mp
from werkzeug.utils import secure_filename
import os
from datetime import datetime

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

def calculate_angle(a, b, c):
    """Вычисление угла между тремя точками в градусах"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def extract_landmarks(pose_landmarks):
    """Извлечение координат 33 точек"""
    landmarks = []
    for i in range(33):
        x = pose_landmarks.landmark[i].x
        y = pose_landmarks.landmark[i].y
        landmarks.append([x, y])
    return landmarks

def analyze_posture(image_path):
    """
    Полный анализ осанки по фото
    Возвращает: метрики, оригинальное фото с разметкой, путь к сохранённому фото
    """
    # Читаем изображение
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Не удалось загрузить изображение: {image_path}")
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        raise ValueError("Не удалось обнаружить позу на изображении")
    
    landmarks = extract_landmarks(results.pose_landmarks)
    
    # Извлекаем координаты ключевых точек
    left_shoulder = landmarks[11]
    right_shoulder = landmarks[12]
    left_hip = landmarks[23]
    right_hip = landmarks[24]
    left_knee = landmarks[25]
    right_knee = landmarks[26]
    left_ankle = landmarks[27]
    right_ankle = landmarks[28]
    nose = landmarks[0]
    left_ear = landmarks[7]
    right_ear = landmarks[8]
    left_elbow = landmarks[13]
    right_elbow = landmarks[14]
    
    # 1. Наклон плеч (разница высоты в процентах)
    shoulder_tilt = abs(left_shoulder[1] - right_shoulder[1]) * 100
    
    # 2. Наклон таза
    hip_tilt = abs(left_hip[1] - right_hip[1]) * 100
    
    # 3. Наклон головы (угол между ушами и носом)
    head_tilt = calculate_angle(left_ear, nose, right_ear)
    
    # 4. Грудной кифоз (угол между плечами и тазом)
    shoulder_center = [(left_shoulder[0] + right_shoulder[0]) / 2, 
                        (left_shoulder[1] + right_shoulder[1]) / 2]
    hip_center = [(left_hip[0] + right_hip[0]) / 2, 
                   (left_hip[1] + right_hip[1]) / 2]
    kyphosis = abs(shoulder_center[1] - hip_center[1]) * 100
    
    # 5. Угол шеи (голова → плечи)
    neck_angle = calculate_angle(left_shoulder, nose, right_shoulder)
    
    # 6. Вальгус колен (угол коленей)
    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
    knee_valgus = abs(left_knee_angle - right_knee_angle)
    
    # 7. Симметрия тела
    left_points = [left_shoulder, left_hip, left_knee, left_ankle]
    right_points = [right_shoulder, right_hip, right_knee, right_ankle]
    symmetry = 100 - sum(abs(l[0] - r[0]) for l, r in zip(left_points, right_points)) / len(left_points) * 100
    symmetry = max(0, min(100, symmetry))
    
    # 8. Общая оценка осанки (0-10)
    posture_score = 10 - (
        (shoulder_tilt / 10) + 
        (hip_tilt / 10) + 
        (head_tilt / 20) + 
        (kyphosis / 20) + 
        (100 - symmetry) / 10
    ) / 5
    posture_score = max(0, min(10, posture_score))
    
    # Рисуем точки на фото
    mp_drawing = mp.solutions.drawing_utils
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
    )
    
    # Добавляем текст с метриками
    cv2.putText(annotated_image, f"Score: {posture_score:.1f}/10", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(annotated_image, f"Shoulder tilt: {shoulder_tilt:.1f}%", (10, 55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(annotated_image, f"Hip tilt: {hip_tilt:.1f}%", (10, 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(annotated_image, f"Head tilt: {head_tilt:.1f} deg", (10, 95), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(annotated_image, f"Kyphosis: {kyphosis:.1f}%", (10, 115), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    return {
        'shoulder_tilt': round(shoulder_tilt, 1),
        'hip_tilt': round(hip_tilt, 1),
        'head_tilt': round(head_tilt, 1),
        'kyphosis': round(kyphosis, 1),
        'neck_angle': round(neck_angle, 1),
        'knee_valgus': round(knee_valgus, 1),
        'symmetry': round(symmetry, 1),
        'posture_score': round(posture_score, 1),
        'annotated_image': annotated_image
    }

def save_analyzed_photo(image, user_id, view):
    """Сохранить фото с разметкой с указанием ракурса"""
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"user_{user_id}_{timestamp}_{view}_analyzed.jpg"
    filepath = os.path.join('uploads', 'analyzed', filename)
    cv2.imwrite(filepath, image)
    return filepath

def save_original_photo(original_path, user_id, view):
    """Сохранить оригинальное фото с указанием ракурса"""
    from datetime import datetime
    import shutil
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"user_{user_id}_{timestamp}_{view}_original.jpg"
    new_path = os.path.join('uploads', 'originals', filename)
    shutil.copy(original_path, new_path)
    return new_path