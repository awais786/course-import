"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

import os
from path import Path as path

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "default.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
    "read_replica": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "read_replica.db",
        "USER": "",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    },
}

GITHUB_REPO_ROOT = "course_data"

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    "openedx_filters",
    "course_import",
    'user_tasks.apps.UserTasksConfig',
)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # Ensure this is included
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Ensure this is included
    'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'course_import.urls'
COURSE_KEY_PATTERN = r'(?P<course_key_string>[^/+]+(/|\+)[^/+]+(/|\+)[^/?]+)'
COURSE_ID_PATTERN = COURSE_KEY_PATTERN.replace('course_key_string', 'course_id')

SECRET_KEY = 'insecure-secret-key'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

OPEN_EDX_FILTERS_CONFIG = {
    "org.edly.templates.fetch.requested.v1": {
        "pipeline": [
            "course_import.pipeline.GithubTemplatesPipeline",
        ],
        "fail_silently": False,
    },
}
