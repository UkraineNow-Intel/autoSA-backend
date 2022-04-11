from decouple import config
from .base import *
import os

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ["*"]

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"
STATIC_ROOT = "/home/ubuntu/application/djangostaticfiles/static/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "MYAPP": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}
