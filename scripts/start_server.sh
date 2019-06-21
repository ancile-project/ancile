#!/usr/bin/bash

source .env/bin/activate;
gunicorn runner:app -b localhost:8000 -w 4 --pid .pidfile --max-requests 1000 --max-requests-jitter 200 --timeout 30 --graceful-timeout 30 --access-logfile logs/access.log
