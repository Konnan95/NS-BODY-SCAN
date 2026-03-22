import os
import sys

sys.path.insert(0, r"C:\Users\zahov\Desktop\NSBodyScan_Own")

from exercise_manager import exercise_manager

stats = exercise_manager.get_statistics()
print("=" * 60)
print("СТАТИСТИКА ПО УПРАЖНЕНИЯМ")
print("=" * 60)
print(f"Всего упражнений в базе: {stats['total_exercises']}")
print(f"Упражнений с GIF: {stats['exercises_with_media']}")
print(f"GIF-файлов в папке: {stats['media_folder_size']}")
print(f"Уникальных мышц: {stats['unique_muscles']}")
print(f"Уникальных частей тела: {stats['unique_body_parts']}")
print(f"Уникального инвентаря: {stats['unique_equipment']}")

print("\nЦЕЛЕВЫЕ МЫШЦЫ (первые 10):")
for muscle in stats['muscles_list'][:10]:
    print(f"  - {muscle}")

print("\nЧАСТИ ТЕЛА:")
for part in stats['body_parts_list']:
    print(f"  - {part}")

print("\nИНВЕНТАРЬ:")
for eq in stats['equipment_list'][:15]:
    print(f"  - {eq}")

print("\n" + "=" * 60)
print("ПРИМЕРЫ ФИЛЬТРАЦИИ")
print("=" * 60)

biceps_exercises = exercise_manager.filter_by_muscles(["biceps"])
print(f"\nУпражнения для бицепса: {len(biceps_exercises)}")
for ex in biceps_exercises[:5]:
    print(f"  - {ex['name']}")

dumbbell_exercises = exercise_manager.filter_by_equipment(["dumbbell"])
print(f"\nУпражнения с гантелями: {len(dumbbell_exercises)}")
for ex in dumbbell_exercises[:5]:
    print(f"  - {ex['name']}")

search_results = exercise_manager.search("push up")
print(f"\nПоиск push up: {len(search_results)} упражнений")
for ex in search_results[:5]:
    print(f"  - {ex['name']}")

print("\nГенерация упрощённого JSON...")
output_file = exercise_manager.generate_media_json()
print(f"Создан файл: {output_file}")