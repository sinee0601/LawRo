"""bench 스크립트 공용 헬퍼 — 운영 설정을 그대로 읽어 경로/모델/임계값을 한 곳에서 해석한다."""

import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"


def load_env() -> None:
    load_dotenv(BACKEND_ROOT / ".env")


def load_settings():
    """backend/app/config.py 의 Settings 를 그대로 사용한다(값 이중 정의 방지)."""
    if str(BACKEND_ROOT) not in sys.path:
        sys.path.insert(0, str(BACKEND_ROOT))
    from app.config import settings

    return settings


def resolve_persist_dir(settings) -> Path:
    """CHROMA_PERSIST_DIRECTORY 는 backend/ 를 기준으로 한 상대경로다."""
    raw = Path(settings.CHROMA_PERSIST_DIRECTORY)
    if raw.is_absolute():
        return raw
    return (BACKEND_ROOT / raw).resolve()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"
