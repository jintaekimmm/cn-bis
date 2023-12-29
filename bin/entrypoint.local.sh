#!/usr/bin/env bash

echo "Waiting for mysql connection..."

while ! nc -z db 3306; do
    sleep 0.2
done

echo "MySQL started..."

exec "$@"
