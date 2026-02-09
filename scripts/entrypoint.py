from __future__ import annotations

import os
import subprocess
import sys
import time

import psycopg


def wait_for_postgres() -> None:
    host = os.getenv("DB_HOST")
    if not host:
        return

    port = int(os.getenv("DB_PORT", "5432"))
    dbname = os.getenv("DB_NAME", "geo_points")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")

    deadline = time.time() + 60
    last_err: Exception | None = None

    print(f"Waiting for Postgres at {host}:{port}...")
    while time.time() < deadline:
        try:
            conn = psycopg.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password,
                connect_timeout=2,
            )
            conn.close()
            return
        except Exception as exc:
            last_err = exc
            time.sleep(1)

    raise SystemExit(f"Postgres is not ready: {last_err}")


def maybe_run_migrations(argv: list[str]) -> None:
    """
    Запускаем миграции только для обычного веб-запуска (docker compose up),
    но не для одноразовых команд типа pytest/ruff/black/pre-commit.
    """
    if os.getenv("RUN_MIGRATIONS", "0") != "1":
        return

    if not argv:
        return
    first = os.path.basename(argv[0])
    if first in {"pytest", "ruff", "black", "pre-commit", "python"}:
        return

    subprocess.check_call([sys.executable, "manage.py", "migrate", "--noinput"])


def main() -> None:
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit("No command provided")

    wait_for_postgres()
    maybe_run_migrations(argv)

    os.execvp(argv[0], argv)


if __name__ == "__main__":
    main()
