import os
from celery import Celery
from celery.schedules import crontab


# set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings.dev")
app = Celery("website")

app.config_from_object("django.conf:settings")
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def test(arg):
    print(arg)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(
        crontab(minute="*/15"), test.s("hello"), name="add every 10"
    )
