from database import get_db_connection

conn = get_db_connection()
cur = conn.cursor()

# Проверяем существование таблицы
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'daily_health'
    )
""")
exists = cur.fetchone()[0]

if exists:
    print("✅ Таблица daily_health существует")
    # Показываем структуру
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'daily_health'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print("\nСтруктура таблицы:")
    for col in columns:
        print(f"  - {col[0]} ({col[1]})")
else:
    print("❌ Таблица daily_health не найдена")
    print("Нужно создать таблицу")

conn.close()