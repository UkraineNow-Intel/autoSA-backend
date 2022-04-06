# AutoSA (Automated Situational Awareness) Backend

This is the repo of the AutoSA team. It is deployed on AWS using Django.

There is an internal list of commonly used sources for intelligence - in the repo, we will access these sources to make information more accessible (e.g. searchable, filtered or mapped (#future)) for the intelligence team.

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

Request a review on your PR before merging. 

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
