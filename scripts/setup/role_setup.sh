#!/usr/bin/bash

source .env/bin/activate
echo "Initializing server roles ... "
echo "Generating sample users ... "
python -m  scripts.setup.init_db