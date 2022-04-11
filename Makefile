Default: run

black:
	black --check .
pycodestyle:
	pycodestyle .
flake8:
	flake8 .
test:
	py.test -v
lint:
	pycodestyle .
	flake8 .

run:
	@python manage.py runserver
