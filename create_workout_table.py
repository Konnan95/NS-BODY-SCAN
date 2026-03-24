from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS workout_programs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
        program_data TEXT NOT NULL,
        version INTEGER DEFAULT 1,
        days_per_week INTEGER DEFAULT 3,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )
""")
conn.commit()
print("✅ Таблица workout_programs создана")
conn.close()