from flask import Blueprint, jsonify, request
from exercise_manager import exercise_manager

# Создаём Blueprint для упражнений
exercises_bp = Blueprint('exercises', __name__, url_prefix='/api/exercises')


@exercises_bp.route('', methods=['GET'])
def get_exercises():
    """Получить все упражнения с медиа"""
    limit = request.args.get('limit', default=1500, type=int)  # Изменили с 100 на 1500
    exercises = exercise_manager.get_all_with_media()
    
    if limit and limit > 0:
        exercises = exercises[:limit]
    
    return jsonify({
        'total': len(exercise_manager.get_all_with_media()),
        'count': len(exercises),
        'exercises': exercises
    })

@exercises_bp.route('/<exercise_id>', methods=['GET'])
def get_exercise(exercise_id):
    """Получить упражнение по ID"""
    exercise = exercise_manager.get_by_id(exercise_id)
    if exercise:
        return jsonify(exercise)
    return jsonify({'error': 'Exercise not found'}), 404


@exercises_bp.route('/filter', methods=['POST'])
def filter_exercises():
    """Фильтрация упражнений"""
    data = request.json
    
    muscles = data.get('muscles', [])
    body_parts = data.get('bodyParts', [])
    equipment = data.get('equipment', [])
    search_query = data.get('search', '')
    
    result = set(exercise_manager.get_all_with_media())
    
    if muscles:
        result &= set(exercise_manager.filter_by_muscles(muscles))
    if body_parts:
        result &= set(exercise_manager.filter_by_body_parts(body_parts))
    if equipment:
        result &= set(exercise_manager.filter_by_equipment(equipment))
    if search_query:
        result &= set(exercise_manager.search(search_query))
    
    return jsonify({
        'count': len(result),
        'exercises': list(result)
    })


@exercises_bp.route('/stats', methods=['GET'])
def get_stats():
    """Получить статистику"""
    return jsonify(exercise_manager.get_statistics())


@exercises_bp.route('/muscles', methods=['GET'])
def get_muscles():
    """Получить список всех мышц"""
    stats = exercise_manager.get_statistics()
    return jsonify({
        'count': len(stats['muscles_list']),
        'muscles': stats['muscles_list']
    })


@exercises_bp.route('/body-parts', methods=['GET'])
def get_body_parts():
    """Получить список всех частей тела"""
    stats = exercise_manager.get_statistics()
    return jsonify({
        'count': len(stats['body_parts_list']),
        'bodyParts': stats['body_parts_list']
    })


@exercises_bp.route('/equipment', methods=['GET'])
def get_equipment():
    """Получить список всего инвентаря"""
    stats = exercise_manager.get_statistics()
    return jsonify({
        'count': len(stats['equipment_list']),
        'equipment': stats['equipment_list']
    })