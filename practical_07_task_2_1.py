"""Cookies та sessions у Flask."""

from flask import Flask, request, make_response, session, redirect, url_for, jsonify

app = Flask(__name__)
app.secret_key = "super-secret-key-for-session"

products_db = {
    1: {"name": "Ноутбук", "price": 25000},
    2: {"name": "Смартфон", "price": 12000},
    3: {"name": "Навушники", "price": 2000},
}

COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 днів


@app.route("/")
def index():
    """Головна сторінка з посиланнями для тестування."""
    return """
    <h1>Cookies та sessions</h1>
    <h2>Cookies</h2>
    <ul>
        <li><a href="/set-theme/dark">Встановити темну тему</a></li>
        <li><a href="/get-theme">Прочитати тему</a></li>
        <li><a href="/set-language/uk">Встановити українську мову</a></li>
        <li><a href="/preferences">Показати cookies</a></li>
    </ul>

    <h2>Sessions</h2>
    <ul>
        <li><a href="/cart/add/1">Додати ноутбук у кошик</a></li>
        <li><a href="/cart/add/2">Додати смартфон у кошик</a></li>
        <li><a href="/cart">Переглянути кошик</a></li>
        <li><a href="/cart/clear">Очистити кошик</a></li>
        <li><a href="/login">Логін</a></li>
        <li><a href="/profile">Профіль</a></li>
        <li><a href="/logout">Вийти</a></li>
    </ul>
    """


@app.route("/set-theme/<theme>")
def set_theme(theme):
    """Встановити тему через cookie."""
    if theme not in {"light", "dark"}:
        return jsonify({"error": "Тема має бути light або dark"}), 400

    response = make_response(jsonify({
        "message": f"Тему встановлено: {theme}",
        "storage": "cookie",
        "note": "Cookie зберігається у браузері клієнта.",
    }))

    response.set_cookie(
        "theme",
        theme,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
    )
    return response


@app.route("/get-theme")
def get_theme():
    """Прочитати тему з cookie."""
    theme = request.cookies.get("theme", "light")
    return jsonify({
        "theme": theme,
        "source": "request.cookies",
    })


@app.route("/set-language/<lang>")
def set_language(lang):
    """Встановити мову через cookie."""
    response = make_response(jsonify({
        "message": f"Мову встановлено: {lang}",
        "storage": "cookie",
    }))
    response.set_cookie(
        "language",
        lang,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
    )
    return response


@app.route("/preferences")
def preferences():
    """Показати всі збережені уподобання з cookies."""
    return jsonify({
        "cookies": dict(request.cookies),
        "explanation": "Cookies зберігаються на стороні клієнта і надсилаються браузером з кожним запитом.",
    })


@app.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    """Додати товар до кошика через session."""
    if product_id not in products_db:
        return jsonify({"error": "Товар не знайдено"}), 404

    cart = session.get("cart", [])
    cart.append(product_id)
    session["cart"] = cart

    return jsonify({
        "message": "Товар додано до кошика",
        "added_product": products_db[product_id],
        "cart": cart,
        "storage": "session",
        "note": "Дані сесії логічно зберігають стан користувача між запитами.",
    })


@app.route("/cart")
def view_cart():
    """Переглянути кошик."""
    cart_ids = session.get("cart", [])
    products = [
        {"id": product_id, **products_db[product_id]}
        for product_id in cart_ids
        if product_id in products_db
    ]

    total = sum(product["price"] for product in products)

    return jsonify({
        "cart_ids": cart_ids,
        "products": products,
        "total": total,
    })


@app.route("/cart/clear")
def clear_cart():
    """Очистити кошик."""
    session.pop("cart", None)
    return jsonify({"message": "Кошик очищено"})


@app.route("/login", methods=["GET", "POST"])
def login():
    """Імітація входу — зберегти ім'я у session."""
    if request.method == "GET":
        return """
        <h1>Логін</h1>
        <form method="POST">
            <label>Ім'я користувача:</label><br>
            <input type="text" name="username" required><br><br>
            <button type="submit">Увійти</button>
        </form>
        """

    if request.is_json:
        payload = request.get_json(silent=True) or {}
        username = payload.get("username", "")
    else:
        username = request.form.get("username", "")

    username = username.strip()

    if not username:
        return jsonify({"error": "Потрібно передати username"}), 400

    session["username"] = username
    return jsonify({
        "message": "Вхід виконано",
        "username": username,
    })


@app.route("/logout")
def logout():
    """Вихід — видалити username з session."""
    session.pop("username", None)
    return jsonify({"message": "Вихід виконано"})


@app.route("/profile")
def profile():
    """Профіль користувача — залежить від session."""
    username = session.get("username")

    if not username:
        return redirect(url_for("login"))

    return jsonify({
        "username": username,
        "message": "Це профіль користувача із session.",
    })


if __name__ == "__main__":
    app.run(debug=True, port=5002)
