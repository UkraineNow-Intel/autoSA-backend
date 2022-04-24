Default: run

black:
	black --check .
flake8:
	flake8 .
test:
	py.test -v
lint:
	flake8 .
migrate:
	python manage.py migrate
	python manage.py migrate django_celery_beat
run:
	@python manage.py runserver
