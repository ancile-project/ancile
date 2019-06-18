#!/usr/bin/env bash

docker run --name ancile_dev_db --env-file scripts/setup/postgres.env -p 127.0.0.1:5432:5432 -d postgres
docker run --name redis_dev -p 127.0.0.1:6379:6379 -d redis
