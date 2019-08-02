#!/usr/bin/bash

source .env/bin/activate
python manage.py migrate
deactivate
