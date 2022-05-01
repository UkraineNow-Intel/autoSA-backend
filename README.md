# AutoSA (Automated Situational Awareness) Backend

This is the repo of the AutoSA team. It is deployed on AWS using Django.

There is an internal list of commonly used sources for Intelligence Analysts who are helping people on the ground exfiltrate. We will access these sources to make information more accessible (e.g. searchable, filtered or mapped (#future)) for the intelligence team.

Current tasks can be found in Projects, but also feel free to ask in our group chat if you need any assistance.

## How do I get set up? ###

### VS Code: fully Dockerized development
All components (Django, DB, Redis) reside in Docker containers.
The container having Django in it is called development container. It plays the role of development environment, and thus will have all the required tools and dependencies (Python, Postgres client libs etc).
> :warning: This approach doesn't run Celery scheduler and workers. Such support can be added though!

Requirements:
- Docker to run containers
- VS Code to manage the development container

To start development, open the project as a remote containers project in VS Code. Check [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers) for more information.

VS Code will automatically run migrations inside developement container to get Djagno database created (see [devcontainer.json](.devcontainer/devcontainer.json) to know more).

Once the development container is up and running, VS Code will spawn a shell inside of it. Please refer to [Start Django Server](#start-django-server) to learn what to do next.

PostgreSQL and Redis services will be accessible via `5432` and `6379` TCP ports of localhost interface.

### Local development with Dockerized dependencies
This approach still leverages Docker containers for dependencies, but local development happens at the host machine.

> :warning: This approach doesn't run Celery scheduler and workers. Such support can be added though!

Requirements:
- Docker to run dependency containers
- Configred local development (Python, Postgres libs etc)

To start containers of the dependcies, run:
```shell
docker compose up
```

PostgreSQL and Redis services will be accessible via `5432` and `6379` TCP ports of localhost interface.

To configure local development environment, please check the relevant parts below.

### Local development with locally installed dependencies

#### Requirements

- python==3.8.10 through python==3.9.9

We have scripts to help with installation:

```shell
# create Postgresql database and user
./scripts/install_database.sh

# install required OS and Python packages, run migrations
./scripts/install.sh
```

Optional steps that are not included in those scripts:

It's always a good idea to create a virtualenv for every repository.

If you're already using conda, pyenv or pipenv, you know how to create one.

Or just create one with python + virtualenv:

```shell
python3 -m venv ~/.venvs/autosa-backend
```

Then activate it:

```shell
source ~/.venvs/autosa-backend/bin/activate
```

1. Now you can install requirements into the venv:
It's always a good idea to create a virtualenv for every repository.

If you're already using conda, pyenv or pipenv, you know how to create one.

Or just create one with python + virtualenv:

```shell
python3 -m venv ~/.venvs/autosa-backend
```

Then activate it:

```shell
source ~/.venvs/autosa-backend/bin/activate
```

1. Now you can install requirements into the venv:

```shell
pip install -r requirements.txt -r requirements-dev.txt -U --upgrade-strategy only-if-needed
```

2. (Optional, for location parsing): Install Spacy language models:

```shell
python -m spacy download en_core_web_sm ru_core_news_sm
```

2. Create a user that can log in to the website. You will be prompted for password:

```shell
python manage.py createsuperuser --email admin@example.com --username admin
```

3. If you will be calling API refresh method, you need to initialize the client session. Unfortunately, this has to be done interactively. Run the Telegram script and answer the prompts to create a session file: 

```shell
PYTHONPATH=. python /Users/irinatruong/src/autoSA-backend/infotools/telegram/telegram.py
```

You also need `TELEGRAM_*` settings in `.env.` file.

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

### Pre-commit hooks

We have some pre-commit hooks to safeguard the repository from unintended changes. Make sure you install those.

```shell
pip install pre-commit
pre-commit install
```

### Writing tests

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
