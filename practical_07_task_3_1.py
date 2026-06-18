"""CRUD: Update та Delete для блогу."""

from flask import Flask, request, render_template_string, redirect, url_for, flash, abort
from datetime import datetime

app = Flask(__name__)
app.secret_key = "blog-secret-key"

LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Блог</title>
</head>
<body>
    <h1>Публікації</h1>

    {% with messages = get_flashed_messages() %}
    {% if messages %}
        <div style="color: green;">{{ messages[0] }}</div>
    {% endif %}
    {% endwith %}

    <a href="{{ url_for('post_create') }}">+ Нова публікація</a>
    <hr>

    {% for post in posts %}
    <article>
        <h2><a href="{{ url_for('post_detail', post_id=post.id) }}">{{ post.title }}</a></h2>
        <p>{{ post.content[:120] }}{% if post.content|length > 120 %}...{% endif %}</p>
        <small>{{ post.author }} | {{ post.created_at }}</small><br>
        <a href="{{ url_for('post_edit', post_id=post.id) }}">Редагувати</a> |
        <a href="{{ url_for('post_delete', post_id=post.id) }}">Видалити</a>
    </article>
    <hr>
    {% else %}
    <p>Публікацій немає.</p>
    {% endfor %}
</body>
</html>
"""

DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ post.title }}</title>
</head>
<body>
    <h1>{{ post.title }}</h1>
    <p>{{ post.content }}</p>
    <small>Автор: {{ post.author }} | {{ post.created_at }}</small>
    <hr>
    <a href="{{ url_for('post_edit', post_id=post.id) }}">Редагувати</a> |
    <a href="{{ url_for('post_delete', post_id=post.id) }}">Видалити</a> |
    <a href="{{ url_for('post_list') }}">Назад до списку</a>
</body>
</html>
"""

FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ form_title }}</title>
</head>
<body>
    <h1>{{ form_title }}</h1>

    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}

    <form method="POST">
        <label>Заголовок:</label><br>
        <input type="text" name="title" value="{{ post.title if post else '' }}"
               required style="width:400px;"><br><br>

        <label>Автор:</label><br>
        <input type="text" name="author" value="{{ post.author if post else '' }}"
               required><br><br>

        <label>Зміст:</label><br>
        <textarea name="content" rows="10" cols="50"
                  required>{{ post.content if post else '' }}</textarea><br><br>

        <button type="submit">{{ button_text }}</button>
        <a href="{{ url_for('post_list') }}">Скасувати</a>
    </form>
</body>
</html>
"""

DELETE_CONFIRM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Видалення</title>
</head>
<body>
    <h1>Підтвердження видалення</h1>
    <p>Ви дійсно бажаєте видалити публікацію "<strong>{{ post.title }}</strong>"?</p>

    <form method="POST">
        <button type="submit" style="color: red;">Так, видалити</button>
        <a href="{{ url_for('post_detail', post_id=post.id) }}">Скасувати</a>
    </form>
</body>
</html>
"""

posts_db = [
    {
        "id": 1,
        "title": "Перша публікація",
        "content": "Зміст першої публікації. Тут розміщено демонстраційний текст.",
        "author": "Іван",
        "created_at": "2025-01-15",
    },
    {
        "id": 2,
        "title": "Друга публікація",
        "content": "Зміст другої публікації. Цей запис можна редагувати або видалити.",
        "author": "Марія",
        "created_at": "2025-01-20",
    },
]
next_id = 3


def get_post_or_404(post_id: int) -> dict:
    """Знайти публікацію або повернути 404."""
    post = next((item for item in posts_db if item["id"] == post_id), None)
    if post is None:
        abort(404)
    return post


def validate_post_form():
    """Валідація форми публікації."""
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    content = request.form.get("content", "").strip()

    if not title or not author or not content:
        return None, "Усі поля мають бути заповнені."

    return {
        "title": title,
        "author": author,
        "content": content,
    }, None


@app.route("/")
def index():
    return redirect(url_for("post_list"))


@app.route("/posts")
def post_list():
    """READ: список публікацій."""
    return render_template_string(LIST_TEMPLATE, posts=posts_db)


@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    """READ: деталі публікації."""
    post = get_post_or_404(post_id)
    return render_template_string(DETAIL_TEMPLATE, post=post)


@app.route("/posts/create", methods=["GET", "POST"])
def post_create():
    """CREATE: створення нової публікації."""
    global next_id

    if request.method == "POST":
        post_data, error = validate_post_form()
        if error:
            return render_template_string(
                FORM_TEMPLATE,
                form_title="Нова публікація",
                button_text="Створити",
                post=request.form,
                error=error,
            )

        new_post = {
            "id": next_id,
            **post_data,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        posts_db.append(new_post)
        next_id += 1

        flash("Публікацію створено.")
        return redirect(url_for("post_detail", post_id=new_post["id"]))

    return render_template_string(
        FORM_TEMPLATE,
        form_title="Нова публікація",
        button_text="Створити",
        post=None,
        error=None,
    )


@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def post_edit(post_id):
    """UPDATE: редагування публікації."""
    post = get_post_or_404(post_id)

    if request.method == "POST":
        post_data, error = validate_post_form()
        if error:
            return render_template_string(
                FORM_TEMPLATE,
                form_title="Редагування публікації",
                button_text="Зберегти",
                post={**post, **request.form},
                error=error,
            )

        post.update(post_data)
        flash("Публікацію оновлено.")
        return redirect(url_for("post_detail", post_id=post["id"]))

    return render_template_string(
        FORM_TEMPLATE,
        form_title="Редагування публікації",
        button_text="Зберегти",
        post=post,
        error=None,
    )


@app.route("/posts/<int:post_id>/delete", methods=["GET", "POST"])
def post_delete(post_id):
    """DELETE: видалення публікації з підтвердженням."""
    post = get_post_or_404(post_id)

    if request.method == "POST":
        posts_db.remove(post)
        flash("Публікацію видалено.")
        return redirect(url_for("post_list"))

    return render_template_string(DELETE_CONFIRM_TEMPLATE, post=post)


@app.errorhandler(404)
def not_found(error):
    return "<h1>404</h1><p>Публікацію не знайдено.</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=5004)
