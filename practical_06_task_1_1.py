# Таблиця ендпоінтів API

## practical_06_task_1_1.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | / | Головна сторінка | 200 |
| GET | /posts | Список публікацій з пагінацією | 200 |
| GET | /posts/<id> | Деталі публікації | 200, 404 |
| GET/POST | /posts/create | Форма та створення публікації | 200, 302 |
| GET | /search?q=... | Пошук публікацій | 200 |
| GET | /archive/<year>/<month> | Архів за датою | 200, 404 |
| GET | /user/<username> | Профіль користувача | 200 |

## practical_06_task_1_2.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /api/items | Список товарів, фільтрація, сортування | 200, 400 |
| POST | /api/items | Створення товару | 201, 400 |
| GET | /api/items/<id> | Деталі товару | 200, 404 |
| PUT | /api/items/<id> | Повне оновлення товару | 200, 400, 404 |
| DELETE | /api/items/<id> | Видалення товару | 204, 404 |

## practical_06_task_1_3.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /set-theme/<theme> | Встановити cookie theme | 200, 400 |
| GET | /get-theme | Прочитати cookie theme | 200 |
| GET | /set-language/<lang> | Встановити cookie language | 200 |
| GET | /preferences | Показати cookies | 200 |
| GET | /cart/add/<product_id> | Додати товар у session cart | 200, 404 |
| GET | /cart | Переглянути кошик | 200 |
| GET | /cart/clear | Очистити кошик | 200 |
| GET/POST | /login | Форма входу / запис username у session | 200, 400 |
| GET | /logout | Видалити username із session | 200 |
| GET | /profile | Профіль або redirect на login | 200, 302 |

## practical_07_task_2_1.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /posts | Список публікацій з пагінацією | 200 |
| GET | /posts/<id> | Деталі публікації | 200, 404 |
| GET/POST | /posts/create | Створення публікації | 200, 302 |

## practical_07_task_2_2.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /posts | Список публікацій | 200 |
| GET | /posts/<id> | Деталі публікації | 200, 404 |
| GET/POST | /posts/create | Створення публікації | 200, 302 |
| GET/POST | /posts/<id>/edit | Редагування публікації | 200, 302, 404 |
| GET/POST | /posts/<id>/delete | Підтвердження та видалення | 200, 302, 404 |

## practical_07_task_3_1.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /api/students | Список студентів, фільтрація, пагінація | 200, 400 |
| POST | /api/students | Створення студента | 201, 400 |
| GET | /api/students/<id> | Деталі студента | 200, 404 |
| PUT | /api/students/<id> | Повне оновлення студента | 200, 400, 404 |
| PATCH | /api/students/<id> | Часткове оновлення студента | 200, 400, 404 |
| DELETE | /api/students/<id> | Видалення студента | 204, 404 |
| GET | /api/students/stats | Статистика студентів | 200 |

## practical_07_task_3_2.py

| Метод | URL | Опис | Статус-коди |
|---|---|---|---|
| GET | /api/v2/students | Список студентів із серіалізацією, fields, search | 200, 400 |
| POST | /api/v2/students | Створення студента з API-ключем | 201, 401, 409, 422 |
