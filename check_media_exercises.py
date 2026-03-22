import os
import json
import shutil

# ========== КОНФИГУРАЦИЯ ==========
PROJECT_ROOT = r"C:\Users\zahov\Desktop\NSBodyScan_Own"
MEDIA_FOLDER = os.path.join(PROJECT_ROOT, "static", "media")
DATA_FOLDER = os.path.join(PROJECT_ROOT, "data")
EXERCISES_JSON = os.path.join(DATA_FOLDER, "exercises.json")

# Источник (внешний репозиторий)
SOURCE_EXERCISES = r"C:\Users\zahov\Desktop\exercisedb-api-main\src\data\exercises.json"

# ========== 1. ПРОВЕРКА И КОПИРОВАНИЕ exercises.json ==========
os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(EXERCISES_JSON):
    if os.path.exists(SOURCE_EXERCISES):
        shutil.copy2(SOURCE_EXERCISES, EXERCISES_JSON)
        print(f"✅ Файл скопирован: {EXERCISES_JSON}")
    else:
        print(f"❌ Ошибка: исходный файл не найден: {SOURCE_EXERCISES}")
        exit(1)
else:
    print(f"✅ Файл уже существует: {EXERCISES_JSON}")

# ========== 2. ЗАГРУЗКА БАЗЫ УПРАЖНЕНИЙ ==========
with open(EXERCISES_JSON, 'r', encoding='utf-8') as f:
    exercises = json.load(f)

print(f"📚 Загружено упражнений: {len(exercises)}")

# ========== 3. СКАНИРОВАНИЕ ПАПКИ С GIF ==========
if not os.path.exists(MEDIA_FOLDER):
    print(f"❌ Папка с медиа не найдена: {MEDIA_FOLDER}")
    exit(1)

gif_files = set(os.listdir(MEDIA_FOLDER))
print(f"🖼️  Найдено файлов в media: {len(gif_files)}")

# ========== 4. ПОИСК УПРАЖНЕНИЙ С МЕДИА ==========
exercises_with_media = []

for ex in exercises:
    # Получаем имя файла из gifUrl (например, "trmte8s.gif")
    gif_name = ex['gifUrl'].split('/')[-1]
    
    if gif_name in gif_files:
        exercises_with_media.append({
            'exerciseId': ex['exerciseId'],
            'name': ex['name'],
            'gifFile': gif_name,
            'targetMuscles': ex.get('targetMuscles', []),
            'equipments': ex.get('equipments', [])
        })

# ========== 5. ВЫВОД РЕЗУЛЬТАТОВ ==========
print("\n" + "="*50)
print(f"📊 ИТОГО УПРАЖНЕНИЙ С МЕДИА: {len(exercises_with_media)}")
print("="*50)

if exercises_with_media:
    print("\n📋 Первые 10 упражнений:")
    for i, ex in enumerate(exercises_with_media[:10], 1):
        print(f"  {i}. {ex['name']}")
        print(f"     ID: {ex['exerciseId']} → GIF: {ex['gifFile']}")
        print(f"     Мышцы: {', '.join(ex['targetMuscles'])}")
        print(f"     Инвентарь: {', '.join(ex['equipments'])}")
        print()
    
    if len(exercises_with_media) > 10:
        print(f"... и ещё {len(exercises_with_media) - 10} упражнений")
else:
    print("⚠️  Упражнения с медиа не найдены")
    print("\nПроверьте:")
    print("  - В папке media есть GIF-файлы?")
    print("  - Имена файлов совпадают с exerciseId (например, trmte8s.gif)?")
    print(f"  - Путь к media: {MEDIA_FOLDER}")