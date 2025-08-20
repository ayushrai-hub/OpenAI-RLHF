from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-xxx'
DEBUG = True

ROOT_URLCONF = 'test_project.urls'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']

INSTALLED_APPS = [
    'test_app.apps.TestAppConfig',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_TZ = True
