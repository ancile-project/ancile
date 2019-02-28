#!/usr/bin/env bash

docker run --name ancile_dev_db --env-file ./utils/postgres/postgres.env -p 5432:5432 -d postgres
