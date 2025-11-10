from .settings import *  # noqa: F401,F403
from . import settings as base_settings

# Тестовая БД: SQLite (файловая)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": base_settings.BASE_DIR / "test_db.sqlite3",
    }
}

# Быстрый хешер для тестов
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Кэш в памяти, чтобы не требовать Redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "test-cache",
    }
}

# Celery: in-memory broker для тестов
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
