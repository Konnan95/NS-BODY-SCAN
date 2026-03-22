from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# Получаем структуру таблицы posture_analyses
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'posture_analyses'
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
print("=== Структура таблицы posture_analyses ===")
for i, col in enumerate(columns):
    print(f"{i}: {col[0]} ({col[1]})")

print("\n=== Структура таблицы body_composition ===")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'body_composition'
    ORDER BY ordinal_position
""")
columns = cur.fetchall()
for i, col in enumerate(columns):
    print(f"{i}: {col[0]} ({col[1]})")

# Покажем реальные данные для пользователя ID=2
print("\n=== РЕАЛЬНЫЕ ДАННЫЕ posture_analyses для user_id=2 ===")
cur.execute("SELECT * FROM posture_analyses WHERE user_id = 2 LIMIT 2")
rows = cur.fetchall()
for row in rows:
    print(f"Количество полей: {len(row)}")
    print(f"Данные: {row}")
    # Покажем каждое поле с индексом
    for i, value in enumerate(row):
        print(f"  [{i}] = {value}")

conn.close()