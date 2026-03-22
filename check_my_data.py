from database import get_db_connection

# Получаем список пользователей
conn = get_db_connection()
cur = conn.cursor()

print("=== ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ ===")
cur.execute("SELECT id, username, name FROM users")
users = cur.fetchall()
for u in users:
    print(f"ID: {u[0]}, Username: {u[1]}, Name: {u[2]}")

# Проверяем каждого пользователя
for u in users:
    user_id = u[0]
    print(f"\n=== ПОЛЬЗОВАТЕЛЬ ID={user_id} ===")
    
    # Проверяем анализы осанки
    cur.execute("SELECT COUNT(*) FROM posture_analyses WHERE user_id = %s", (user_id,))
    posture_count = cur.fetchone()[0]
    print(f"Анализов осанки: {posture_count}")
    
    if posture_count > 0:
        cur.execute("SELECT * FROM posture_analyses WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            print(f"  - ID:{row[0]}, score:{row[5]}, date:{row[7]}")
    
    # Проверяем анализы состава тела
    cur.execute("SELECT COUNT(*) FROM body_composition WHERE user_id = %s", (user_id,))
    comp_count = cur.fetchone()[0]
    print(f"Анализов состава тела: {comp_count}")
    
    if comp_count > 0:
        cur.execute("SELECT * FROM body_composition WHERE user_id = %s", (user_id,))
        rows = cur.fetchall()
        for row in rows:
            print(f"  - ID:{row[0]}, fat:{row[2]}%, date:{row[6]}")

conn.close()