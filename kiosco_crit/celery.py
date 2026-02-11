import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kiosco_crit.settings")

app = Celery("kiosco_crit")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
