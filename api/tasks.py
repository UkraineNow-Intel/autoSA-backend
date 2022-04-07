from celery import shared_task


@shared_task
def dummy_task(arg):
    print(arg)
