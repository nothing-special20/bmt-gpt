"""
WSGI config for bmt-gpt-saas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

debug_status = os.getenv('DEBUG', 'False') == 'True'
#debugging only happens locally, so if debug is true, then use settings, otherwise use prod settings
if debug_status:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings_production')

application = get_wsgi_application()
