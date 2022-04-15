Default: run

black:
	black --check .
flake8:
	flake8 .
test:
	py.test -v
lint:
	flake8 .

run:
	@python manage.py runserver
