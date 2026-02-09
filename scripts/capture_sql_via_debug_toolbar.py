from __future__ import annotations

import argparse
import html as htmllib
import http.client
import json
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class StepResult:
    name: str
    method: str
    path: str
    status: int
    store_id: str | None
    sql_queries: list[str]


_RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}")
_RE_PBKDF2 = re.compile(r"pbkdf2_sha256\$\d+\$[^']+")
_RE_GEN_USERNAME = re.compile(r"u_[0-9a-f]{6,32}")


def _sanitize_sql(sql: str) -> str:
    """
    Убираем чувствительные литералы (токены/хэши/генерируемые username),
    чтобы файл можно было безопасно хранить в репозитории.
    """
    sql = _RE_JWT.sub("<redacted_jwt>", sql)
    sql = _RE_PBKDF2.sub("<redacted_password_hash>", sql)
    sql = _RE_GEN_USERNAME.sub("<generated_username>", sql)
    return sql


def _http_request(
    conn: http.client.HTTPConnection,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
) -> tuple[int, dict[str, str], bytes]:
    hdrs = dict(headers or {})
    body: bytes | None = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
        hdrs["Content-Length"] = str(len(body))
    conn.request(method, path, body=body, headers=hdrs)
    resp = conn.getresponse()
    data = resp.read()
    return resp.status, dict(resp.getheaders()), data


def _wait_for_http(conn: http.client.HTTPConnection, path: str, *, timeout_s: float = 30.0) -> None:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            status, _, _ = _http_request(conn, "GET", path, headers={"Connection": "keep-alive"})
            if 200 <= status < 500:
                return
        except Exception as exc:
            last_err = exc
        time.sleep(0.5)
    raise SystemExit(f"Server is not ready at {path}: {last_err}")


def _debug_history_refresh(conn: http.client.HTTPConnection) -> list[dict[str, Any]]:
    status, _, data = _http_request(
        conn,
        "GET",
        "/__debug__/history_refresh/?store_id=dummy&exclude_history=1",
        headers={"Connection": "keep-alive"},
    )
    if status != 200:
        raise RuntimeError(f"history_refresh status={status} body={data[:2000]!r}")
    payload = json.loads(data.decode("utf-8"))
    return payload.get("requests", [])


def _pick_new_store_id(prev: set[str], current: list[dict[str, Any]]) -> str | None:
    ids = [r.get("id") for r in current if r.get("id")]
    for sid in reversed(ids):
        if sid not in prev:
            return sid
    return None


def _extract_sql_queries_from_sqlpanel(content_html: str) -> list[str]:
    spans = re.findall(
        r'<span class="djDebugCollapsed[^>]*>(.*?)</span>',
        content_html,
        flags=re.DOTALL,
    )
    queries: list[str] = []
    for s in spans:
        s = s.replace("<br/>", "\n").replace("<br />", "\n")
        s = re.sub(r"&nbsp;?", " ", s)
        s = re.sub(r"<[^>]+>", " ", s)
        s = htmllib.unescape(s)
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n\s*", "\n", s).strip()
        if s.upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
            queries.append(s)
    return queries


def _debug_render_sql_panel(conn: http.client.HTTPConnection, store_id: str) -> list[str]:
    status, _, data = _http_request(
        conn,
        "GET",
        f"/__debug__/render_panel/?store_id={store_id}&panel_id=SQLPanel",
        headers={"Connection": "keep-alive"},
    )
    if status != 200:
        raise RuntimeError(f"render_panel status={status} body={data[:2000]!r}")
    payload = json.loads(data.decode("utf-8"))
    content_html = payload.get("content", "")
    return _extract_sql_queries_from_sqlpanel(content_html)


