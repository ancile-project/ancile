#!/usr/bin/bash

source .env/bin/activate;
gunicorn  --bind 0.0.0.0:8000 ancile.web.ancile_web.wsgi:application -w 4 --pid .pidfile