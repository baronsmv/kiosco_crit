#!/bin/sh
set -e

# Wait for Django to be ready
until curl -sf http://django:8000/; do
  echo "[FETCH] Waiting for Django..."
  sleep 5
done

# Loop forever, fetching data every hour between 06-16
while true; do
  HOUR=$(date +%H)
  if [ "$HOUR" -ge 6 ] && [ "$HOUR" -le 16 ]; then
    /app/scripts/carousel/fetch_espacios.sh
  fi
  sleep 3600
done
