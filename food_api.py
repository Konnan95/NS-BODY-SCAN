"""
Food API - демо-режим (без реального API)
"""

class FoodAPI:
    def __init__(self):
        pass
    
    def search_food(self, query, limit=20):
        """Поиск продуктов (демо-режим)"""
        # Демо-продукты
        demo_products = {
            'курица': [
                {'name': 'Куриная грудка отварная', 'calories': 165, 'protein': 31, 'fat': 3.6, 'carbs': 0},
                {'name': 'Куриное филе жареное', 'calories': 220, 'protein': 30, 'fat': 11, 'carbs': 0},
                {'name': 'Курица целиком запечённая', 'calories': 239, 'protein': 27, 'fat': 14, 'carbs': 0},
            ],
            'рис': [
                {'name': 'Рис отварной белый', 'calories': 130, 'protein': 2.7, 'fat': 0.3, 'carbs': 28},
                {'name': 'Рис бурый отварной', 'calories': 123, 'protein': 2.7, 'fat': 1, 'carbs': 25},
            ],
            'гречка': [
                {'name': 'Гречка отварная', 'calories': 132, 'protein': 4.5, 'fat': 2.3, 'carbs': 25},
            ],
            'яйцо': [
                {'name': 'Яйцо куриное варёное', 'calories': 155, 'protein': 12.6, 'fat': 10.6, 'carbs': 0.6},
            ],
            'творог': [
                {'name': 'Творог 5%', 'calories': 121, 'protein': 17, 'fat': 5, 'carbs': 1.5},
            ],
            'овсянка': [
                {'name': 'Овсянка на воде', 'calories': 88, 'protein': 3, 'fat': 1.7, 'carbs': 15},
            ],
            'банан': [
                {'name': 'Банан', 'calories': 89, 'protein': 1.1, 'fat': 0.3, 'carbs': 22.8},
            ],
            'яблоко': [
                {'name': 'Яблоко', 'calories': 52, 'protein': 0.3, 'fat': 0.2, 'carbs': 13.8},
            ]
        }
        
        query_lower = query.lower()
        results = []
        
        for key, products in demo_products.items():
            if key in query_lower or query_lower in key:
                for p in products:
                    results.append({
                        'id': f"demo_{key}",
                        'name': p['name'],
                        'brand': 'Демо',
                        'calories': p['calories'],
                        'protein': p['protein'],
                        'fat': p['fat'],
                        'carbs': p['carbs'],
                        'image': ''
                    })
        
        # Если нет совпадений
        if not results:
            results = [
                {'id': 'demo_1', 'name': f'{query} (демо)', 'brand': 'Демо', 
                 'calories': 100, 'protein': 10, 'fat': 5, 'carbs': 10, 'image': ''}
            ]
        
        print(f"🔍 Поиск: {query} -> найдено {len(results)} продуктов (демо)")
        return results[:limit]
    
    def get_food_details(self, food_id):
        """Получить детали продукта (демо)"""
        return None
    
    def get_product_by_barcode(self, barcode):
        """Поиск по штрихкоду (демо)"""
        return None

food_api = FoodAPI()