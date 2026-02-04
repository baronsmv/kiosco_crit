#!/bin/bash
set -e
exec >> /proc/1/fd/1 2>&1

echo "[INFO] Waiting for Django..."
until curl -sf http://django:8000/; do
  sleep 5
done

echo "[INFO] Initial fetch"
./fetch_espacios.sh

echo "[INFO] Starting cron"
cron -f
