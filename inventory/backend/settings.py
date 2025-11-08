"""
Django settings for Asset Verification & Management System.
"""

from pathlib import Path
from datetime import timedelta
from decouple import config
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qsl
import os

# ---------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------
# Paths and core settings
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config(
    "SECRET_KEY", default="django-insecure-change-this-in-production-abc123xyz"
)

DEBUG = config("DEBUG", default=True, cast=bool)

# ---------------------------------------------------------------------
# Dynamic environment-based configuration helpers
# ---------------------------------------------------------------------
def get_list_from_env(key, default=None):
    value = config(key, default=default)
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


# ---------------------------------------------------------------------
# Hosts and security
# ---------------------------------------------------------------------
ALLOWED_HOSTS = get_list_from_env(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,.a.run.app,.lovable.dev",
)

# For HTTPS behind Cloud Run proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# ---------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "django_filters",
    "drf_yasg",
    "django_extensions",
    # Local apps
    "apps.users",
    "apps.departments",
    "apps.rbac",
    "apps.items",
    "apps.locations",
    "apps.logs",
    "apps.catalogue",
    "apps.records",
]

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ---------------------------------------------------------------------
# Database (Neon / Postgres via DATABASE_URL)
# ---------------------------------------------------------------------
tmpPostgres = urlparse(os.getenv("DATABASE_URL", ""))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tmpPostgres.path.replace("/", "") if tmpPostgres.path else "",
        "USER": tmpPostgres.username,
        "PASSWORD": tmpPostgres.password,
        "HOST": tmpPostgres.hostname,
        "PORT": tmpPostgres.port or 5432,
        "OPTIONS": dict(parse_qsl(tmpPostgres.query)),
    }
}

# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# Static and media files
# ---------------------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# Custom user model
# ---------------------------------------------------------------------
AUTH_USER_MODEL = "users.User"

# ---------------------------------------------------------------------
# REST Framework
# ---------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}

# ---------------------------------------------------------------------
# JWT Configuration
# ---------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "staff_id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------------------------------------------------------------
# CORS & CSRF (dynamic via environment)
# ---------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=False, cast=bool)

CORS_ALLOWED_ORIGINS = get_list_from_env(
    "CORS_ALLOWED_ORIGINS",
    default="https://lovable.dev,https://preview--verimana-admin-77336.lovable.app",
)

CORS_ALLOWED_ORIGIN_REGEXES = get_list_from_env(
    "CORS_ALLOWED_ORIGIN_REGEXES",
    default="^https://.*\\.lovable\\.dev$,^https://.*\\.a\\.run\\.app$",
)

CSRF_TRUSTED_ORIGINS = get_list_from_env(
    "CSRF_TRUSTED_ORIGINS",
    default="https://lovable.dev,https://*.lovable.dev,https://*.a.run.app",
)

print("CORS_ALLOWED_ORIGINS:", CORS_ALLOWED_ORIGINS)
print("CSRF_TRUSTED_ORIGINS:", CSRF_TRUSTED_ORIGINS)
print("CORS_ALLOW_ALL_ORIGINS:", CORS_ALLOW_ALL_ORIGINS)
print("CORS_ALLOWED_ORIGIN_REGEXES:", CORS_ALLOWED_ORIGIN_REGEXES)

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# ---------------------------------------------------------------------
# Swagger (DRF-YASG)
# ---------------------------------------------------------------------
SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Bearer": {"type": "apiKey", "name": "Authorization", "in": "header"}
    },
    "USE_SESSION_AUTH": False,
    "JSON_EDITOR": True,
    "DEFAULT_API_URL": config("SWAGGER_DEFAULT_API_URL", default="http://localhost:8000"),
    "SUPPORTED_SUBMIT_METHODS": ["get", "post", "put", "patch", "delete"],
}
