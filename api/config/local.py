"""Local configuration helpers."""

import os

from .base import BaseConfig, _env_flag


class LocalConfig(BaseConfig):
    """Local overrides (env file + defaults) for development."""

    PG_HOST = os.getenv("PG_HOST", "localhost")
    PG_PORT = int(os.getenv("PG_PORT", "5432"))
    PG_USER = os.getenv("PG_USER", "postgres")
    PG_PASS = os.getenv("PG_PASS", "")
    PG_DB = os.getenv("PG_DB", "postgres")
    OFFLINE_MODE = _env_flag("OFFLINE_MODE")
    DB_URL = f"postgres://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

    TORTOISE_ORM = {
        "connections": {"default": DB_URL},
        "apps": {
            "models": {
                "models": ["models", "aerich.models"],
                "default_connection": "default",
            }
        },
    }
