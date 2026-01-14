"""
Production settings for folha_pagamento project.
"""
from .base import *
from decouple import config

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# CSRF Trusted Origins for Production
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='https://localhost').split(',')

# Database - PostgreSQL for production (can be overridden to SQLite in .env)
DATABASES = {
    'default': config(
        'DATABASE_URL',
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        cast=lambda v: {
            'ENGINE': config('DB_ENGINE', default='django.db.backends.postgresql'),
            'NAME': config('DB_NAME', default='folha_pagamento'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default=''),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        } if not v.startswith('sqlite') else {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    )
}

# Se DB_ENGINE for sqlite no .env, simplifica:
if config('DB_ENGINE', default='') == 'django.db.backends.sqlite3':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Static files - Production with WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security Settings - Production
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Ensure logs directory exists
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
