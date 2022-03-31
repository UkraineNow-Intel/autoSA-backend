# AutoSA (Automated Situational Awareness) Backend

This is the repo of the AutoSA team. It is deployed on AWS using flask, gunicore & nginx.

There is an internal list of commonly used sources for intelligence - in the repo, we will access these sources to make information more accessible (e.g. mapped or searchable) for the intelligence team.

Current tasks can be found on Jira, but also feel free to ask in our group chat if you need any assistance.

## Requirements
- python==3.8.10 through python==3.9.9

## How do I get set up? ###

1. Install requirements

`pip install -r requirements.txt -r requirements-dev.txt -U --upgrade-strategy only-if-needed`


2. (Optional, for location parsing): Install Spacy language models:

`python -m spacy download en_core_web_sm ru_core_news_sm`

3. Configure Server by copying server.config.default file
`cp server.config.default server.config`

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