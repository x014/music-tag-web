import os
import sys
import pytest
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_vue_cli.settings_test')

import django
django.setup()

from django.contrib.auth.models import User
from django.core.management import call_command


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command('migrate', '--run-syncdb', verbosity=0)


@pytest.fixture
def test_user(db):
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={
            'password': 'testpass123',
            'email': 'test@test.com'
        }
    )
    yield user


@pytest.fixture
def admin_user(db):
    user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'password': 'admin123',
            'email': 'admin@test.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    yield user


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, test_user):
    api_client.force_authenticate(user=test_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client
