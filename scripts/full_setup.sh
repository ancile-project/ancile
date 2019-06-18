#!/usr/bin/bash

mkdir logs

bash scripts/setup/setup_env.sh

bash scripts/setup/setup_dockers.sh

bash scripts/setup/copy_templates.sh

sleep 2

bash scripts/setup/run_migrations.sh

