"""Views/контролери для обробки запитів у Flask."""

from flask import Flask, request, jsonify, abort
from functools import wraps

app = Flask(__name__)

items_db = {
    1: {"id": 1, "name": "Ноутбук", "price": 25000, "category": "електроніка"},
    2: {"id": 2, "name": "Книга Python", "price": 500, "category": "книги"},
    3: {"id": 3, "name": "Навушники", "price": 2000, "category": "електроніка"},
}
next_id = 4


def validate_json(required_fields):
    """Декоратор для валідації JSON-запитів."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)

            if data is None:
                return jsonify({"error": "Очікується JSON"}), 400

            missing = [field for field in required_fields if field not in data]
            if missing:
                return jsonify({
                    "error": f"Відсутні поля: {', '.join(missing)}"
                }), 400

            return f(*args, **kwargs)
        return wrapper
    return decorator


def find_item_or_404(item_id: int) -> dict:
    """Пошук елемента або помилка 404."""
    item = items_db.get(item_id)
    if item is None:
        abort(404)
    return item


def validate_item_data(data: dict):
    """Перевірити коректність даних елемента."""
    name = str(data.get("name", "")).strip()
    category = str(data.get("category", "")).strip()

    try:
        price = float(data.get("price"))
    except (TypeError, ValueError):
        return None, "Ціна має бути числом"

    if not name:
        return None, "Назва не може бути порожньою"
    if not category:
        return None, "Категорія не може бути порожньою"
    if price <= 0:
        return None, "Ціна має бути більшою за 0"

    return {"name": name, "price": price, "category": category}, None


@app.route("/api/items", methods=["GET"])
def get_items():
    """GET /api/items — список елементів з фільтрацією та сортуванням."""
    category = request.args.get("category", type=str)
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", default="id", type=str)
    order = request.args.get("order", default="asc", type=str)

    allowed_sort_fields = {"id", "name", "price", "category"}
    if sort not in allowed_sort_fields:
        return jsonify({"error": f"Сортування за полем '{sort}' не підтримується"}), 400

    if order not in {"asc", "desc"}:
        return jsonify({"error": "Параметр order має бути asc або desc"}), 400

    items = list(items_db.values())

    if category:
        items = [item for item in items if item["category"].lower() == category.lower()]
    if min_price is not None:
        items = [item for item in items if item["price"] >= min_price]
    if max_price is not None:
        items = [item for item in items if item["price"] <= max_price]

    reverse = order == "desc"
    items.sort(key=lambda item: item[sort], reverse=reverse)

    return jsonify({
        "count": len(items),
        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
        },
        "sort": sort,
        "order": order,
        "items": items,
    }), 200


@app.route("/api/items", methods=["POST"])
@validate_json(["name", "price", "category"])
def create_item():
    """POST /api/items — створити елемент з валідацією."""
    global next_id

    data = request.get_json()
    cleaned, error = validate_item_data(data)
    if error:
        return jsonify({"error": error}), 400

    item = {"id": next_id, **cleaned}
    items_db[next_id] = item
    next_id += 1

    return jsonify(item), 201


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """GET /api/items/:id — отримати деталі елемента."""
    return jsonify(find_item_or_404(item_id)), 200


@app.route("/api/items/<int:item_id>", methods=["PUT"])
@validate_json(["name", "price", "category"])
def update_item(item_id):
    """PUT /api/items/:id — оновити елемент повністю."""
    item = find_item_or_404(item_id)

    data = request.get_json()
    cleaned, error = validate_item_data(data)
    if error:
        return jsonify({"error": error}), 400

    item.update(cleaned)
    return jsonify(item), 200


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """DELETE /api/items/:id — видалити елемент."""
    find_item_or_404(item_id)
    del items_db[item_id]
    return "", 204


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не знайдено"}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Некоректний запит"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=5001)
