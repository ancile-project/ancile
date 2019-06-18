#!/usr/bin/env bash

docker run --name redis_dev -p 127.0.0.1:6379:6379 -d redis