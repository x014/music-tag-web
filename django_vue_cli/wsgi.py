"""
WSGI config for  task.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_vue_cli.settings')

if os.getenv("dockerrun", "no") == "yes":
    from component.mysql_pool import patch_mysql
    from gevent import monkey
    monkey.patch_all(thread=False)
    patch_mysql()

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
