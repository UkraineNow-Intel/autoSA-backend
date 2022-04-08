from celery import Celery
from celery.schedules import crontab

app = Celery("website")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # schedule a dummy task to run every minute:
    # import api.tasks
    # sender.add_periodic_task(
    #     crontab(minute="*", hour="*"), api.tasks.dummy_task.s("hello"), name="api.tasks.dummy_task"
    # )
    pass
