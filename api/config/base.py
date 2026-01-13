from __future__ import annotations

import os


def _env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


class BaseConfig:
    """Core configuration values shared by all environments."""

    API_PREFIX = os.getenv("API_PREFIX", "/api")
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    DEBUG = _env_flag("DEBUG")
    DEBUG_AUTH = _env_flag("DEBUG_AUTH")
    OFFLINE_MODE = _env_flag("OFFLINE_MODE")
    OFFLINE_ADMIN_EMAIL = os.getenv("OFFLINE_ADMIN_EMAIL", "devadmin@example.com")
    SERVER_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")
    GOOGLE_AUDIENCE = os.getenv("GOOGLE_AUDIENCE") or os.getenv("GOOGLE_CLIENT_ID")
