#!/usr/bin/bash

source .env/bin/activate;
gunicorn  --bind 0.0.0.0:8000 ancile.web.ancile_web.wsgi:application -w 4 --pid .pidfile --access-logfile logs/access.log --reload
# gunicorn runner:app -b localhost:8000 -w 4 --pid .pidfile --access-logfile logs/access.log --reload
