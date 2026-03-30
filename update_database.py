"""
Обновление базы данных NS Body Scan
Добавляет недостающие поля и таблицы
"""

from database import get_db_connection

def update_database():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 50)
    print("Обновление базы данных NS Body Scan")
    print("=" * 50)
    
    # ========== 1. Добавляем поля для тренера (если нет) ==========
    print("\n📌 Добавляем поля для тренера...")
    trainer_fields = [
        'specialization', 'experience', 'about', 'certifications', 'price_per_hour'
    ]
    for field in trainer_fields:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {field} TEXT")
            print(f"   ✅ {field}")
        except Exception as e:
            print(f"   ⚠️ {field}: {e}")
    
    # ========== 2. Добавляем антропометрические поля (если нет) ==========
    print("\n📌 Добавляем антропометрические поля...")
    anthrop_fields = ['neck', 'chest', 'waist', 'hip', 'thigh', 'knee', 'ankle', 'biceps', 'forearm', 'wrist']
    for field in anthrop_fields:
        try:
            cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {field} FLOAT")
            print(f"   ✅ {field}")
        except Exception as e:
            print(f"   ⚠️ {field}: {e}")
    
    # ========== 3. Создаём таблицу trainer_clients ==========
    print("\n📌 Создаём таблицу trainer_clients...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trainer_clients (
            id SERIAL PRIMARY KEY,
            trainer_id INTEGER REFERENCES users(id),
            client_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(trainer_id, client_id)
        )
    """)
    print("   ✅ trainer_clients")
    
    # ========== 4. Создаём таблицу reviews ==========
    print("\n📌 Создаём таблицу reviews...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            client_id INTEGER REFERENCES users(id),
            trainer_id INTEGER REFERENCES users(id),
            rating INTEGER CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ reviews")
    
    # ========== 5. Создаём таблицу trainer_earnings ==========
    print("\n📌 Создаём таблицу trainer_earnings...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trainer_earnings (
            id SERIAL PRIMARY KEY,
            trainer_id INTEGER REFERENCES users(id),
            amount DECIMAL(10,2),
            commission DECIMAL(10,2),
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ trainer_earnings")
    
    # ========== 6. Создаём таблицу achievements ==========
    print("\n📌 Создаём таблицу achievements...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            achievement_type VARCHAR(50),
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, achievement_type)
        )
    """)
    print("   ✅ achievements")
    
    # ========== 7. Создаём таблицу exercise_analyses ==========
    print("\n📌 Создаём таблицу exercise_analyses...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercise_analyses (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            exercise_type VARCHAR(50),
            score INTEGER,
            feedback TEXT,
            angles JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ exercise_analyses")
    
    # ========== 8. Добавляем индексы для ускорения ==========
    print("\n📌 Добавляем индексы...")
    indices = [
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
        "CREATE INDEX IF NOT EXISTS idx_posture_user_id ON posture_analyses(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_composition_user_id ON body_composition(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_daily_health_user_date ON daily_health(user_id, date)",
        "CREATE INDEX IF NOT EXISTS idx_workout_programs_user_active ON workout_programs(user_id, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_trainer_clients_trainer ON trainer_clients(trainer_id)",
        "CREATE INDEX IF NOT EXISTS idx_reviews_trainer ON reviews(trainer_id)",
    ]
    for idx in indices:
        try:
            cur.execute(idx)
            print(f"   ✅ {idx.split('ON')[1].strip() if 'ON' in idx else idx}")
        except Exception as e:
            print(f"   ⚠️ {idx[:50]}: {e}")
    
    conn.commit()
    print("\n" + "=" * 50)
    print("✅ Обновление базы данных завершено!")
    print("=" * 50)
    
    conn.close()

if __name__ == '__main__':
    update_database()