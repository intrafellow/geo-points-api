## geo-points-api

Backend API на **Django 5 + DRF + GeoDjango/PostGIS** для работы с гео-точками и сообщениями:
- создание точки на карте
- создание сообщения к точке
- поиск точек/сообщений в радиусе (**radius в км**)
- авторизация по **JWT (access/refresh)**

Проект сделан под тестовое задание (intern/junior), но с “продовым” стеком: PostGIS, индексы, throttling, пагинация, тесты.

---

## Соответствие ТЗ (коротко)

- **POST `/api/points/`** — создание точки
- **POST `/api/points/messages/`** — создание сообщения к точке
- **GET `/api/points/search/`** — поиск точек в радиусе (параметры `latitude`, `longitude`, `radius` в км)
- **GET `/api/points/messages/search/`** — поиск сообщений в радиусе
- **Безопасность**: все доменные эндпоинты требуют `Authorization: Bearer <access>`
- **Документация**: README + примеры curl + OpenAPI/Swagger

Дополнительно (вне исходного ТЗ, для удобства проверки):
- **POST `/api/auth/register/`** — регистрация пользователя
- **POST `/api/admin/test-users/`** — создание тестового пользователя (только admin/staff, можно отключить через env)

---

## Требования

- Python **3.10+**
- PostgreSQL **+ PostGIS**

---

## Структура проекта (DRF style)

Доменные эндпоинты реализованы в каноничном стиле DRF:

- **`apps/geo/views/`**: DRF views на `GenericAPIView` / `ListAPIView` + mixins (тонкий API-слой)
- **`apps/geo/urls.py`**: маршрутизация эндпоинтов (URL'ы не менялись)
- **`apps/geo/schemas/`**: DRF serializers (request/response контракты + валидации)
- **`apps/geo/models/`**: модели + `QuerySet` методы для geo-запросов (`within_radius`)

Сервисный слой и репозитории намеренно **убраны**: ORM/geo-запросы живут в `QuerySet`, а валидации — в сериализаторах.

---

## Быстрый старт (Docker, рекомендовано)

### 1) Подготовить `.env`

```bash
cp env.example .env
```

### 2) Поднять PostGIS + приложение

```bash
docker compose up --build
```

### 3) Миграции и пользователь

Миграции выполняются автоматически при старте контейнера `web` (см. `scripts/entrypoint.py` + `RUN_MIGRATIONS=1` в `docker-compose.yml`).

Создать admin-пользователя можно вручную:

```bash
docker compose exec web python manage.py createsuperuser
```

---

## Запуск локально (без Docker)

1) Поднимите PostGIS локально и задайте переменные окружения как в `.env` (см. `env.example`).
2) Установите зависимости:

```bash
python -m pip install -r requirements.txt
```

3) Примените миграции и запустите сервер:

```bash
python manage.py migrate
python manage.py runserver
```

---

## Django Debug Toolbar (для анализа SQL)

Для быстрых проверок количества/времени запросов можно включить **django-debug-toolbar**:

- В проекте он подключается **только при `DJANGO_DEBUG=1`** и **автоматически отключён в тестах** (в проде не активен).
- Для DRF удобнее всего смотреть toolbar на **HTML-страницах** (Swagger/Redoc/Browsable API), т.к. в JSON-ответы он не “встраивается”.
  - Откройте `GET /api/docs/` в браузере — справа появится панель.
  - Запускайте запросы из Swagger UI или открывайте эндпоинты в Browsable API, и смотрите вкладку **SQL**.

Если вы запускаете приложение в Docker и панель не показывается из-за `INTERNAL_IPS`, задайте:

```bash
DJANGO_INTERNAL_IPS=127.0.0.1,localhost
```

Что смотреть в контексте этого проекта:

- **Поиск точек/сообщений**: убедиться, что запрос использует PostGIS `dwithin` и не делает лишних N+1.
  - Для поиска сообщений важно **не тащить колонки `geo_points`** (точка нужна только для geo-фильтра) и тянуть из автора только `username`.
- **Пагинация**: на страницах со списками убедиться, что количество запросов стабильно при росте данных.

### Как вытащить SQL в файл (без ручных кликов)

В репозитории есть скрипт `scripts/capture_sql_via_debug_toolbar.py`, который:
- прогоняет набор ключевых эндпоинтов (register/token/create/search)
- забирает SQL из debug-toolbar History (`/__debug__/history_refresh` + `render_panel?panel_id=SQLPanel`)
- пишет результат в markdown-файл, маскируя чувствительные литералы (JWT/хэши)

#### Вариант A: с хоста (рекомендовано)

```bash
docker compose up --build
python scripts/capture_sql_via_debug_toolbar.py --base-url http://localhost:8000 --out SQL_CAPTURE.md
```

#### Вариант B: из контейнера web

```bash
docker compose up --build
docker compose exec web python scripts/capture_sql_via_debug_toolbar.py --base-url http://localhost:8000 --out SQL_CAPTURE.md
```

Результат: `SQL_CAPTURE.md`.

---

## Переменные окружения

Минимально:
- **`DJANGO_SECRET_KEY`**: секрет Django (обязательно для прод-режима)
- **`DJANGO_DEBUG`**: `1`/`0`
- **`DJANGO_ALLOWED_HOSTS`**: список хостов через запятую
- **`DB_*`**: параметры подключения к Postgres/PostGIS

