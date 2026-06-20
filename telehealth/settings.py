from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    # local apps
    "authentication",
    "patients",
    "consoltants",
    "base",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "telehealth.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "telehealth.wsgi.application"

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "Telehealth",
        "USER": "postgres",
        "PASSWORD": "root",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"

# JWT configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(
        hours=1
    ),  # The access token (used to authenticate API requests) expires after 1 hour.
    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=7
    ),  # The refresh token lives for 7 days. It's used to get a new access token without re-logging in.
    "ROTATE_REFRESH_TOKENS": True,
    # Every time you use a refresh token to get a new access token, you also get a brand new refresh token. The old one becomes invalid.
    "BLACKLIST_AFTER_ROTATION": True,
    # Works with the above — the old refresh token is added to a blacklist so it can't be reused, even if someone intercepts it.
    "UPDATE_LAST_LOGIN": True,  # Updates the last_login field in the User model every time someone logs in via JWT.
}
AUTH_USER_MODEL = "authentication.User"
REST_FRAMEWORK = {
    # Tells Django how to verify who the user is. Here it uses JWT — so when a request comes in, DRF checks the Authorization: Bearer <token> header to identify the user.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Tells Django who is allowed in. IsAuthenticated means every API endpoint is blocked by default unless the user is logged in. You can override this per view.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # When an endpoint returns a list (e.g. all users), it won't dump everything at once. It splits results into pages of 20 and you navigate with ?page=1, ?page=2 etc.
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Controls the format of API responses. JSONRenderer means all responses come back as JSON only — no browsable HTML API.
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer"

    ],
    # Rate limiting — prevents abuse/spam of your API.
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",  # limits unauthenticated users
        "rest_framework.throttling.UserRateThrottle",  # limits logged-in users
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "10/min",
        "user": "60/min",
    },
}

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://localhost:8000",  # Django itself
]
# Allows the browser to send cookies and auth headers (like your JWT tokens) along with cross-origin requests.
CORS_ALLOW_CREDENTIALS = True
