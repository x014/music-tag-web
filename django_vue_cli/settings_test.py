from django_vue_cli.settings import *
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

IS_USE_CELERY = False

SITE_LOGIN = "false"

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

MEDIA_ROOT = os.path.join(BASE_DIR, 'test_media')

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
