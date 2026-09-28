import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

from .local_settings import (
    SECRET_KEY,
    DEBUG,
    ALLOWED_HOSTS,
    DB_CONFIG,
    TEMPLATES_DIR,
    STATICFILES_DIR,
    STATIC_DIR,
    MEDIA_DIR,
    LOGS_DIR,
)

from ASMS.logging import LOGGING as DJANGO_LOGGING

# ==============================================================================
# Paths
# ==============================================================================

SETTINGS_DIR = Path(__file__).resolve().parent
BASE_DIR = SETTINGS_DIR.parent

LOGS_DIR = Path(os.getenv("LOGS_DIR", LOGS_DIR))
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# Core
# ==============================================================================

SECRET_KEY = SECRET_KEY

DEBUG = DEBUG

ALLOWED_HOSTS = ALLOWED_HOSTS

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1",
    "http://localhost",
    "https://*.ngrok-free.app",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ==============================================================================
# Applications
# ==============================================================================

INSTALLED_APPS = [
    "jazzmin",
    "django_extensions",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
     "django_browser_reload",

    "ASMS",
    "Home",
    "product",
    "TrialItem",
]

# ==============================================================================
# Middleware
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
     "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "ASMS.urls"

# ==============================================================================
# Templates
# ==============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
         "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",  # internationalization context processor
            ],
        },
    },
]

WSGI_APPLICATION = "ASMS.wsgi.application"

# ==============================================================================
# Database
# ==============================================================================

DATABASES = {
    "default": DB_CONFIG,
}

# ==============================================================================
# Password Validation
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ==============================================================================
# Internationalization
# ==============================================================================

# Language settings
LANGUAGE_CODE = 'en'  # English
TIME_ZONE = 'Asia/Shanghai'  # Optional: Set timezone to China
USE_I18N = True
USE_TZ = True


# ==============================================================================
# Languages
# ==============================================================================

LANGUAGES = [
    ('en', _('English')),
    ('zh-hans', _('Simplified Chinese')),
]


# ==============================================================================
# Locale
# ==============================================================================

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]


# ==============================================================================
# Static & Media
# ==============================================================================

STATIC_URL = "/static/"

STATIC_ROOT = STATIC_DIR

STATICFILES_DIRS = [
    STATICFILES_DIR,
]

MEDIA_URL = "/media/"

MEDIA_ROOT = MEDIA_DIR

# ==============================================================================
# Logging
# ==============================================================================

LOGGING = DJANGO_LOGGING

# ==============================================================================
# Default Primary Key
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================================================================
# Authentication
# ==============================================================================

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# ==============================================================================
# Jazzmin
# ==============================================================================

JAZZMIN_SETTINGS = {
    "site_title": "ASMA",
    "site_header": "ASMA",
    "site_brand": "ASMA",
    "welcome_sign": "Welcome to the ASMA Management System",
    "copyright": "Pyxis ASMA",
    "user_avatar": None,
}



