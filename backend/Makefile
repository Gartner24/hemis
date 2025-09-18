dev:
	FLASK_ENV=development flask --app app --debug run --host=0.0.0.0 -p 5000

prod:
	FLASK_ENV=production gunicorn --config gunicorn.conf.py wsgi:app

download:
	pip install -r requirements.txt

install:
	pip install -r requirements.txt

test:
	FLASK_ENV=testing python -m pytest

lint:
	flake8 app/
	black --check app/

format:
	black app/
