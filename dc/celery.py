import os
from celery import Celery

# set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dc.settings')

app = Celery('dc')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


def backoff(attempts):
    """Return a backoff delay, in seconds, given a number of attempts.

    The delay increases very rapidly with the number of attemps:
    1, 2, 4, 8, 16, 32, ...

    """
    return 2 ** attempts


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
