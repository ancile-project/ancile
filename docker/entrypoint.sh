#!/bin/bash
python manage.py migrate --noinput
gunicorn --bind :8000 -w 4 --pid .pidfile ancile.web.ancile_web.wsgi:application
