#!/usr/bin/bash

if [[ $(basename $(pwd)) != "ancile" ]]; then
    echo "This script must be run from the base 'Ancile' directory."
    exit 1
fi

echo "This will attempt to delete everything setup by 'full_install.sh'"
echo "Press enter to continue."

read cont

echo "Deleting python virtualenv"
rm -rf .env/ > /dev/null
echo "Deleting Logs"
rm -rf logs/ > /dev/null
echo "Deleting config files"
rm config/config.yaml config/oauth.yaml
echo "Stopping Docker containers"
docker stop ancile_dev_db redis_dev > /dev/null
echo "Deleting Docker containers"
docker rm ancile_dev_db redis_dev > /dev/null