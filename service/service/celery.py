import os

from celery import Celery
from celery.signals import setup_logging

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service.settings")

app = Celery("service")

app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self, string):
    print(f"Request: {string}")
