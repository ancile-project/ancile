#!/usr/bin/bash

source .env/bin/activate
export FLASK_APP=runner.py
flask db upgrade
