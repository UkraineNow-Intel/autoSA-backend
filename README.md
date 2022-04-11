# AutoSA (Automated Situational Awareness) Backend

This is the repo of the AutoSA team. It is deployed on AWS using Django.

There is an internal list of commonly used sources for Intelligence Analysts who are helping people on the ground exfiltrate. We will access these sources to make information more accessible (e.g. searchable, filtered or mapped (#future)) for the intelligence team.

Current tasks can be found in Projects, but also feel free to ask in our group chat if you need any assistance.

## Requirements

- python==3.8.10 through python==3.9.9

## How do I get set up? ###

1. Install requirements

```shell
pip install -r requirements.txt -r requirements-dev.txt -U --upgrade-strategy only-if-needed
```

2. (Optional, for location parsing): Install Spacy language models:

```shell
python -m spacy download en_core_web_sm ru_core_news_sm
```

4. Run migrations

```shell
python manage.py migrate
```

5. Create a user that can log in to the website. You will be prompted for password:

```shell
python manage.py createsuperuser --email admin@example.com --username admin
```

## Start Django Server

```shell
python manage.py runserver
```

## Background tasks

To schedule background tasks, we use [Celery](https://docs.celeryq.dev/en/stable/index.html), [django-celery-beat](https://django-celery-beat.readthedocs.io/en/latest/), and [Redis](https://redis.io).

Note: `django-celery-beat` is included in `requirements.txt`, but after it's installed, you also need to run migrations:

```python manage.py migrate django_celery_beat```

If you're working on background tasks, such as [api tasks](api/tasks.py), you'll also have to [install Redis](https://redis.io/docs/getting-started/#install-redis) and run three additional processes:

* Redis, for storing tasks and exchanging messages.
* Celery worker(s), for performing tasks.
* Celery beat, for scheduling tasks.

You can run them in separate terminal windows (or tabs in screen session).

For exact commands see [Procfile.dev](Procfile.dev).

Note: Django does not know how to use a `Procfile` (Heroku does). I added it here only for documenting commands that we need for `dev` and `prod`.

There is one example task in [api/tasks.py](api/tasks.py).

It is scheduled (commented out) in [website/celery.py](website/celery.py).

### Contribution guidelines ###

* Writing tests

Tests should go in the `tests` directory.

We suggest using `pytest`.

Run all tests with:

```shell
make test
```

Or, to be more selective, use:

```shell
python manage.py test [PATH] [OPTIONS...]
```

* Code review

We use `black` to enforce the uniform coding style. Run `black .` before submitting a PR.

Before you commit, please:

```shell
make black
make lint
```

Request a review on your PR before merging. 

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
