#!/bin/bash

source /opt/venv/bin/activate

python manage.py makemigrations

python manage.py migrate

python manage.py collectstatic --no-input

gunicorn beckings.wsgi:application --bind 0.0.0.0:8080
