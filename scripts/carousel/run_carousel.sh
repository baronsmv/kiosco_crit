#!/bin/sh
exec >> /proc/self/fd/1 2>&1
set -e

echo "[INFO] Waiting for Django..."
until curl -sf http://django:8000/; do
  sleep 5
done

echo "[INFO] Django ready. Initial fetch."
/app/scripts/fetch_espacios.sh

echo "[INFO] Starting cron."
cron -f