Опционально:
- **`MAX_SEARCH_RADIUS_KM`**: ограничение радиуса поиска (в км). Если не задано — лимит не применяется.
- **`JWT_ACCESS_MINUTES`** (по умолчанию 10), **`JWT_REFRESH_DAYS`** (по умолчанию 7)
- **`THROTTLE_ANON`**, **`THROTTLE_USER`**, **`API_PAGE_SIZE`**
- **`DJANGO_LANGUAGE_CODE`** (по умолчанию `ru-ru`), **`DJANGO_TIME_ZONE`** (по умолчанию `UTC`)
- **`ENABLE_TEST_USER_ENDPOINT`**: `1`/`0` — включить/выключить `POST /api/admin/test-users/` (по умолчанию включено в debug)
- **`LOG_LEVEL`**, **`DJANGO_LOG_LEVEL`**: уровни логирования (по умолчанию `INFO`). Логи пишутся в stdout, удобно смотреть через `docker compose logs -f web`.

---

## Авторизация (JWT)

### Получить токен (access/refresh)

```bash
curl -X POST "http://localhost:8000/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

Ответ:

```json
{"access":"...","refresh":"..."}
```

### Использовать токен

Все доменные эндпоинты требуют:

`Authorization: Bearer <access>`

### Refresh токена

```bash
curl -X POST "http://localhost:8000/api/auth/token/refresh/" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"..."}'
```

### Отозвать refresh-токен (blacklist)

```bash
curl -X POST "http://localhost:8000/api/auth/token/blacklist/" \
  -H "Content-Type: application/json" \
  -d '{"refresh":"..."}'
```

---

## Регистрация (доп. эндпоинт для тестового задания)

**POST `/api/auth/register/`** (без авторизации)

Request:

```json
{"username":"user1","password":"S0mething-Longer_123"}
```

Response `201`:

```json
{"id": 1, "username": "user1"}
```

Далее получите JWT через `POST /api/auth/token/`.

---

## API (эндпоинты из ТЗ)

### 1) Создание точки

**POST `/api/points/`** (JWT required)

Request:

```json
{
  "title": "optional string",
  "latitude": 55.751244,
  "longitude": 37.618423
}
```

Response `201`:

```json
{
  "id": 1,
  "title": "optional string",
  "latitude": 55.751244,
  "longitude": 37.618423,
  "created_at": "2025-01-01T12:00:00Z"
}
```

### 2) Создание сообщения к точке

**POST `/api/points/messages/`** (JWT required)

Request:

```json
{
  "point_id": 1,
  "text": "hello"
}
```

Response `201`:

```json
{
  "id": 1,
  "point_id": 1,
  "text": "hello",
  "author": "username",
  "created_at": "2025-01-01T12:00:00Z"
}
```

### 3) Поиск точек в радиусе

**GET `/api/points/search/?latitude=...&longitude=...&radius=...`** (JWT required)

- `radius` — в **км**
- Пагинация: `page`, `page_size`
- Опционально можно ограничить максимальный радиус через `MAX_SEARCH_RADIUS_KM` (км)

Response `200` (пагинация):

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "optional string",
      "latitude": 55.751244,
      "longitude": 37.618423,
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

### 4) Поиск сообщений в радиусе

**GET `/api/points/messages/search/?latitude=...&longitude=...&radius=...`** (JWT required)

- `radius` — в **км**
- Пагинация: `page`, `page_size`
- Опционально можно ограничить максимальный радиус через `MAX_SEARCH_RADIUS_KM` (км)

Response `200` (пагинация):

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "point_id": 1,
      "text": "hello",
      "author": "username",
      "created_at": "2025-01-01T12:00:00Z"
    }
  ]
}
```

---

## Примеры curl

### Получить токен и сохранить access

```bash
BASE_URL="http://localhost:8000"
TOKENS_JSON=$(curl -sS -X POST "$BASE_URL/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}')
ACCESS=$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read())["access"])' <<<"$TOKENS_JSON")
```

### Создать точку

```bash
curl -X POST "$BASE_URL/api/points/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{"title":"A","latitude":55.751244,"longitude":37.618423}'
```

### Создать сообщение

```bash
curl -X POST "$BASE_URL/api/points/messages/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ACCESS" \
  -d '{"point_id":1,"text":"hello"}'
```

### Поиск точек (radius в км)

```bash
curl "$BASE_URL/api/points/search/?latitude=55.751244&longitude=37.618423&radius=1" \
  -H "Authorization: Bearer $ACCESS"
```

### Поиск сообщений (radius в км)

```bash
curl "$BASE_URL/api/points/messages/search/?latitude=55.751244&longitude=37.618423&radius=1" \
  -H "Authorization: Bearer $ACCESS"
```

---

## OpenAPI / Swagger

- OpenAPI schema:
  - JSON: `GET /api/schema/?format=json`
  - YAML: `GET /api/schema/` (по умолчанию)
- Swagger UI: `GET /api/docs/`
- Redoc: `GET /api/redoc/`

Авторизация в Swagger:
1) получите `access` через `POST /api/auth/token/`
2) нажмите **Authorize**
3) вставьте:

`Bearer <access>`

---

## Тесты

Тесты требуют PostGIS. Самый простой способ:

```bash
docker compose run --rm web pytest -q
```

Покрытие (pytest-cov):

```bash
docker compose run --rm web pytest --cov=apps --cov-report=term -q
```

Текущее покрытие: **99%** (TOTAL по `--cov=apps`).

---

## Технические заметки (GeoDjango/PostGIS)

- Гео-координаты хранятся в `PointField(srid=4326, geography=True)` — это удобно для расстояний в метрах/км.
- Радиусный поиск сделан через `dwithin` + `D(km=radius)` (GeoDjango транслирует в PostGIS).
- На гео-поле есть **GIST индекс** для ускорения выборок.

---

## Production notes

- В проде обязательно задайте `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, корректный `DJANGO_ALLOWED_HOSTS`.
- В API включены throttling и пагинация (см. `config/settings.py`).
