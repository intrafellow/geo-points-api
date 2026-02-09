# SQL capture (django-debug-toolbar)

- **generated_at**: `2026-02-09 16:15:15`
- **source**: debug-toolbar History (`/__debug__/history_refresh`) + `/__debug__/render_panel/?panel_id=SQLPanel`
- **note**: токены/хэши/служебные литералы в SQL могут быть замаскированы как `<redacted_...>`.

## Summary

| step | request | status | sql_count |
| --- | --- | ---: | ---: |
| `register` | `POST /api/auth/register/` | `201` | `2` |
| `token` | `POST /api/auth/token/` | `200` | `3` |
| `create_point` | `POST /api/points/` | `201` | `2` |
| `create_message` | `POST /api/points/messages/` | `201` | `3` |
| `search_points` | `GET /api/points/search/?latitude=55.751244&longitude=37.618423&radius=2` | `200` | `4` |
| `search_messages` | `GET /api/points/messages/search/?latitude=55.751244&longitude=37.618423&radius=2` | `200` | `3` |

## register

- **request**: `POST /api/auth/register/`
- **status**: `201`
- **store_id**: `bf6c5448b9e44befb1b57cec275f79d6`
- **sql_count**: `2`

```sql
SELECT 1 AS "a" 
FROM "auth_user" 
WHERE "auth_user"."username" = '<generated_username>' 
LIMIT 1;

INSERT INTO "auth_user" ("password", "last_login", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined") 
VALUES ('<redacted_password_hash>', NULL , false , '<generated_username>', '', '', '', false , true , '2026-02-09 13:15:14.789086+00:00'::timestamptz) RETURNING "auth_user"."id";

```

## token

- **request**: `POST /api/auth/token/`
- **status**: `200`
- **store_id**: `cc616f4713ac4ad19f20000c27495bb7`
- **sql_count**: `3`

```sql
SELECT "auth_user"."id", 
"auth_user"."password", 
"auth_user"."last_login", 
"auth_user"."is_superuser", 
"auth_user"."username", 
"auth_user"."first_name", 
"auth_user"."last_name", 
"auth_user"."email", 
"auth_user"."is_staff", 
"auth_user"."is_active", 
"auth_user"."date_joined" 
FROM "auth_user" 
WHERE "auth_user"."username" = '<generated_username>' 
LIMIT 21;

INSERT INTO "token_blacklist_outstandingtoken" ("user_id", "jti", "token", "created_at", "expires_at") 
VALUES (7, 'b8bcd5efe4df461d8cbff3da8652e6f7', '<redacted_jwt>', '2026-02-09 13:15:15.114322+00:00'::timestamptz, '2026-02-16 13:15:15+00:00'::timestamptz) RETURNING "token_blacklist_outstandingtoken"."id";

UPDATE "auth_user" 
SET "last_login" = '2026-02-09 13:15:15.137914+00:00'::timestamptz 
WHERE "auth_user"."id" = 7;

```

## create_point

- **request**: `POST /api/points/`
- **status**: `201`
- **store_id**: `a22f554a428843b18597b77492bd3512`
- **sql_count**: `2`

```sql
SELECT "auth_user"."id", 
"auth_user"."password", 
"auth_user"."last_login", 
"auth_user"."is_superuser", 
"auth_user"."username", 
"auth_user"."first_name", 
"auth_user"."last_name", 
"auth_user"."email", 
"auth_user"."is_staff", 
"auth_user"."is_active", 
"auth_user"."date_joined" 
FROM "auth_user" 
WHERE "auth_user"."id" = 7 
LIMIT 21;

INSERT INTO "geo_points" ("title", "location", "created_at") 
VALUES ('A', '0101000020e61000000f0c207c28cf42407aa86dc328e04b40'::geography, '2026-02-09 13:15:15.207395+00:00'::timestamptz) RETURNING "geo_points"."id";

```

## create_message

- **request**: `POST /api/points/messages/`
- **status**: `201`
- **store_id**: `afb0d0e6a7b04c3d9dcf05613460dcd8`
- **sql_count**: `3`

