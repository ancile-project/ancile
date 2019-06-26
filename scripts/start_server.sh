#!/usr/bin/bash

source .env/bin/activate;
gunicorn runner:app -b localhost:8000 -w 4 --pid .pidfile --access-logfile logs/access.log
