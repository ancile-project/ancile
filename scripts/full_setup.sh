#!/usr/bin/bash

if [[ $(basename $(pwd)) != "ancile" ]]; then
    echo "This script must be run from the base 'Ancile' directory."
    exit 1
fi

mkdir logs

bash scripts/setup/setup_env.sh

bash scripts/setup/setup_dockers.sh

# bash scripts/setup/copy_templates.sh

echo "Waiting for docker ..."
sleep 5

echo "Running migrations"
bash scripts/setup/run_migrations.sh

echo "... done."
