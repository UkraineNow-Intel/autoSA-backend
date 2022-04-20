from .base import *

SECRET_KEY = "abc"

DEBUG = True

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://localhost:3000"]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True

STATICFILES_DIRS = [BASE_DIR / "static"]

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"

MEDIA_ROOT = BASE_DIR / "media"
