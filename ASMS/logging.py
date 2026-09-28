import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

BASE_DIR = Path(__file__).resolve().parent.parent

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{asctime}] [{levelname}] {name}:{lineno} - {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
        "request": {
            "format": "[{asctime}] {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },

        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "project.log",
            "formatter": "verbose",
            "level": "INFO",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },

        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "errors.log",
            "formatter": "verbose",
            "level": "ERROR",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },

        "security_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "security.log",
            "formatter": "verbose",
            "level": "WARNING",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },

        "db_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "db_queries.log",
            "formatter": "verbose",
            "level": "DEBUG",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },

        "access_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "access.log",
            "formatter": "request",
            "level": "INFO",
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },

        "django.request": {
            "handlers": ["console", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },

        "django.server": {
            "handlers": ["console", "access_file"],
            "level": "INFO",
            "propagate": False,
        },

        "django.db.backends": {
            "handlers": ["db_file"],
            "level": "DEBUG",
            "propagate": False,
        },

        "django.security": {
            "handlers": ["console", "security_file", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },

        "django.template": {
            "handlers": ["console", "error_file"],
            "level": "WARNING",
            "propagate": False,
        },

        "django.contrib": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },

        "ASMS": {
            "handlers": ["console", "file", "error_file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },

    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}