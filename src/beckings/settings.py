import sys
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("DJANGO_SECRET_KEY", default="")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DJANGO_DEBUG", cast=bool, default=False)

ALLOWED_HOSTS = ["beckings-production.up.railway.app", "localhost", "127.0.0.1", "0.0.0.0"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.up.railway.app",
    "https://*.railway.app",
    "https://beckings-production.up.railway.app"
]

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = not DEBUG

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "django.contrib.humanize",
    "django.contrib.syndication",
    "django.contrib.postgres",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken", # Later drf-something
    "django_cotton",
    "django_htmx",
    "tailwind",
]

INTERNAL_APPS = [
    "theme",
    "products",
    "clients",
]

INSTALLED_APPS = list(set(DJANGO_APPS) | set(THIRD_PARTY_APPS) | set(INTERNAL_APPS))

TAILWIND_APP_NAME = "theme"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    # HTMX
    "django_htmx.middleware.HtmxMiddleware",
]


ROOT_URLCONF = "beckings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                
                "helpers.context_processors.default_price",
            ],
            "builtins": [
                "django.templatetags.static",
                "django.templatetags.i18n",
                "tailwind.templatetags.tailwind_tags",
                "helpers.templatetags.utils",
            ]
        },
    },
]

WSGI_APPLICATION = "beckings.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    import dj_database_url # noqa
    DATABASES["default"] = dj_database_url.config(default=DATABASE_URL)

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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


AUTHENTICATION_BACKENDS = [
    # default
    "django.contrib.auth.backends.ModelBackend",
    
    # email
    "clients.backends.EmailBackend"
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

STATIC_DIR = BASE_DIR / "static"

STATIC_DIR.mkdir(exist_ok=True)

STATICFILES_DIRS = [
    STATIC_DIR
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SITE_ID = config("SITE_ID", cast=int, default=1)

# Windows
if sys.platform.startswith("win"):

    NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"

DEFAULT_PRICE_CURRENCY = "₦"
SITE_ADMIN_NAME = config("SITE_ADMIN_NAME", default="")
# Email
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail"
EMAIL_HOST_USER = config("EMAIL_USERNAME", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_PASSWORD", default="")
EMAIL_USE_TLS = True
EMAIL_PORT = 568

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Admin

ADMINS = [
    (SITE_ADMIN_NAME, EMAIL_HOST_USER)
]


# Rest framework

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication"
    ],

}
