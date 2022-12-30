python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
gunicorn config.wsgi:application -w 5 -b 0.0.0.0:8000 --timeout 1800
