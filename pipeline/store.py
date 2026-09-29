"""추출 결과 저장소 (SQLite).

cache_key = content_type + 본문 + 모델 + 프롬프트 지문. 같은 키가 성공 상태로 있으면 다시 호출하지 않는다.
taxonomy 버전과 가이드 문구가 프롬프트 지문에 들어가 있으므로, 분류 체계가 바뀌면 자연히 재추출 대상이 된다.
분석은 DuckDB 등에서 이 파일을 그대로 읽으면 된다.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

from pipeline.taxonomy import REPO_ROOT

DEFAULT_DB = REPO_ROOT / "pipeline" / "out" / "extractions.sqlite"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS extractions (
    cache_key         TEXT PRIMARY KEY,
    item_id           TEXT NOT NULL,
    source            TEXT NOT NULL,
    content_type      TEXT NOT NULL,
    model             TEXT NOT NULL,
    taxonomy_version  TEXT NOT NULL,
    prompt_version    TEXT NOT NULL,
    prompt_fp         TEXT NOT NULL,
    status            TEXT NOT NULL,          -- ok | error
    labels            TEXT,                   -- JSON
    issues            TEXT,                   -- JSON list
    language          TEXT,                   -- 규칙 기반 (LLM 아님)
    error             TEXT,
    prompt_tokens     INTEGER,
    cached_tokens     INTEGER,
    completion_tokens INTEGER,
    latency_ms        REAL,
    attempts          INTEGER,
    created_at        TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_extractions_run ON extractions (model, prompt_fp, source);
"""


def cache_key(content_type: str, text: str, model: str, prompt_fp: str) -> str:
    return hashlib.sha256("\x1f".join([content_type, text, model, prompt_fp]).encode()).hexdigest()


class Store:
    def __init__(self, path: Path = DEFAULT_DB):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)

    def done_keys(self, keys: list[str]) -> set[str]:
        found: set[str] = set()
        for i in range(0, len(keys), 500):
            chunk = keys[i : i + 500]
            rows = self.conn.execute(
                f"SELECT cache_key FROM extractions WHERE status = 'ok' AND cache_key IN ({','.join('?' * len(chunk))})",
                chunk,
            )
            found.update(r[0] for r in rows)
        return found

    def upsert(self, row: dict) -> None:
        row = {**row}
        for k in ("labels", "issues"):
            if row.get(k) is not None:
                row[k] = json.dumps(row[k], ensure_ascii=False)
        cols = ", ".join(row)
        self.conn.execute(
            f"INSERT OR REPLACE INTO extractions ({cols}) VALUES ({', '.join('?' * len(row))})",
            list(row.values()),
        )
        self.conn.commit()

    def fetch(self, keys: list[str]) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i in range(0, len(keys), 500):
            chunk = keys[i : i + 500]
            for r in self.conn.execute(
                f"SELECT * FROM extractions WHERE cache_key IN ({','.join('?' * len(chunk))})", chunk
            ):
                d = dict(r)
                d["labels"] = json.loads(d["labels"]) if d["labels"] else None
                d["issues"] = json.loads(d["issues"]) if d["issues"] else []
                out[d["cache_key"]] = d
        return out
