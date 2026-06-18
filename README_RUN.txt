"""REST API: серіалізація, фільтрація, обробка помилок."""

from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import time

app = Flask(__name__)

students_db = {}
next_id = 1


class APIError(Exception):
    """Базове виключення API."""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class StudentSerializer:
    """Серіалізатор для перетворення даних студента."""

    @staticmethod
    def serialize(student: dict, fields: list[str] | None = None) -> dict:
        """Серіалізувати студента та за потреби вибрати лише потрібні поля."""
        created_at = student.get("created_at")

        result = {
            "id": student.get("id"),
            "name": student.get("name"),
            "group": student.get("group"),
            "email": student.get("email"),
            "gpa": student.get("gpa"),
            "created_at": created_at,
            "created_date": created_at[:10] if created_at else None,
            "academic_status": "успішно" if float(student.get("gpa", 0)) >= 60 else "неуспішно",
        }

        if fields:
            return {field: result[field] for field in fields if field in result}

        return result

    @staticmethod
    def deserialize(data: dict) -> dict:
        """Десеріалізувати вхідні дані з валідацією."""
        if not isinstance(data, dict):
            raise APIError("Очікується JSON-об'єкт", 400)

        errors = {}

        name = str(data.get("name", "")).strip()
        group = str(data.get("group", "")).strip()
        email = str(data.get("email", "")).strip().lower()

        if not name:
            errors["name"] = "Поле name обов'язкове"
        if not group:
            errors["group"] = "Поле group обов'язкове"
        if not email:
            errors["email"] = "Поле email обов'язкове"
        elif "@" not in email:
            errors["email"] = "Некоректний email"

        try:
            gpa = float(data.get("gpa"))
            if not 0 <= gpa <= 100:
                errors["gpa"] = "GPA має бути у діапазоні 0-100"
        except (TypeError, ValueError):
            errors["gpa"] = "GPA має бути числом"

        if errors:
            raise APIError("Помилка валідації", 422, errors)

        return {
            "name": name,
            "group": group,
            "email": email,
            "gpa": gpa,
        }

    @staticmethod
    def serialize_list(students: list[dict], fields: list[str] | None = None) -> list[dict]:
        """Серіалізувати список студентів."""
        return [StudentSerializer.serialize(student, fields) for student in students]


@app.before_request
def log_request():
    """Логувати кожен вхідний запит."""
    request.start_time = time.time()
    print(f"[{datetime.now().isoformat(timespec='seconds')}] {request.method} {request.url}")


@app.after_request
def add_headers(response):
    """Додати заголовки до кожної відповіді."""
    duration = time.time() - getattr(request, "start_time", time.time())

    response.headers["X-Request-Time"] = f"{duration:.4f}s"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-API-Key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"

    return response


def require_api_key(f):
    """Перевірка API-ключа у заголовку X-API-Key."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if api_key != "secret-api-key-123":
            return jsonify({"error": "Невірний API-ключ"}), 401

        return f(*args, **kwargs)
    return wrapper


@app.route("/api/v2/students", methods=["GET"])
def get_students_v2():
    """GET /api/v2/students — з серіалізацією, вибором полів та пошуком."""
    fields_param = request.args.get("fields", "")
    search = request.args.get("search", "").strip().lower()
    sort = request.args.get("sort", default="id", type=str)
    order = request.args.get("order", default="asc", type=str)

    fields = [field.strip() for field in fields_param.split(",") if field.strip()] or None

    allowed_sort_fields = {"id", "name", "group", "email", "gpa", "created_at"}
    if sort not in allowed_sort_fields:
        raise APIError("Некоректне поле сортування", 400, {"allowed": sorted(allowed_sort_fields)})

    if order not in {"asc", "desc"}:
        raise APIError("Некоректний напрямок сортування", 400, {"allowed": ["asc", "desc"]})

    students = list(students_db.values())

    if search:
        students = [
            student for student in students
            if search in student["name"].lower()
            or search in student["group"].lower()
            or search in student["email"].lower()
        ]

    students.sort(key=lambda student: student[sort], reverse=(order == "desc"))

    return jsonify({
        "count": len(students),
        "students": StudentSerializer.serialize_list(students, fields),
    }), 200


@app.route("/api/v2/students", methods=["POST"])
@require_api_key
def create_student_v2():
    """POST /api/v2/students — з серіалізацією та авторизацією."""
    global next_id

    data = request.get_json(silent=True)
    if data is None:
        raise APIError("Очікується JSON", 400)

    cleaned = StudentSerializer.deserialize(data)

    email_is_used = any(
        student["email"].lower() == cleaned["email"].lower()
        for student in students_db.values()
    )
    if email_is_used:
        raise APIError("Email вже використовується", 409, {"email": cleaned["email"]})

    student = {
        **cleaned,
        "id": next_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    students_db[next_id] = student
    next_id += 1

    return jsonify(StudentSerializer.serialize(student)), 201


@app.errorhandler(APIError)
def handle_api_error(error):
    """Централізована обробка помилок API."""
    response = {
        "error": error.message,
        "status": error.status_code,
        "details": error.details,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    return jsonify(response), error.status_code


@app.errorhandler(404)
def not_found(error):
    """Єдина відповідь для 404."""
    response = {
        "error": "Ресурс не знайдено",
        "status": 404,
        "details": {},
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    return jsonify(response), 404


def seed_students():
    """Тестові дані для перевірки API."""
    global next_id

    test_students = [
        {"name": "Іваненко О.", "group": "КІ-21", "email": "ivan@kpi.ua", "gpa": 85.5},
        {"name": "Петренко М.", "group": "КІ-21", "email": "petro@kpi.ua", "gpa": 92.0},
        {"name": "Сидоренко А.", "group": "КІ-22", "email": "syd@kpi.ua", "gpa": 78.3},
        {"name": "Коваль Л.", "group": "КІ-22", "email": "koval@kpi.ua", "gpa": 95.1},
    ]

    for student in test_students:
        students_db[next_id] = {
            **student,
            "id": next_id,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }
        next_id += 1


if __name__ == "__main__":
    seed_students()
    app.run(debug=True, port=5006)
