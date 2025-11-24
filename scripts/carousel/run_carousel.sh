#!/bin/sh
set -e

# Wait for Django to be ready
until curl -sf http://django:8000/; do
  echo "Waiting for Django..."
  sleep 5
done

# Loop forever, fetching data every hour
while true; do
  /app/scripts/carousel/fetch_espacios.sh
  sleep 3600
done
