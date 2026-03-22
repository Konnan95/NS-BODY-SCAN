"""
Генератор недельного меню
"""

import random

# База блюд с КБЖУ (примерные значения)
MEALS_DB = {
    'breakfast': [
        {'name': 'Омлет из 3 яиц с овощами', 'kcal': 350, 'protein': 25, 'fat': 20, 'carbs': 10},
        {'name': 'Овсяная каша на молоке с ягодами', 'kcal': 400, 'protein': 15, 'fat': 10, 'carbs': 60},
        {'name': 'Сырники из обезжиренного творога', 'kcal': 380, 'protein': 28, 'fat': 12, 'carbs': 45},
        {'name': 'Рисовая каша с яблоком и корицей', 'kcal': 320, 'protein': 8, 'fat': 5, 'carbs': 65},
        {'name': 'Греческий йогурт с орехами и медом', 'kcal': 300, 'protein': 20, 'fat': 12, 'carbs': 25}
    ],
    'lunch': [
        {'name': 'Куриная грудка запеченная + гречка + овощи', 'kcal': 550, 'protein': 45, 'fat': 15, 'carbs': 55},
        {'name': 'Рыба на пару + рис + салат из свежих овощей', 'kcal': 520, 'protein': 40, 'fat': 12, 'carbs': 60},
        {'name': 'Говядина/индейка + картофель запеченный + овощи', 'kcal': 580, 'protein': 42, 'fat': 18, 'carbs': 50},
        {'name': 'Чечевичный суп + цельнозерновой хлеб + салат', 'kcal': 480, 'protein': 25, 'fat': 10, 'carbs': 70},
        {'name': 'Тунец с киноа и авокадо', 'kcal': 530, 'protein': 38, 'fat': 22, 'carbs': 45}
    ],
    'dinner': [
        {'name': 'Творог с зеленью + овощной салат', 'kcal': 320, 'protein': 30, 'fat': 12, 'carbs': 20},
        {'name': 'Омлет с овощами и сыром', 'kcal': 380, 'protein': 28, 'fat': 22, 'carbs': 15},
        {'name': 'Рыба запеченная + овощи-гриль', 'kcal': 400, 'protein': 35, 'fat': 18, 'carbs': 20},
        {'name': 'Салат с тунцом, авокадо и листовыми овощами', 'kcal': 450, 'protein': 32, 'fat': 28, 'carbs': 18},
        {'name': 'Куриное филе на пару + цветная капуста', 'kcal': 340, 'protein': 38, 'fat': 8, 'carbs': 25}
    ],
    'snack': [
        {'name': 'Яблоко + горсть орехов', 'kcal': 200, 'protein': 5, 'fat': 12, 'carbs': 20},
        {'name': 'Стакан кефира/йогурта', 'kcal': 120, 'protein': 8, 'fat': 4, 'carbs': 12},
        {'name': 'Морковь/сельдерей с хумусом', 'kcal': 150, 'protein': 4, 'fat': 8, 'carbs': 15},
        {'name': 'Банан + немного арахисовой пасты', 'kcal': 250, 'protein': 6, 'fat': 10, 'carbs': 35},
        {'name': 'Протеиновый батончик', 'kcal': 180, 'protein': 15, 'fat': 6, 'carbs': 20}
    ]
}

def generate_meal_plan(calories_goal, goal_type='tone'):
    """
    Генерация недельного меню на основе калорийности
    
    calories_goal: целевая калорийность в день
    goal_type: lose / gain / tone / posture
    """
    
    # Корректируем калорийность под цель
    if goal_type == 'lose':
        calories_goal -= 50
    elif goal_type == 'gain':
        calories_goal += 100
    
    # Случайно выбираем блюда на неделю
    weekly_menu = {}
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    
    for i, day in enumerate(days):
        breakfast = random.choice(MEALS_DB['breakfast'])
        lunch = random.choice(MEALS_DB['lunch'])
        dinner = random.choice(MEALS_DB['dinner'])
        snack = random.choice(MEALS_DB['snack'])
        
        total_kcal = breakfast['kcal'] + lunch['kcal'] + dinner['kcal'] + snack['kcal']
        
        weekly_menu[day] = {
            'name': day_names[i],
            'breakfast': breakfast,
            'lunch': lunch,
            'dinner': dinner,
            'snack': snack,
            'total_kcal': total_kcal,
            'target_kcal': calories_goal
        }
    
    return weekly_menu

def format_meal_plan_html(meal_plan):
    """Форматирует меню в HTML для вывода на странице"""
    
    html = '<h3>🥗 Примерное меню на неделю</h3>'
    
    for day, data in meal_plan.items():
        html += f'''
        <div class="meal-day">
            <h4>{data['name']}</h4>
            <p><strong>🥣 Завтрак:</strong> {data['breakfast']['name']} ({data['breakfast']['kcal']} ккал)</p>
            <p><strong>🍲 Обед:</strong> {data['lunch']['name']} ({data['lunch']['kcal']} ккал)</p>
            <p><strong>🍽️ Ужин:</strong> {data['dinner']['name']} ({data['dinner']['kcal']} ккал)</p>
            <p><strong>🍎 Перекус:</strong> {data['snack']['name']} ({data['snack']['kcal']} ккал)</p>
            <p><em>📊 Итого: {data['total_kcal']} / {data['target_kcal']} ккал</em></p>
        </div>
        <hr>
        '''
    
    return html

def get_random_meal(meal_type):
    """Возвращает случайное блюдо из указанной категории"""
    if meal_type in MEALS_DB:
        return random.choice(MEALS_DB[meal_type])
    return None