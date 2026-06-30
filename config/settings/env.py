import os
from pathlib import Path

from dotenv import load_dotenv
from typing import Any, Callable


BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


def env(key: str, default: Any=None, cast: Callable[[Any], Any]=str):
    value = os.getenv(key, default)

    if value is None:
        return None
    if cast is bool:
        return str(value).strip().lower() in {"1", "true", "yes", "on"}
    if cast is list:
        return [item.strip() for item in str(value).split(",") if item.strip()]

    return cast(value)


def database_config():
    return {
        "ENGINE": env("POSTGRES_ENGINE", "django.db.backends.postgresql"),
        "NAME": env("POSTGRES_DB", "cork"),
        "USER": env("POSTGRES_USER", "cork"),
        "PASSWORD": env("POSTGRES_PASSWORD", "corkpass"),
        "HOST": env("POSTGRES_HOST", "localhost"),
        "PORT": env("POSTGRES_PORT", "5432"),
        "CONN_MAX_AGE": env("POSTGRES_CONN_MAX_AGE", 60, int),
    }
