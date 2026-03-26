"""
Анализ техники упражнений по видео (MediaPipe)
Поддерживает: приседания, отжимания, выпады, становую тягу, планку, подтягивания, отжимания на брусьях, подъём ног
"""

import cv2
import mediapipe as mp
import numpy as np
import tempfile
import os

class VideoAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.exercises = {
            'squat': {
                'name': 'Приседания',
                'analyze': self.analyze_squat_frame
            },
            'pushup': {
                'name': 'Отжимания',
                'analyze': self.analyze_pushup_frame
            },
            'lunge': {
                'name': 'Выпады',
                'analyze': self.analyze_lunge_frame
            },
            'deadlift': {
                'name': 'Становая тяга',
                'analyze': self.analyze_deadlift_frame
            },
            'plank': {
                'name': 'Планка',
                'analyze': self.analyze_plank_frame
            },
            'pullup': {
                'name': 'Подтягивания',
                'analyze': self.analyze_pullup_frame
            },
            'dip': {
                'name': 'Отжимания на брусьях',
                'analyze': self.analyze_dip_frame
            },
            'leg_raise': {
                'name': 'Подъём ног',
                'analyze': self.analyze_leg_raise_frame
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
    
    def analyze_squat_frame(self, landmarks):
        """Анализ приседаний"""
        try:
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            
            knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            hip_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            
            feedback = []
            score = 100
            
            if knee_angle < 80:
                feedback.append("⚠️ Опуститесь ниже! Колено должно быть под 90°")
                score -= 25
            elif knee_angle > 110:
                feedback.append("⚠️ Слишком глубоко! Колено не должно выходить за носок")
                score -= 20
            
            if hip_angle < 60:
                feedback.append("⚠️ Наклоняйтесь больше вперёд")
                score -= 15
            elif hip_angle > 100:
                feedback.append("⚠️ Спина слишком вертикальна")
                score -= 15
            
            if not feedback:
                feedback.append("✅ Отличная техника приседаний!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'knee': round(knee_angle, 1), 'hip': round(hip_angle, 1)},
                'exercise': 'Приседания'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_pushup_frame(self, landmarks):
        """Анализ отжиманий"""
        try:
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            
            elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            body_angle = self.calculate_angle(left_shoulder, left_hip, [left_hip[0], left_hip[1] + 0.1])
            
            feedback = []
            score = 100
            
            if elbow_angle > 100:
                feedback.append("⚠️ Опуститесь ниже! Локти должны быть под 90°")
                score -= 30
            elif elbow_angle < 70:
                feedback.append("⚠️ Слишком низко, не напрягайте плечи")
                score -= 20
            
            if body_angle < 160:
                feedback.append("⚠️ Держите спину прямой, не прогибайтесь!")
                score -= 25
            
            if not feedback:
                feedback.append("✅ Отличные отжимания!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'elbow': round(elbow_angle, 1), 'body': round(body_angle, 1)},
                'exercise': 'Отжимания'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_lunge_frame(self, landmarks):
        """Анализ выпадов"""
        try:
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            right_hip = [landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                         landmarks[self.mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            right_knee = [landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].x,
                          landmarks[self.mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
            right_ankle = [landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,
                           landmarks[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
            
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            feedback = []
            score = 100
            
            if left_knee_angle < 80 or right_knee_angle < 80:
                feedback.append("⚠️ Опуститесь ниже! Колено должно быть под 90°")
                score -= 30
            
            if left_knee_angle > 110 or right_knee_angle > 110:
                feedback.append("⚠️ Колено не должно выходить за носок!")
                score -= 25
            
            if not feedback:
                feedback.append("✅ Отличные выпады!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'left_knee': round(left_knee_angle, 1), 'right_knee': round(right_knee_angle, 1)},
                'exercise': 'Выпады'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_deadlift_frame(self, landmarks):
        """Анализ становой тяги"""
        try:
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            
            back_angle = self.calculate_angle(left_shoulder, left_hip, left_knee)
            
            feedback = []
            score = 100
            
            if back_angle < 30:
                feedback.append("⚠️ Спина слишком округлена! Держите спину прямой")
                score -= 40
            elif back_angle < 45:
                feedback.append("⚠️ Спина недостаточно прямая")
                score -= 25
            elif back_angle > 70:
                feedback.append("⚠️ Наклоняйтесь больше вперёд")
                score -= 20
            
            if not feedback:
                feedback.append("✅ Отличная техника становой тяги!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'back': round(back_angle, 1)},
                'exercise': 'Становая тяга'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_plank_frame(self, landmarks):
        """Анализ планки"""
        try:
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            body_angle = self.calculate_angle(left_shoulder, left_hip, left_ankle)
            
            feedback = []
            score = 100
            
            if body_angle < 160:
                feedback.append("⚠️ Опустите таз! Тело должно быть прямой линией")
                score -= 35
            elif body_angle > 180:
                feedback.append("⚠️ Поднимите таз! Не прогибайтесь")
                score -= 30
            
            if not feedback:
                feedback.append("✅ Отличная планка!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'body': round(body_angle, 1)},
                'exercise': 'Планка'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_pullup_frame(self, landmarks):
        """Анализ подтягиваний"""
        try:
            left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            
            feedback = []
            score = 100
            
            if elbow_angle > 120:
                feedback.append("⚠️ Подтянитесь выше! Локти должны сгибаться до 90°")
                score -= 30
            elif elbow_angle < 70:
                feedback.append("⚠️ Не опускайтесь до конца, сохраняйте напряжение")
                score -= 20
            
            if not feedback:
                feedback.append("✅ Отличные подтягивания!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'elbow': round(elbow_angle, 1)},
                'exercise': 'Подтягивания'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_dip_frame(self, landmarks):
        """Анализ отжиманий на брусьях"""
        try:
            left_shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                             landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            left_elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            left_wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            
            elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            
            feedback = []
            score = 100
            
            if elbow_angle > 100:
                feedback.append("⚠️ Опуститесь ниже! Локти должны быть под 90°")
                score -= 30
            elif elbow_angle < 70:
                feedback.append("⚠️ Слишком низко, не перенапрягайте плечи")
                score -= 20
            
            if not feedback:
                feedback.append("✅ Отличные отжимания на брусьях!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'elbow': round(elbow_angle, 1)},
                'exercise': 'Отжимания на брусьях'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_leg_raise_frame(self, landmarks):
        """Анализ подъёма ног"""
        try:
            left_hip = [landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].x,
                        landmarks[self.mp_pose.PoseLandmark.LEFT_HIP.value].y]
            left_knee = [landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_KNEE.value].y]
            left_ankle = [landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].x,
                          landmarks[self.mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
            
            leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            
            feedback = []
            score = 100
            
            if leg_angle < 90:
                feedback.append("⚠️ Поднимите ноги выше! Угол должен быть 90°")
                score -= 35
            elif leg_angle > 110:
                feedback.append("⚠️ Слишком высоко, не помогайте корпусом")
                score -= 20
            
            if not feedback:
                feedback.append("✅ Отличные подъёмы ног!")
            
            return {
                'score': max(0, score),
                'feedback': feedback,
                'angles': {'leg': round(leg_angle, 1)},
                'exercise': 'Подъём ног'
            }
        except Exception as e:
            return {'error': str(e), 'score': 0, 'feedback': ['Не удалось распознать позу']}
    
    def analyze_video(self, video_path, exercise_type='squat'):
        """Анализ видео с упражнением"""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        scores = []
        all_feedback = []
        last_angles = {}
        
        exercise = self.exercises.get(exercise_type, self.exercises['squat'])
        analyzer = exercise['analyze']
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # Анализируем каждый 10-й кадр
            if frame_count % 10 == 0:
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.pose.process(image_rgb)
                
                if results.pose_landmarks:
                    analysis = analyzer(results.pose_landmarks.landmark)
                    if 'score' in analysis:
                        scores.append(analysis['score'])
                        all_feedback.extend(analysis.get('feedback', []))
                        last_angles = analysis.get('angles', {})
        
        cap.release()
        
        if scores:
            avg_score = sum(scores) / len(scores)
            unique_feedback = list(dict.fromkeys(all_feedback))[:3]
            
            if avg_score >= 85:
                final_feedback = "✅ Отлично! Техника выполнения правильная!"
            elif avg_score >= 70:
                final_feedback = "⚠️ Хорошо, но есть небольшие ошибки."
            else:
                final_feedback = "🔴 Техника требует улучшения."
            
            return {
                'success': True,
                'avg_score': round(avg_score, 1),
                'feedback': unique_feedback if unique_feedback else [final_feedback],
                'angles': last_angles,
                'frames_analyzed': len(scores),
                'exercise_name': exercise['name']
            }
        
        return {'success': False, 'error': 'Не удалось распознать позу в видео'}
    def get_template_gif(self, exercise_type):
        """Возвращает путь к эталонному GIF для упражнения"""
        templates = {
            'squat': '/static/media/templates/squat_template.gif',
            'pushup': '/static/media/templates/pushup_template.gif',
            'lunge': '/static/media/templates/lunge_template.gif',
            'deadlift': '/static/media/templates/deadlift_template.gif',
            'plank': '/static/media/templates/plank_template.gif',
            'pullup': '/static/media/templates/pullup_template.gif',
            'dip': '/static/media/templates/dip_template.gif',
            'leg_raise': '/static/media/templates/leg_raise_template.gif'
        }
        return templates.get(exercise_type)
video_analyzer = VideoAnalyzer()