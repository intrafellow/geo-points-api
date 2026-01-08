## geo-points-api

Backend API на **Django 5 + DRF + GeoDjango/PostGIS** для работы с гео-точками и сообщениями:
- создание точки на карте
- создание сообщения к точке
- поиск точек/сообщений в радиусе (**radius в км**)
- авторизация по **JWT (access/refresh)**

Проект сделан под тестовое задание (intern/junior), но с “продовым” стеком: PostGIS, индексы, throttling, пагинация, тесты.

---

## Соответствие ТЗ (коротко)

- **POST `/api/points/`** — создание точки ✅
- **POST `/api/points/messages/`** — создание сообщения к точке ✅
- **GET `/api/points/search/`** — поиск точек в радиусе (параметры `latitude`, `longitude`, `radius` в км) ✅
- **GET `/api/points/messages/search/`** — поиск сообщений в радиусе ✅
- **Безопасность**: все доменные эндпоинты требуют `Authorization: Bearer <access>` ✅
- **Документация**: README + примеры curl + OpenAPI/Swagger ✅

---

## Требования

- Python **3.10+**
- PostgreSQL **+ PostGIS**

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

В другом терминале:

```bash
docker compose exec web python manage.py migrate
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

---

## Технические заметки (GeoDjango/PostGIS)

- Гео-координаты хранятся в `PointField(srid=4326, geography=True)` — это удобно для расстояний в метрах/км.
- Радиусный поиск сделан через `dwithin` + `D(km=radius)` (GeoDjango транслирует в PostGIS).
- На гео-поле есть **GIST индекс** для ускорения выборок.

---

## Production notes

- В проде обязательно задайте `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, корректный `DJANGO_ALLOWED_HOSTS`.
- В API включены throttling и пагинация (см. `config/settings.py`).



