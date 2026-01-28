#!/bin/sh
set -e

# Wait for Django to be ready
until curl -sf http://django:8000/; do
  echo "[FETCH] Waiting for Django..."
  sleep 5
done

# Initial fetch
/app/scripts/carousel/fetch_espacios.sh

# Loop forever, fetching data every hour between 06-16
while true; do
  HOUR=$(date +%H)

  if [ "$HOUR" -ge 6 ] && [ "$HOUR" -lt 17 ]; then
    sleep 3600
    /app/scripts/carousel/fetch_espacios.sh
  else
    sleep 900
  fi
done