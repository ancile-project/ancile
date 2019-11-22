#!/usr/bin/bash

source .env/bin/activate;
bash scripts/start_db.sh
bash scripts/start_dev_vue.sh & python manage.py runserver
