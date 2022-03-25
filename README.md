# AutoSA (Automated Situational Awareness) Backend

This is the repo of the AutoSA team. It is deployed on AWS using flask, gunicore & nginx.

There is an internal list of commonly used sources for intelligence - in the repo, we will access these sources to make information more accessible (e.g. mapped or searchable) for the intelligence team.

Current tasks can be found on Jira, but also feel free to ask in our group chat if you need any assistance.

## Requirements
- python==3.8.10 through python==3.9.9

## How do I get set up? ###

1. Install requirements

`pip install -r requirements.txt -r requirements-dev.txt -U --upgrade-strategy only-if-needed`

2. Configure Server by copying server.config.default file
`cp server.config.default server.config`

3. Run server
`python flaskapp.py`

For gunicore, the wsgi file can be used to run the server.

There are other parts in this repository that will slowly be added to the flaskapp and are therefore not explained in the readme (yet).

## Start Django Server

```
python manage.py runserver
```

### Contribution guidelines ###

* Writing tests

Tests should go in the `tests` directory.

We suggest using `pytest`.

* Code review

We use `black` to enforce the uniform coding style.

Request a review on your PR before merging. 

* Other guidelines

TBD

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact