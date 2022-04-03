Default: run

black:
	black --check .
pycodestyle:
	pycodestyle .
flake8:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --extend-ignore E203 --statistics
test:
	@python manage.py test --verbosity 2

run:
	@python manage.py runserver
