"""Cloud-ready configuration helpers."""

import os

from .base import BaseConfig, _env_flag


class CloudConfig(BaseConfig):
    """Cloud overrides for managed environments."""

    PG_GCP_PATH = os.getenv("PG_GCP_PATH")
    PG_PORT = int(os.getenv("PG_PORT", "5432"))
    PG_USER = os.getenv("PG_USER")
    PG_PASS = os.getenv("PG_PASS")
    PG_DB = os.getenv("PG_DB")
    OFFLINE_MODE = _env_flag("OFFLINE_MODE")
    DB_URL = os.getenv("DATABASE_URL")

    if DB_URL:
        TORTOISE_ORM = {
            "connections": {"default": DB_URL},
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                }
            },
        }
    else:
        TORTOISE_ORM = {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": f"/cloudsql/{PG_GCP_PATH}",
                        "port": PG_PORT,
                        "user": PG_USER,
                        "password": PG_PASS,
                        "database": PG_DB,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                }
            },
        }