```sql
SELECT "auth_user"."id", 
"auth_user"."password", 
"auth_user"."last_login", 
"auth_user"."is_superuser", 
"auth_user"."username", 
"auth_user"."first_name", 
"auth_user"."last_name", 
"auth_user"."email", 
"auth_user"."is_staff", 
"auth_user"."is_active", 
"auth_user"."date_joined" 
FROM "auth_user" 
WHERE "auth_user"."id" = 7 
LIMIT 21;

SELECT "geo_points"."id" 
FROM "geo_points" 
WHERE "geo_points"."id" = 7 
ORDER BY "geo_points"."id" ASC 
LIMIT 1;

INSERT INTO "geo_messages" ("point_id", "author_id", "text", "created_at") 
VALUES (7, 7, 'hello', '2026-02-09 13:15:15.313590+00:00'::timestamptz) RETURNING "geo_messages"."id";

```

## search_points

- **request**: `GET /api/points/search/?latitude=55.751244&longitude=37.618423&radius=2`
- **status**: `200`
- **store_id**: `31dd3ffa5344408eae5d22983e193327`
- **sql_count**: `4`

```sql
SELECT "auth_user"."id", 
"auth_user"."password", 
"auth_user"."last_login", 
"auth_user"."is_superuser", 
"auth_user"."username", 
"auth_user"."first_name", 
"auth_user"."last_name", 
"auth_user"."email", 
"auth_user"."is_staff", 
"auth_user"."is_active", 
"auth_user"."date_joined" 
FROM "auth_user" 
WHERE "auth_user"."id" = 7 
LIMIT 21;

SELECT "spatial_ref_sys"."srid", 
"spatial_ref_sys"."auth_name", 
"spatial_ref_sys"."auth_srid", 
"spatial_ref_sys"."srtext", 
"spatial_ref_sys"."proj4text" 
FROM "spatial_ref_sys" 
WHERE "spatial_ref_sys"."srid" = 4326 
LIMIT 21;

SELECT COUNT(*) AS "__count" 
FROM "geo_points" 
WHERE ST_DWithin("geo_points"."location", '0101000020e61000000f0c207c28cf42407aa86dc328e04b40'::geometry, 2000.0);

SELECT "geo_points"."id", 
"geo_points"."title", 
"geo_points"."location", 
"geo_points"."created_at" 
FROM "geo_points" 
WHERE ST_DWithin("geo_points"."location", '0101000020e61000000f0c207c28cf42407aa86dc328e04b40'::geometry, 2000.0) 
ORDER BY "geo_points"."id" ASC 
LIMIT 7;

```

## search_messages

- **request**: `GET /api/points/messages/search/?latitude=55.751244&longitude=37.618423&radius=2`
- **status**: `200`
- **store_id**: `82e113ddf9d44dddbc75db1b84e9ba38`
- **sql_count**: `3`

```sql
SELECT "auth_user"."id", 
"auth_user"."password", 
"auth_user"."last_login", 
"auth_user"."is_superuser", 
"auth_user"."username", 
"auth_user"."first_name", 
"auth_user"."last_name", 
"auth_user"."email", 
"auth_user"."is_staff", 
"auth_user"."is_active", 
"auth_user"."date_joined" 
FROM "auth_user" 
WHERE "auth_user"."id" = 7 
LIMIT 21;

SELECT COUNT(*) AS "__count" 
FROM "geo_messages" 
INNER JOIN "geo_points" 
ON ("geo_messages"."point_id" = "geo_points"."id") 
WHERE ST_DWithin("geo_points"."location", '0101000020e61000000f0c207c28cf42407aa86dc328e04b40'::geometry, 2000.0);

SELECT "geo_messages"."id", 
"geo_messages"."point_id", 
"geo_messages"."author_id", 
"geo_messages"."text", 
"geo_messages"."created_at", 
"auth_user"."id", 
"auth_user"."username" 
FROM "geo_messages" 
INNER JOIN "geo_points" 
ON ("geo_messages"."point_id" = "geo_points"."id") 
INNER JOIN "auth_user" 
ON ("geo_messages"."author_id" = "auth_user"."id") 
WHERE ST_DWithin("geo_points"."location", '0101000020e61000000f0c207c28cf42407aa86dc328e04b40'::geometry, 2000.0) 
ORDER BY "geo_messages"."id" ASC 
LIMIT 7;

```

