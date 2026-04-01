"""
Модели базы данных SQLAlchemy
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from config import DB_CONFIG

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    name = Column(String(100))
    age = Column(Integer)
    height = Column(Float)
    weight = Column(Float)
    goal = Column(String(50))
    activity = Column(Float)
    role = Column(String(20), default='user')
    subscription = Column(String(50), default='free')
    created_at = Column(DateTime, default=datetime.now)
    
    # Антропометрические данные
    neck = Column(Float)
    chest = Column(Float)
    waist = Column(Float)
    hip = Column(Float)
    thigh = Column(Float)
    knee = Column(Float)
    ankle = Column(Float)
    biceps = Column(Float)
    forearm = Column(Float)
    wrist = Column(Float)
    
    # Данные тренера
    specialization = Column(String(200))
    experience = Column(String(50))
    about = Column(Text)
    certifications = Column(Text)
    price_per_hour = Column(String(50))
    
    # Связи
    posture_analyses = relationship("PostureAnalysis", back_populates="user")
    body_compositions = relationship("BodyComposition", back_populates="user")
    daily_health = relationship("DailyHealth", back_populates="user")
    workout_programs = relationship("WorkoutProgram", back_populates="user")
    meal_plans = relationship("MealPlan", back_populates="user")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")

class PostureAnalysis(Base):
    __tablename__ = 'posture_analyses'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    shoulder_slope = Column(Float)
    hip_slope = Column(Float)
    head_tilt = Column(Float)
    kyphosis = Column(Float)
    neck_angle = Column(Float)
    knee_valgus = Column(Float)
    symmetry = Column(Float)
    posture_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    
    # Фото
    original_photo_path = Column(String(500))
    analyzed_photo_path = Column(String(500))
    front_photo_path = Column(String(500))
    side_photo_path = Column(String(500))
    
    user = relationship("User", back_populates="posture_analyses")

class BodyComposition(Base):
    __tablename__ = 'body_composition'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    body_fat = Column(Float)
    muscle_mass = Column(Float)
    water = Column(Float)
    visceral_fat = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="body_compositions")

class DailyHealth(Base):
    __tablename__ = 'daily_health'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    date = Column(Date, default=datetime.now)
    steps = Column(Integer)
    sleep_hours = Column(Float)
    weight = Column(Float)
    
    user = relationship("User", back_populates="daily_health")

class WorkoutProgram(Base):
    __tablename__ = 'workout_programs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    program_data = Column(Text)
    version = Column(Integer, default=1)
    days_per_week = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="workout_programs")

class MealPlan(Base):
    __tablename__ = 'meal_plans'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    plan_data = Column(Text)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="meal_plans")

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")