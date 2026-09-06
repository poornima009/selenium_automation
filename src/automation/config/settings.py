from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _as_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str
    username: str
    password: str
    site_name: str
    headless: bool
    default_timeout_ms: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(_project_root() / ".env")

    base_url = os.getenv("BASE_URL", "https://demosso.nyggs.com/").rstrip("/") + "/"
    username = os.getenv("SSO_USERNAME") or os.getenv("USERNAME", "")
    password = os.getenv("SSO_PASSWORD") or os.getenv("PASSWORD", "")
    if not username or not password:
        raise ValueError("SSO_USERNAME and SSO_PASSWORD must be set in the environment or .env")

    return Settings(
        base_url=base_url,
        username=username,
        password=password,
        site_name=os.getenv("SITE_NAME", "Demo"),
        headless=_as_bool(os.getenv("HEADLESS", "true")),
        default_timeout_ms=int(os.getenv("DEFAULT_TIMEOUT_MS", "30000")),
    )
