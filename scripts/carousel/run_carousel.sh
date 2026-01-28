#!/bin/sh
set -e

echo "[INFO] Waiting for Django..."
until curl -sf http://django:8000/; do
  sleep 5
done

echo "[INFO] Django ready. Initial fetch."
/app/scripts/carousel/fetch_espacios.sh

echo "[INFO] Starting cron."
crond -f -l 8
