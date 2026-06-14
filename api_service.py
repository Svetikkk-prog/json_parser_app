from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE_PATH = 'data.json'

def load_data():
    """Загружает данные из JSON-файла. Если файла нет, возвращает пустой список."""
    if not os.path.exists(JSON_FILE_PATH):
        return []
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Сохраняет список данных в JSON-файл."""
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/items', methods=['GET'])
def get_all_items():
    """Вернуть все товары."""
    data = load_data()
    return jsonify(data), 200

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Вернуть один товар по id."""
    data = load_data()
    item = next((i for i in data if i['id'] == item_id), None)
    if item:
        return jsonify(item), 200
    return jsonify({'error': 'Item not found'}), 404

@app.route('/items', methods=['POST'])
def create_item():
    """Создать новый товар."""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    new_item_data = request.get_json()
    # Проверка обязательных полей
    required = ['name', 'description', 'price']
    for field in required:
        if field not in new_item_data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Проверка типа price
    try:
        new_item_data['price'] = float(new_item_data['price'])
    except (TypeError, ValueError):
        return jsonify({'error': 'Price must be a number'}), 400

    data = load_data()
    # Генерация нового ID
    new_id = max([item['id'] for item in data], default=0) + 1
    new_item = {
        'id': new_id,
        'name': new_item_data['name'],
        'description': new_item_data['description'],
        'price': new_item_data['price']
    }
    data.append(new_item)
    save_data(data)
    return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """Обновить существующий товар."""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    update_data = request.get_json()
    data = load_data()
    # Поиск индекса элемента
    index = None
    for i, item in enumerate(data):
        if item['id'] == item_id:
            index = i
            break
    if index is None:
        return jsonify({'error': 'Item not found'}), 404

    # Обновляем только переданные поля
    if 'name' in update_data:
        data[index]['name'] = update_data['name']
    if 'description' in update_data:
        data[index]['description'] = update_data['description']
    if 'price' in update_data:
        try:
            data[index]['price'] = float(update_data['price'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Price must be a number'}), 400

    save_data(data)
    return jsonify(data[index]), 200

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    """Удалить товар."""
    data = load_data()
    new_data = [item for item in data if item['id'] != item_id]
    if len(new_data) == len(data):
        return jsonify({'error': 'Item not found'}), 404
    save_data(new_data)
    return '', 204

if __name__ == '__main__':
    # Убедимся, что файл data.json существует и содержит хотя бы пустой массив
    if not os.path.exists(JSON_FILE_PATH):
        save_data([])
    app.run(debug=True, port=5000)