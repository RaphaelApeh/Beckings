# 
python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic --on-input

gunicorn beckings.wsgi.application --bind 8080
