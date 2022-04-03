Default: run

black:
	black --check .
pycodestyle:
	pycodestyle .
flake8:
	flake8 .
test:
	@python manage.py test --verbosity 2

run:
	@python manage.py runserver
