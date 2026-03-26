import imageio
import numpy as np
import os

def create_simple_gif(filename, text):
    """Создаёт простой анимированный GIF с текстом"""
    frames = []
    for i in range(30):  # 30 кадров
        # Создаём кадр (300x300)
        frame = np.ones((300, 300, 3), dtype=np.uint8) * 240  # светло-серый фон
        
        # Добавляем текст
        import cv2
        cv2.putText(frame, text, (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        # Добавляем движущуюся точку (анимация)
        x = 50 + i * 8
        cv2.circle(frame, (x, 200), 12, (255, 102, 181), -1)
        
        frames.append(frame)
    
    # Сохраняем GIF
    imageio.mimsave(filename, frames, fps=15, loop=0)
    print(f"✅ Создан: {filename}")

# Создаём папку
os.makedirs('static/media/templates', exist_ok=True)

# Создаём GIF для каждого упражнения
templates = [
    ('squat_template.gif', 'ПРИСЕДАНИЯ'),
    ('pushup_template.gif', 'ОТЖИМАНИЯ'),
    ('lunge_template.gif', 'ВЫПАДЫ'),
    ('deadlift_template.gif', 'СТАНОВАЯ ТЯГА'),
    ('plank_template.gif', 'ПЛАНКА'),
    ('pullup_template.gif', 'ПОДТЯГИВАНИЯ'),
    ('dip_template.gif', 'БРУСЬЯ'),
    ('leg_raise_template.gif', 'ПОДЪЁМ НОГ')
]

for filename, text in templates:
    create_simple_gif(f'static/media/templates/{filename}', text)

print("✅ Все эталонные GIF созданы!")