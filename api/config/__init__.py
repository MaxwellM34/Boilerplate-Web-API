"""Configuration helpers for the base API service."""

import os

from dotenv import load_dotenv

# Prefer repo .env over pre-set environment variables to avoid stale values.
load_dotenv(override=True)

def _get_env() -> str:
    return os.getenv("ENV", "local").strip().lower()


_env = _get_env()

if _env == "cloud":
    from .cloud import CloudConfig as Config
else:
    from .local import LocalConfig as Config

__all__ = ["Config"]
