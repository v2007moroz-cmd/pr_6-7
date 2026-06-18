"""CRUD: Create та Read для блогу."""

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

    {% if posts %}
        {% for post in posts %}
        <article>
            <h2><a href="{{ url_for('post_detail', post_id=post.id) }}">{{ post.title }}</a></h2>
            <p>{{ post.content[:100] }}{% if post.content|length > 100 %}...{% endif %}</p>
            <small>{{ post.author }} | {{ post.created_at }}</small>
        </article>
        <hr>
        {% endfor %}
    {% else %}
        <p>Поки немає публікацій.</p>
    {% endif %}

    <p>Сторінка {{ page }} з {{ total_pages }}</p>
    {% if page > 1 %}
        <a href="{{ url_for('post_list', page=page-1) }}">Попередня</a>
    {% endif %}
    {% if page < total_pages %}
        <a href="{{ url_for('post_list', page=page+1) }}">Наступна</a>
    {% endif %}
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
    <a href="{{ url_for('post_list') }}">Назад до списку</a>
</body>
</html>
"""

posts_db = []
next_id = 1


def get_post_or_404(post_id: int) -> dict:
    """Знайти публікацію або повернути 404."""
    post = next((item for item in posts_db if item["id"] == post_id), None)
    if post is None:
        abort(404)
    return post


def validate_post_form():
    """Перевірка полів форми."""
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
    """Редірект на список публікацій."""
    return redirect(url_for("post_list"))


@app.route("/posts")
def post_list():
    """READ: список усіх публікацій з пагінацією."""
    page = request.args.get("page", default=1, type=int)
    per_page = 5

    if page < 1:
        page = 1

    total_posts = len(posts_db)
    total_pages = max((total_posts + per_page - 1) // per_page, 1)

    if page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    posts = posts_db[start:end]

    return render_template_string(
        LIST_TEMPLATE,
        posts=posts,
        page=page,
        total_pages=total_pages,
    )


@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    """READ: деталі однієї публікації."""
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

        flash("Публікацію успішно створено.")
        return redirect(url_for("post_detail", post_id=new_post["id"]))

    return render_template_string(
        FORM_TEMPLATE,
        form_title="Нова публікація",
        button_text="Створити",
        post=None,
        error=None,
    )


@app.errorhandler(404)
def not_found(error):
    return "<h1>404</h1><p>Публікацію не знайдено.</p>", 404


if __name__ == "__main__":
    app.run(debug=True, port=5003)