def _format_markdown(results: list[StepResult]) -> str:
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    parts: list[str] = []
    parts.append("# SQL capture (django-debug-toolbar)\n\n")
    parts.append(f"- **generated_at**: `{ts}`\n")
    parts.append(
        "- **source**: debug-toolbar History (`/__debug__/history_refresh`) + "
        "`/__debug__/render_panel/?panel_id=SQLPanel`\n"
    )
    parts.append(
        "- **note**: токены/хэши/служебные литералы в SQL могут быть замаскированы "
        "как `<redacted_...>`.\n\n"
    )

    parts.append("## Summary\n\n")
    parts.append("| step | request | status | sql_count |\n")
    parts.append("| --- | --- | ---: | ---: |\n")
    for r in results:
        parts.append(
            f"| `{r.name}` | `{r.method} {r.path}` | `{r.status}` | `{len(r.sql_queries)}` |\n"
        )
    parts.append("\n")

    for r in results:
        parts.append(f"## {r.name}\n\n")
        parts.append(f"- **request**: `{r.method} {r.path}`\n")
        parts.append(f"- **status**: `{r.status}`\n")
        parts.append(f"- **store_id**: `{r.store_id}`\n")
        parts.append(f"- **sql_count**: `{len(r.sql_queries)}`\n")
        if r.sql_queries:
            parts.append("\n```sql\n")
            for q in r.sql_queries:
                parts.append(_sanitize_sql(q.rstrip()) + ";\n\n")
            parts.append("```\n")
        else:
            parts.append("\n_SQL не зафиксирован (или запрос не попал в History)._ \n")
        parts.append("\n")

    return "".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture SQL per endpoint via django-debug-toolbar History + SQLPanel render.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of running server (debug-toolbar must be enabled).",
    )
    parser.add_argument(
        "--out",
        default="SQL_CAPTURE.md",
        help="Output markdown file path.",
    )
    args = parser.parse_args()

    parsed = urlparse(args.base_url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit("Only http/https base urls are supported.")
    if parsed.scheme == "https":
        raise SystemExit("HTTPS is not supported by this script (use http).")

    host = parsed.hostname or "localhost"
    port = parsed.port or 80

    conn = http.client.HTTPConnection(host, port, timeout=30)
    seen_store_ids: set[str] = set()

    _wait_for_http(conn, "/api/docs/", timeout_s=30.0)
    _http_request(conn, "GET", "/api/docs/", headers={"Connection": "keep-alive"})
    seen_store_ids.update(r["id"] for r in _debug_history_refresh(conn) if r.get("id"))

    username = f"u_{uuid.uuid4().hex[:10]}"
    password = "S0mething-Longer_123"

    results: list[StepResult] = []

    def run_step(
        name: str,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> tuple[int, bytes, list[str]]:
        status, _, data = _http_request(
            conn,
            method,
            path,
            json_body=json_body,
            headers={"Connection": "keep-alive", **(headers or {})},
        )
        hist = _debug_history_refresh(conn)
        new_id = _pick_new_store_id(seen_store_ids, hist)
        if new_id is not None:
            seen_store_ids.add(new_id)
            sql = _debug_render_sql_panel(conn, new_id)
        else:
            sql = []
        results.append(StepResult(name, method, path, status, new_id, sql))
        return status, data, sql

    run_step(
        "register",
        "POST",
        "/api/auth/register/",
        json_body={"username": username, "password": password},
    )
    status, data, _ = run_step(
        "token", "POST", "/api/auth/token/", json_body={"username": username, "password": password}
    )
    if status != 200:
        raise SystemExit(f"token request failed: status={status} body={data[:500]!r}")

    access = json.loads(data.decode("utf-8"))["access"]
    authz = {"Authorization": f"Bearer {access}"}

    status, data, _ = run_step(
        "create_point",
        "POST",
        "/api/points/",
        json_body={"title": " A ", "latitude": 55.751244, "longitude": 37.618423},
        headers=authz,
    )
    if status != 201:
        raise SystemExit(f"create_point failed: status={status} body={data[:500]!r}")
    point_id = json.loads(data.decode("utf-8"))["id"]

    run_step(
        "create_message",
        "POST",
        "/api/points/messages/",
        json_body={"point_id": point_id, "text": " hello "},
        headers=authz,
    )

    run_step(
        "search_points",
        "GET",
        "/api/points/search/?latitude=55.751244&longitude=37.618423&radius=2",
        headers=authz,
    )
    run_step(
        "search_messages",
        "GET",
        "/api/points/messages/search/?latitude=55.751244&longitude=37.618423&radius=2",
        headers=authz,
    )

    conn.close()

    out = _format_markdown(results)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"Wrote: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
