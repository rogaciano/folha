"""
Development settings for folha_pagamento project.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'folha.sistema9.com.br']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Django Browser Reload (Development only)
INSTALLED_APPS += ['django_browser_reload']
MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware']

# Email Backend - Console for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files - Development
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Security Settings - Development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
