"""
Голосовой AI-тренер (gTTS - Google Text-to-Speech)
"""

from gtts import gTTS
import os
import uuid
from flask import send_file

class VoiceTrainer:
    def __init__(self):
        self.temp_dir = 'static/audio'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def speak(self, text, lang='ru'):
        """
        Создаёт аудиофайл с озвучкой текста
        Возвращает путь к файлу
        """
        try:
            filename = f"{uuid.uuid4().hex}.mp3"
            filepath = os.path.join(self.temp_dir, filename)
            
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filepath)
            
            return f'/static/audio/{filename}'
        except Exception as e:
            print(f"⚠️ Ошибка озвучивания: {e}")
            return None
    
    def speak_sync(self, text, lang='ru'):
        """Создаёт и возвращает URL аудиофайла"""
        return self.speak(text, lang)

# Глобальный экземпляр
voice_trainer = VoiceTrainer()