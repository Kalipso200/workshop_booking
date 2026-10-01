# Workshop Booking System

REST API для системы управления бронированием мастер-классов.

Проект реализован на **Django + Django REST Framework** с JWT-аутентификацией,
разграничением прав (роли `admin` / `user`), валидацией данных и оптимизацией ORM.
Документация API — через **drf-spectacular** (Swagger UI / ReDoc).

---

## Содержание

- [Возможности](#-возможности)
- [Технологический стек](#-технологический-стек)
- [Структура проекта](#-структура-проекта)
- [Быстрый старт через Docker](#-быстрый-старт-через-docker)
- [Локальный запуск (PostgreSQL в Docker)](#-локальный-запуск-postgresql-в-docker)
- [Переменные окружения](#-переменные-окружения)
- [Миграции и суперпользователь](#-миграции-и-суперпользователь)
- [API — эндпоинты](#-api--эндпоинты)
- [Аутентификация (JWT)](#-аутентификация-jwt)
- [Swagger / ReDoc](#-swagger--redoc)
- [Тесты](#-тесты)
- [Postman-коллекция](#-postman-коллекция)
- [Архитектура и ключевые решения](#-архитектура-и-ключевые-решения)
- [Полезные команды](#-полезные-команды)
- [Решение проблем](#-решение-проблем)

---

##  Возможности

-  **Публичный просмотр** списка и деталей мастер-классов без авторизации.
-  **JWT-аутентификация** (`access` / `refresh`).
-  **Регистрация** новых пользователей с ролью `user` по умолчанию.
-  **CRUD мастер-классов** доступен только пользователям с ролью `admin`.
-  **Бронирование мастер-классов** — только для авторизованных пользователей.
-  **Валидация**:
  - запрет записи на прошедшие даты;
  - запрет дублирования активной брони на один мастер-класс;
  - проверка вместимости (нельзя забронировать больше, чем `capacity`).
-  **Просмотр своих броней** — пользователь видит только свои.
-  **Отмена брони** — мягкое удаление (статус меняется на `cancelled`).
-  **Автодокументация API** через drf-spectacular.
-  **Тесты** на все ключевые сценарии.
-  **Готовая Postman-коллекция** с переменными и автотестами.

---

## Технологический стек

| Компонент | Версия / примечание |
|---|---|
| Python | 3.12 (рекомендуется; Django 5.0 не поддерживает 3.14) |
| Django | 5.0.6 |
| Django REST Framework | 3.15.1+ |
| SimpleJWT | 5.3.1 |
| drf-spectacular | 0.27.2+ |
| PostgreSQL | 16 (в Docker) |
| Docker / docker-compose | для контейнеризации |
| Gunicorn | для production-запуска в контейнере |

---

##  Структура проекта

```
workshop_booking/
├── .env                       # переменные окружения (локальные)
├── .env.example               # шаблон .env
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml         # web + db
├── docker-compose.db.yml      # только db (для локальной разработки)
├── manage.py
├── requirements.txt
├── README.md
│
├── workshop_booking/          # настройки проекта
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                  # пользователи, роли, аутентификация
│   ├── models.py              # User (с ролью)
│   ├── permissions.py         # IsAdminRole
│   ├── serializers.py
│   ├── views.py               # RegisterView, ProfileView
│   ├── urls.py                # /api/auth/...
│   ├── admin.py
│   ├── tests.py
│   └── migrations/
│
├── workshops/                 # мастер-классы
│   ├── models.py              # Workshop
│   ├── serializers.py
│   ├── services.py            # select_related / prefetch_related
│   ├── views.py               # WorkshopViewSet
│   ├── urls.py                # /api/workshops/...
│   ├── admin.py
│   ├── tests.py
│   └── migrations/
│
└── bookings/                  # бронирования
    ├── models.py              # Booking + UniqueConstraint
    ├── serializers.py
    ├── services.py            # get_user_bookings
    ├── views.py               # BookingViewSet
    ├── urls.py                # /api/bookings/...
    ├── admin.py
    ├── tests.py
    └── migrations/
```

---

## Быстрый старт через Docker

Полностью контейнеризованный запуск — Django в контейнере + PostgreSQL в контейнере.

### 1. Клонируйте проект и перейдите в директорию

```bash
git clone <repo_url>
cd workshop_booking
```

### 2. Создайте `.env`

```bash
cp .env.docker .env          # Linux / macOS
copy .env.docker .env        # Windows (cmd)
```

### 3. Запустите контейнеры

```bash
docker compose up --build
```

Будут подняты:
- `db` — PostgreSQL 16 на порту `5432`;
- `web` — Django с `runserver` на порту `8000`.

### 4. Создайте суперпользователя

В отдельном терминале:

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Готово

- API: http://localhost:8000/api/
- Админка: http://localhost:8000/admin/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/

### Полезные команды

```bash
# Остановить
docker compose down

# Остановить + удалить volume с БД (полный сброс)
docker compose down -v

# Логи
docker compose logs -f web
docker compose logs -f db

# Миграции внутри контейнера
docker compose exec web python manage.py migrate

# Тесты внутри контейнера
docker compose exec web python manage.py test
```

---

## Локальный запуск (PostgreSQL в Docker)

Такой вариант удобен для разработки: Django работает на хосте с hot-reload,
а PostgreSQL крутится в изолированном контейнере.

### 1. Поднимите PostgreSQL

Используйте отдельный compose-файл `docker-compose.db.yml`:

```bash
docker compose -f docker-compose.db.yml up -d
```

Проверьте, что контейнер запущен:

```bash
docker ps
```

Должен отображаться `workshop_db` со статусом `Up (healthy)`.

### 2. Создайте и активируйте виртуальное окружение

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (cmd):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> Используйте **Python 3.12**. На Python 3.14 Django 5.0.6 падает с `AttributeError: 'super' object has no attribute 'dicts'`.

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Создайте `.env` и проверьте `POSTGRES_HOST`

```bash
cp .env.example .env          # Linux / macOS
copy .env.example .env        # Windows
```

**Важно:** в `.env` должно быть `POSTGRES_HOST=localhost`, потому что Django теперь работает на хосте, а не в docker-сети.

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 5. Примените миграции

```bash
python manage.py makemigrations accounts workshops bookings
python manage.py migrate
```

### 6. Создайте суперпользователя

```bash
python manage.py createsuperuser
```

После создания зайдите в `/admin/` и убедитесь, что у пользователя установлена роль `admin`.

### 7. Запустите сервер

```bash
python manage.py runserver
```

API: http://localhost:8000/api/

### Остановка/сброс БД

```bash
# Остановить контейнер с БД
docker compose -f docker-compose.db.yml down

# Остановить и удалить volume (полный сброс данных)
docker compose -f docker-compose.db.yml down -v
```

---

## Переменные окружения

Шаблон — `.env.example`. Значения по умолчанию рассчитаны на запуск в Docker.

| Переменная | Назначение | Пример |
|---|---|---|
| `DJANGO_SECRET_KEY` | секретный ключ Django | `change-me-in-production` |
| `DJANGO_DEBUG` | режим отладки | `True` |
| `DJANGO_ALLOWED_HOSTS` | разрешённые хосты через запятую | `localhost,127.0.0.1` |
| `POSTGRES_DB` | имя БД | `workshop_db` |
| `POSTGRES_USER` | пользователь БД | `workshop_user` |
| `POSTGRES_PASSWORD` | пароль БД | `workshop_pass` |
| `POSTGRES_HOST` | хост БД | `db` (в Docker) / `localhost` (локально) |
| `POSTGRES_PORT` | порт БД | `5432` |

 **Для production:** обязательно смените `DJANGO_SECRET_KEY`, установите `DJANGO_DEBUG=False`, укажите конкретные `DJANGO_ALLOWED_HOSTS` и используйте надёжный пароль БД.

---

## Миграции и суперпользователь

```bash
# Создать миграции (только при изменении моделей)
python manage.py makemigrations

# Применить миграции
python manage.py migrate

# Проверить статус
python manage.py showmigrations

# Создать суперпользователя
python manage.py createsuperuser
```

### Установить роль admin вручную

Через shell:

```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username="admin")
u.role = User.Role.ADMIN
u.save()
```

Или через админку: `/admin/accounts/user/<id>/change/` → поле **Роль** → `Администратор`.

---

## API — эндпоинты

Базовый URL: `http://localhost:8000/api/`

### Аутентификация

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| `POST` | `/api/auth/register/` | все | Регистрация нового пользователя |
| `POST` | `/api/auth/login/` | все | Вход, возвращает `access` + `refresh` |
| `POST` | `/api/auth/refresh/` | все | Обновление access-токена |
| `GET` | `/api/auth/me/` | авторизован | Данные текущего пользователя |

### Мастер-классы

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| `GET` | `/api/workshops/` | все | Список мастер-классов |
| `GET` | `/api/workshops/{id}/` | все | Детали мастер-класса |
| `POST` | `/api/workshops/` | **admin** | Создать мастер-класс |
| `PUT` | `/api/workshops/{id}/` | **admin** | Полное обновление |
| `PATCH` | `/api/workshops/{id}/` | **admin** | Частичное обновление |
| `DELETE` | `/api/workshops/{id}/` | **admin** | Удалить |

### Бронирования

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| `GET` | `/api/bookings/` | авторизован | Список своих броней |
| `POST` | `/api/bookings/` | авторизован | Создать бронь |
| `GET` | `/api/bookings/{id}/` | авторизован | Детали своей брони |
| `DELETE` | `/api/bookings/{id}/` | авторизован | Отменить бронь |

### Примеры запросов

**Регистрация:**

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ivan","email":"ivan@example.com","password":"strongpass123"}'
```

**Логин:**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ivan","password":"strongpass123"}'
```

**Создание мастер-класса (admin):**

```bash
curl -X POST http://localhost:8000/api/workshops/ \
  -H "Authorization: Bearer <admin_access>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Django REST Framework",
    "description": "Практический мастер-класс",
    "date": "2027-01-15T18:00:00Z",
    "capacity": 10
  }'
```

**Создание брони:**

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <user_access>" \
  -H "Content-Type: application/json" \
  -d '{"workshop_id": 1}'
```

**Список своих броней:**

```bash
curl http://localhost:8000/api/bookings/ \
  -H "Authorization: Bearer <user_access>"
```

**Отмена брони:**

```bash
curl -X DELETE http://localhost:8000/api/bookings/1/ \
  -H "Authorization: Bearer <user_access>"
```

### Коды ответов

| Код | Значение |
|---|---|
| 200 | OK |
| 201 | Created |
| 204 | No Content (успешное удаление) |
| 400 | Ошибка валидации |
| 401 | Не авторизован |
| 403 | Нет прав |
| 404 | Не найдено |

---

## Аутентификация (JWT)

Проект использует **JWT Bearer**-аутентификацию (`djangorestframework-simplejwt`).

### Получение токена

```bash
POST /api/auth/login/
Content-Type: application/json

{ "username": "ivan", "password": "strongpass123" }
```

Ответ:

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Использование

Передавайте `access`-токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Время жизни

| Токен | Срок |
|---|---|
| `access` | 1 час |
| `refresh` | 7 дней |

### Обновление access

```bash
POST /api/auth/refresh/
Content-Type: application/json

{ "refresh": "<refresh_token>" }
```

### Роли

| Роль | Возможности |
|---|---|
| `user` | Просмотр мастер-классов, создание/просмотр/отмена своих броней |
| `admin` | Всё то же + CRUD мастер-классов |

Роль также автоматически считается `admin`, если у пользователя `is_superuser=True`.

---

## Swagger / ReDoc

Документация генерируется автоматически через **drf-spectacular**:

| URL | Что показывает |
|---|---|
| http://localhost:8000/api/schema/ | Сырая OpenAPI 3 схема (YAML/JSON) |
| http://localhost:8000/api/schema/swagger-ui/ | Интерактивный Swagger UI |
| http://localhost:8000/api/schema/redoc/ | ReDoc (альтернативный UI) |

### Авторизация в Swagger UI

1. Откройте Swagger UI.
2. Нажмите **Authorize** (справа сверху).
3. Введите `Bearer <ваш_access_токен>` (получите его через `POST /api/auth/login/`).
4. Благодаря `persistAuthorization: True` токен сохранится между перезагрузками.

### Генерация схемы через CLI

```bash
python manage.py spectacular --file schema.yml
python manage.py spectacular --file schema.yml --validate
```

---

##  Тесты

Тесты лежат в `tests.py` каждого приложения.

### Запуск всех тестов

```bash
python manage.py test
```

Django создаст тестовую БД `test_workshop_db`, применит миграции, прогонит тесты и удалит БД.
PostgreSQL-сервер при этом должен быть доступен.

### Запуск по приложению

```bash
python manage.py test accounts
python manage.py test workshops
python manage.py test bookings
```

### Конкретный класс / метод

```bash
python manage.py test bookings.tests.BookingAPITests
python manage.py test bookings.tests.BookingAPITests.test_capacity_limit
```

### Полезные флаги

| Флаг | Что делает |
|---|---|
| `-v 2` | Подробный вывод |
| `--keepdb` | Не удалять тестовую БД между запусками |
| `--parallel` | Параллельный запуск |
| `--failfast` | Остановиться на первой ошибке |

Пример:

```bash
python manage.py test --keepdb --parallel -v 2
```

### Что проверяется

**accounts:**
- регистрация нового пользователя;
- логин выдаёт `access` и `refresh`;
- `/api/auth/me/` требует авторизации;
- профиль возвращает текущего пользователя.

**workshops:**
- публичный список и детали;
- обычный пользователь не может создавать;
- админ может создавать;
- запрет создания в прошлом.

**bookings:**
- требуется авторизация;
- создание брони;
- запрет дубля;
- проверка вместимости;
- изоляция (только свои брони);
- отмена меняет статус, после чего можно бронировать снова.

---

##  Postman-коллекция

В проекте две папки для Postman:

- `Workshop_Booking.postman_collection.json` — сама коллекция.
- `Workshop_Booking.postman_environment.json` — окружение.

### Импорт

Postman → **File → Import** → перетащите JSON-файл.

### Порядок запуска

1. **Auth → Register User** — создаст `testuser`.
2. **Auth → Login (user)** — сохранит `accessToken`.
3. **Auth → Login (admin)** — сохранит `adminToken` (предварительно создайте администратора).
4. **Workshops → List Workshops** — подтянет `workshopId`.
5. **Workshops → Create Workshop (admin)** — создаст мастер-класс.
6. **Bookings → Create Booking** — создаст бронь.
7. **Bookings → List My Bookings** — покажет ваши брони.

>  **Важно:** для запросов `Register User`, `Login`, `Refresh` в Postman должен быть установлен **No Auth**, иначе туда прилетит устаревший `Bearer` и сервер вернёт `token_not_valid`.

### Run collection

Правой кнопкой на коллекцию → **Run collection** → **Run**. Postman прогонит все запросы и покажет автотесты (зелёные галочки = пройдено).

---

## Архитектура и ключевые решения

### Разделение на приложения

- **`accounts`** — модель `User` с ролями, JWT-аутентификация, права.
- **`workshops`** — модель `Workshop`, публичное чтение, CRUD для админа.
- **`bookings`** — модель `Booking`, брони пользователя.

### Сервисный слой

Логика выборки вынесена в `services.py`, чтобы:
- держать вьюхи «тонкими»;
- переиспользовать запросы в разных местах;
- централизованно применять `select_related` / `prefetch_related`.

### Оптимизация ORM

- `Workshop.objects.select_related("created_by").prefetch_related("bookings")` — избегаем N+1 при рендере списка мастер-классов и подсчёте мест.
- `Booking.objects.select_related("workshop", "workshop__created_by")` — избегаем N+1 при выводе броней с вложенным мастер-классом.

### Запрет дублей на уровне БД

В `Booking.Meta.constraints` используется:

```python
UniqueConstraint(
    fields=("user", "workshop"),
    condition=Q(status="active"),
    name="unique_active_booking_per_user_workshop",
)
```

Это гарантирует, что **активная** бронь пользователя на конкретный мастер-класс уникальна. Отменённые (со `status="cancelled"`) не мешают создать новую.

### Мягкое удаление броней

`DELETE /api/bookings/{id}/` не удаляет запись физически, а меняет `status` на `cancelled`.
Это позволяет:
- сохранить историю;
- разрешить повторную бронь после отмены;
- не ломать `UniqueConstraint`.

### Валидация

- Дата мастер-класса — в будущем.
- Дата мастер-класса при бронировании — в будущем.
- Свободные места — `available_seats > 0`.
- Отсутствие активной брони у пользователя.

### Безопасность

- Пароли хранятся в виде хешей (стандарт Django).
- Сериализаторы не отдают `password` в ответе.
- JWT — с ограниченным сроком жизни.
- Права проверяются через кастомный `IsAdminRole`.

---

##  Полезные команды

```bash
# Запуск сервера
python manage.py runserver

# Проверка проекта
python manage.py check

# Создание миграций
python manage.py makemigrations

# Применение миграций
python manage.py migrate

# Список миграций
python manage.py showmigrations

# Shell
python manage.py shell

# Создание суперпользователя
python manage.py createsuperuser

# Тесты
python manage.py test

# Генерация OpenAPI-схемы
python manage.py spectacular --file schema.yml

# Сбор статики (для production)
python manage.py collectstatic
```

### Docker

```bash
# Запустить всё
docker compose up --build

# Остановить
docker compose down

# Остановить + удалить volume (сброс БД)
docker compose down -v

# Логи
docker compose logs -f web
docker compose logs -f db

# Выполнить команду в контейнере
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test

# Только PostgreSQL (для локальной разработки)
docker compose -f docker-compose.db.yml up -d
docker compose -f docker-compose.db.yml down
docker compose -f docker-compose.db.yml down -v
```

---

## Решение проблем

### `AttributeError: 'super' object has no attribute 'dicts'` в админке

**Причина:** Python 3.14 + Django 5.0.6 — несовместимость в `template/context.py`.

**Решение:**
- Понизить Python до 3.12, **или**
- Обновить Django до 5.2+.

### `ImportError: cannot import name 'cc_delim_re' from 'django.utils.cache'`

**Причина:** DRF 3.15.1 использует функцию, удалённую в новых Django.

**Решение:**

```bash
pip install --upgrade djangorestframework
```

Убедитесь, что версия DRF ≥ 3.16.

### `psycopg2-binary` не устанавливается на Windows

**Причина:** для новых версий Python нет wheel-пакета `psycopg2-binary`.

**Решение:** используйте `psycopg[binary]` (v3) — он уже в `requirements.txt`:

```txt
psycopg[binary]
```

### Ошибка `permission denied to create database` при тестах

**Причина:** у пользователя БД нет прав на создание тестовой БД.

**Решение:**

```bash
docker exec -it workshop_db psql -U workshop_user -d workshop_db -c "ALTER USER workshop_user CREATEDB;"
```

### `could not connect to server: Connection refused`

**Причина:** PostgreSQL ещё не готов.

**Решение:** подождите 5–10 секунд или проверьте логи:

```bash
docker logs workshop_db
```

Если видите `database system is ready to accept connections` — можно подключаться.

### Порт 5432 уже занят

**Причина:** на хосте уже запущен PostgreSQL.

**Решение:** в `docker-compose.db.yml` поменяйте маппинг:

```yaml
ports:
  - "5433:5432"
```

И в `.env`: `POSTGRES_PORT=5433`.

### Postman возвращает `token_not_valid` на `/register/`

**Причина:** на уровне коллекции задан `Bearer {{accessToken}}`, и этот заголовок прилетает на публичные эндпоинты.

**Решение:** для `Register User`, `Login`, `Refresh` установите **No Auth** в Postman.

### `Authorization: Bearer null` при запросе к `/bookings/`

**Причина:** переменная `accessToken` пуста — вы не выполнили `Login (user)` перед запросом.

**Решение:** сначала запустите `Auth → Login (user)`, затем проверьте значение переменной в **Collections → Workshop Booking API → Variables**.

---
