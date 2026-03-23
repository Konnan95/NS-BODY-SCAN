from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS user_activity_logs (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        action VARCHAR(100),
        page VARCHAR(100),
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()
print("✅ Таблица user_activity_logs создана")

# Проверим
cur.execute("SELECT COUNT(*) FROM user_activity_logs")
count = cur.fetchone()[0]
print(f"📊 Записей в таблице: {count}")

conn.close()