"""
YOLO11 + MediaPipe для анализа техники упражнений по ВИДЕО
"""

import cv2
import numpy as np
from ultralytics import YOLOE as YOLO
import mediapipe as mp
import tempfile
import os

class YoloVideoAnalyzer:
    def __init__(self):
        # Загружаем YOLO11 для детекции позы
        self.model = YOLO('yolo11n-pose.pt')
        
        # MediaPipe для более точных точек
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        self.exercise_config = {
            'squat': {
                'name': 'Приседания',
                'angles': ['knee', 'hip'],
                'good_range': {
                    'knee': (90, 110),
                    'hip': (70, 100)
                },
                'feedback': {
                    'knee_low': '⚠️ Опуститесь ниже! Колено должно быть под 90°',
                    'knee_high': '⚠️ Слишком глубоко! Колено не должно выходить за носок',
                    'hip_low': '⚠️ Наклоняйтесь больше вперёд',
                    'hip_high': '⚠️ Спина слишком вертикальна',
                    'good': '✅ Отличная техника!'
                }
            },
            'pushup': {
                'name': 'Отжимания',
                'angles': ['elbow', 'body'],
                'good_range': {
                    'elbow': (70, 100),
                    'body': (160, 180)
                },
                'feedback': {
                    'elbow_high': '⚠️ Опуститесь ниже! Локти должны быть под 90°',
                    'elbow_low': '⚠️ Слишком низко, не напрягайте плечи',
                    'body_low': '⚠️ Держите спину прямой, не прогибайтесь!',
                    'good': '✅ Отлично!'
                }
            },
            'lunge': {
                'name': 'Выпады',
                'angles': ['front_knee', 'back_knee'],
                'good_range': {
                    'front_knee': (80, 100),
                    'back_knee': (80, 100)
                },
                'feedback': {
                    'front_knee': '⚠️ Колено не должно выходить за носок!',
                    'back_knee': '⚠️ Опустите заднее колено ниже',
                    'good': '✅ Отлично!'
                }
            }
        }
    
    def calculate_angle(self, a, b, c):
        """Вычисление угла между тремя точками"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
        return angle
    
    def get_landmarks_from_yolo(self, results):
        """Получить ключевые точки из YOLO"""
        if len(results) > 0 and results[0].keypoints is not None:
            keypoints = results[0].keypoints.data[0].cpu().numpy()
            return keypoints
        return None
    
    def analyze_squat(self, landmarks):
        """Анализ приседаний по точкам"""
        try:
            # YOLO индексы: 5-левое плечо, 6-правое, 11-левый таз, 12-правый, 
            # 13-левое колено, 14-правое, 15-левая лодыжка, 16-правая
            
            left_hip = landmarks[11][:2]
            left_knee = landmarks[13][:2]
            left_ankle = landmarks[15][:2]
            left_shoulder = landmarks[5][:2]
            
            knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            hip_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            
            feedback = []
            score = 100
            
            if knee_angle < 80:
                feedback.append(self.exercise_config['squat']['feedback']['knee_low'])
                score -= 25
            elif knee_angle > 110:
                feedback.append(self.exercise_config['squat']['feedback']['knee_high'])
                score -= 20
            
            if hip_angle < 60:
                feedback.append(self.exercise_config['squat']['feedback']['hip_low'])
                score -= 15
            elif hip_angle > 100:
                feedback.append(self.exercise_config['squat']['feedback']['hip_high'])
                score -= 15
            
            if not feedback:
                feedback.append(self.exercise_config['squat']['feedback']['good'])
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {
                    'knee': round(knee_angle, 1),
                    'hip': round(hip_angle, 1)
                },
                'exercise': 'Приседания'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_pushup(self, landmarks):
        """Анализ отжиманий по точкам"""
        try:
            left_shoulder = landmarks[5][:2]
            left_elbow = landmarks[7][:2]
            left_wrist = landmarks[9][:2]
            left_hip = landmarks[11][:2]
            
            elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            body_angle = self.calculate_angle(left_shoulder, left_hip, [left_hip[0], left_hip[1] + 0.1])
            
            feedback = []
            score = 100
            
            if elbow_angle > 100:
                feedback.append(self.exercise_config['pushup']['feedback']['elbow_high'])
                score -= 30
            elif elbow_angle < 70:
                feedback.append(self.exercise_config['pushup']['feedback']['elbow_low'])
                score -= 20
            
            if body_angle < 160:
                feedback.append(self.exercise_config['pushup']['feedback']['body_low'])
                score -= 25
            
            if not feedback:
                feedback.append(self.exercise_config['pushup']['feedback']['good'])
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {
                    'elbow': round(elbow_angle, 1),
                    'body': round(body_angle, 1)
                },
                'exercise': 'Отжимания'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_video(self, video_path, exercise_type='squat'):
        """
        Анализ видео с упражнением
        Возвращает: среднюю оценку, список кадров с анализом
        """
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        scores = []
        frames_analysis = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Анализируем каждый 10-й кадр (для скорости)
            if frame_count % 10 == 0:
                results = self.model(frame)
                
                if len(results) > 0 and results[0].keypoints is not None:
                    landmarks = results[0].keypoints.data[0].cpu().numpy()
                    
                    if exercise_type == 'squat':
                        analysis = self.analyze_squat(landmarks)
                    elif exercise_type == 'pushup':
                        analysis = self.analyze_pushup(landmarks)
                    else:
                        analysis = {'error': 'Неизвестное упражнение', 'score': 0}
                    
                    if 'score' in analysis:
                        scores.append(analysis['score'])
                        frames_analysis.append({
                            'frame': frame_count,
                            'score': analysis['score'],
                            'feedback': analysis.get('feedback', [])
                        })
        
        cap.release()
        
        if scores:
            avg_score = sum(scores) / len(scores)
            
            # Определяем общую обратную связь
            if avg_score >= 85:
                final_feedback = "✅ Отлично! Техника выполнения правильная. Продолжайте в том же духе!"
            elif avg_score >= 70:
                final_feedback = "⚠️ Хорошо, но есть небольшие ошибки. Обратите внимание на рекомендации."
            else:
                final_feedback = "🔴 Техника требует улучшения. Внимательно изучите рекомендации."
            
            return {
                'avg_score': round(avg_score, 1),
                'frames_analyzed': len(scores),
                'total_frames': frame_count,
                'final_feedback': final_feedback,
                'sample_feedback': frames_analysis[0]['feedback'] if frames_analysis else [],
                'success': True
            }
        
        return {'success': False, 'error': 'Не удалось распознать позу в видео'}
    
    def save_analyzed_video(self, video_path, exercise_type='squat'):
        """
        Сохранить видео с нарисованными точками и оценкой
        """
        cap = cv2.VideoCapture(video_path)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, f'analyzed_{os.path.basename(video_path)}')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            results = self.model(frame)
            
            if len(results) > 0:
                # Рисуем точки
                annotated_frame = results[0].plot()
            else:
                annotated_frame = frame
            
            # Добавляем текст с оценкой
            cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            out.write(annotated_frame)
        
        cap.release()
        out.release()
        
        return output_path


# Глобальный экземпляр
yolo_analyzer = YoloVideoAnalyzer()