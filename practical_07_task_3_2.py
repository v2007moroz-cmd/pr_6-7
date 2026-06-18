"""REST API для ресурсу 'Студент'."""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

students_db = {}
next_id = 1


def find_student_or_none(student_id: int):
    """Повернути студента за id або None."""
    return students_db.get(student_id)


def validate_student_data(data: dict, partial: bool = False, current_id: int | None = None):
    """Валідація даних студента.

    partial=False — перевіряються всі поля для POST/PUT.
    partial=True — перевіряються лише передані поля для PATCH.
    """
    errors = {}
    cleaned = {}

    required_fields = ["name", "group", "email", "gpa"]
    if not partial:
        for field in required_fields:
            if field not in data:
                errors[field] = "Поле обов'язкове"

    if "name" in data or not partial:
        name = str(data.get("name", "")).strip()
        if not name:
            errors["name"] = "Ім'я не може бути порожнім"
        else:
            cleaned["name"] = name

    if "group" in data or not partial:
        group = str(data.get("group", "")).strip()
        if not group:
            errors["group"] = "Група не може бути порожньою"
        else:
            cleaned["group"] = group

    if "email" in data or not partial:
        email = str(data.get("email", "")).strip().lower()
        if not email:
            errors["email"] = "Email не може бути порожнім"
        elif "@" not in email:
            errors["email"] = "Некоректний email"
        else:
            email_is_used = any(
                student["email"].lower() == email and student["id"] != current_id
                for student in students_db.values()
            )
            if email_is_used:
                errors["email"] = "Email вже використовується"
            else:
                cleaned["email"] = email

    if "gpa" in data or not partial:
        try:
            gpa = float(data.get("gpa"))
            if not 0 <= gpa <= 100:
                errors["gpa"] = "GPA має бути у діапазоні 0-100"
            else:
                cleaned["gpa"] = gpa
        except (TypeError, ValueError):
            errors["gpa"] = "GPA має бути числом"

    return cleaned, errors


@app.route("/api/students", methods=["GET"])
def get_students():
    """GET /api/students — список усіх студентів з фільтрацією, сортуванням і пагінацією."""
    group = request.args.get("group", type=str)
    min_gpa = request.args.get("min_gpa", type=float)
    sort_by = request.args.get("sort_by", default="id", type=str)
    order = request.args.get("order", default="asc", type=str)
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    allowed_sort_fields = {"id", "name", "gpa", "group", "email", "created_at"}
    if sort_by not in allowed_sort_fields:
        return jsonify({"error": f"Сортування за полем '{sort_by}' не підтримується"}), 400

    if order not in {"asc", "desc"}:
        return jsonify({"error": "order має бути asc або desc"}), 400

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    students = list(students_db.values())

    if group:
        students = [student for student in students if student["group"].lower() == group.lower()]
    if min_gpa is not None:
        students = [student for student in students if student["gpa"] >= min_gpa]

    students.sort(key=lambda student: student[sort_by], reverse=(order == "desc"))

    count = len(students)
    start = (page - 1) * per_page
    end = start + per_page

    return jsonify({
        "count": count,
        "page": page,
        "per_page": per_page,
        "students": students[start:end],
    }), 200


@app.route("/api/students", methods=["POST"])
def create_student():
    """POST /api/students — створити студента."""
    global next_id

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Очікується JSON"}), 400

    cleaned, errors = validate_student_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    student = {
        **cleaned,
        "id": next_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    students_db[next_id] = student
    next_id += 1

    return jsonify(student), 201


@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    """GET /api/students/:id — отримати конкретного студента."""
    student = find_student_or_none(student_id)
    if student is None:
        return jsonify({"error": "Студента не знайдено"}), 404

    return jsonify(student), 200


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    """PUT /api/students/:id — повне оновлення студента."""
    student = find_student_or_none(student_id)
    if student is None:
        return jsonify({"error": "Студента не знайдено"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Очікується JSON"}), 400

    cleaned, errors = validate_student_data(data, partial=False, current_id=student_id)
    if errors:
        return jsonify({"errors": errors}), 400

    student.update(cleaned)
    return jsonify(student), 200


@app.route("/api/students/<int:student_id>", methods=["PATCH"])
def patch_student(student_id):
    """PATCH /api/students/:id — часткове оновлення студента."""
    student = find_student_or_none(student_id)
    if student is None:
        return jsonify({"error": "Студента не знайдено"}), 404

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Очікується JSON"}), 400

    cleaned, errors = validate_student_data(data, partial=True, current_id=student_id)
    if errors:
        return jsonify({"errors": errors}), 400

    student.update(cleaned)
    return jsonify(student), 200


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """DELETE /api/students/:id — видалити студента."""
    student = find_student_or_none(student_id)
    if student is None:
        return jsonify({"error": "Студента не знайдено"}), 404

    del students_db[student_id]
    return "", 204


@app.route("/api/students/stats", methods=["GET"])
def students_stats():
    """GET /api/students/stats — статистика по студентах."""
    students = list(students_db.values())
    total = len(students)

    avg_gpa = round(sum(student["gpa"] for student in students) / total, 2) if total else 0

    groups = {}
    for student in students:
        groups[student["group"]] = groups.get(student["group"], 0) + 1

    top_students = sorted(students, key=lambda student: student["gpa"], reverse=True)[:3]

    return jsonify({
        "total": total,
        "avg_gpa": avg_gpa,
        "groups": groups,
        "top_students": top_students,
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ресурс не знайдено", "status": 404}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Некоректний запит", "status": 400}), 400


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"error": "Помилка валідації", "status": 422}), 422


def seed_students():
    """Заповнити базу тестовими даними."""
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
    app.run(debug=True, port=5005)
