"""Маршрутизація Flask: GET, POST, динамічні параметри."""

from flask import Flask, request, render_template_string, redirect, url_for, abort

app = Flask(__name__)

BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>
    <nav>
        <a href="{{ url_for('index') }}">Головна</a> |
        <a href="{{ url_for('post_list') }}">Публікації</a> |
        <a href="{{ url_for('search') }}">Пошук</a>
    </nav>
    <hr>
    {{ content | safe }}
</body>
</html>
"""

posts_db = [
    {
        "id": 1,
        "title": "Вступ до Python",
        "content": "Python — потужна мова програмування для вебу, аналізу даних та автоматизації.",
        "author": "Іван",
    },
    {
        "id": 2,
        "title": "Flask для початківців",
        "content": "Flask — мікрофреймворк для швидкого створення веб-додатків.",
        "author": "Марія",
    },
    {
        "id": 3,
        "title": "REST API",
        "content": "REST — архітектурний стиль для побудови веб-сервісів.",
        "author": "Петро",
    },
]
next_id = 4


def render_page(title: str, content: str, status_code: int = 200):
    """Допоміжна функція для рендерингу сторінки."""
    return render_template_string(BASE_TEMPLATE, title=title, content=content), status_code


@app.route("/")
def index():
    """GET / — головна сторінка."""
    content = """
    <p>Це демонстраційний Flask-додаток для перевірки маршрутизації.</p>
    <ul>
        <li><a href="/posts">Список публікацій</a></li>
        <li><a href="/posts/create">Створити публікацію</a></li>
        <li><a href="/search?q=Flask">Пошук Flask</a></li>
        <li><a href="/archive/2026/6">Архів за червень 2026</a></li>
        <li><a href="/user/olena">Профіль користувача</a></li>
    </ul>
    """
    return render_page("Головна сторінка", content)


@app.route("/posts")
def post_list():
    """GET /posts?page=1&per_page=10 — список публікацій з пагінацією."""
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)

    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10

    start = (page - 1) * per_page
    end = start + per_page
    posts = posts_db[start:end]

    items = "".join(
        f"""
        <article>
            <h2><a href="{url_for('post_detail', post_id=post['id'])}">{post['title']}</a></h2>
            <p>{post['content']}</p>
            <small>Автор: <a href="{url_for('user_profile', username=post['author'])}">{post['author']}</a></small>
        </article>
        <hr>
        """
        for post in posts
    )

    if not items:
        items = "<p>Публікацій на цій сторінці немає.</p>"

    content = f"""
    <p>Поточна сторінка: {page}; на сторінці: {per_page}</p>
    <p><a href="{url_for('post_create')}">+ Створити публікацію</a></p>
    {items}
    """
    return render_page("Список публікацій", content)


@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    """GET /posts/<int:post_id> — деталі публікації."""
    post = next((item for item in posts_db if item["id"] == post_id), None)
    if post is None:
        abort(404)

    content = f"""
    <article>
        <h2>{post['title']}</h2>
        <p>{post['content']}</p>
        <small>Автор: {post['author']}</small>
    </article>
    <p><a href="{url_for('post_list')}">Назад до списку</a></p>
    """
    return render_page(f"Публікація #{post_id}", content)


@app.route("/posts/create", methods=["GET", "POST"])
def post_create():
    """GET+POST /posts/create — форма створення публікації."""
    global next_id

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        content_text = request.form.get("content", "").strip()

        if not title or not author or not content_text:
            error = "<p style='color:red;'>Усі поля обов'язкові.</p>"
            return render_page("Створення публікації", error + create_form())

        new_post = {
            "id": next_id,
            "title": title,
            "content": content_text,
            "author": author,
        }
        posts_db.append(new_post)
        next_id += 1

        return redirect(url_for("post_detail", post_id=new_post["id"]))

    return render_page("Створення публікації", create_form())


def create_form() -> str:
    """HTML-форма для створення публікації."""
    return """
    <form method="POST">
        <label>Заголовок:</label><br>
        <input type="text" name="title" required><br><br>

        <label>Автор:</label><br>
        <input type="text" name="author" required><br><br>

        <label>Зміст:</label><br>
        <textarea name="content" rows="6" cols="50" required></textarea><br><br>

        <button type="submit">Створити</button>
    </form>
    """


@app.route("/search")
def search():
    """GET /search?q=query — пошук публікацій за рядком."""
    query = request.args.get("q", "").strip().lower()

    if not query:
        content = """
        <form method="GET">
            <input type="text" name="q" placeholder="Введіть запит">
            <button type="submit">Шукати</button>
        </form>
        """
        return render_page("Пошук", content)

    results = [
        post for post in posts_db
        if query in post["title"].lower() or query in post["content"].lower()
    ]

    items = "".join(
        f'<li><a href="{url_for("post_detail", post_id=post["id"])}">{post["title"]}</a></li>'
        for post in results
    ) or "<li>Нічого не знайдено.</li>"

    content = f"""
    <p>Пошуковий запит: <strong>{query}</strong></p>
    <ul>{items}</ul>
    """
    return render_page("Результати пошуку", content)


@app.route("/archive/<int:year>/<int:month>")
def archive(year, month):
    """GET /archive/<int:year>/<int:month> — архів за датою."""
    if month < 1 or month > 12:
        abort(404)

    content = f"""
    <p>Архів публікацій за {month:02d}.{year}.</p>
    <p>У цьому прикладі дата використовується як динамічний параметр URL.</p>
    """
    return render_page("Архів", content)


@app.route("/user/<string:username>")
def user_profile(username):
    """GET /user/<string:username> — профіль користувача."""
    user_posts = [post for post in posts_db if post["author"].lower() == username.lower()]

    items = "".join(
        f'<li><a href="{url_for("post_detail", post_id=post["id"])}">{post["title"]}</a></li>'
        for post in user_posts
    ) or "<li>У користувача поки немає публікацій.</li>"

    content = f"""
    <p>Ім'я користувача: <strong>{username}</strong></p>
    <h3>Публікації автора</h3>
    <ul>{items}</ul>
    """
    return render_page("Профіль користувача", content)


@app.errorhandler(404)
def page_not_found(error):
    """HTML-відповідь для неіснуючих сторінок."""
    return render_page("404", "<p>Сторінку не знайдено.</p>", 404)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
