import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
debug_status = os.getenv('DEBUG', 'False') == 'True'
#debugging only happens locally, so if debug is true, then use settings, otherwise use prod settings
if debug_status:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bmt_gpt.settings_production')

app = Celery('bmt_gpt')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
