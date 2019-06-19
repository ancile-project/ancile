#!/usr/bin/bash

source .env/bin/activate
export FLASK_APP=runner.py
flask db upgrade

echo "Initializing server roles ... "
echo "Generating sample users ... "
python -m  scripts.setup.init_db