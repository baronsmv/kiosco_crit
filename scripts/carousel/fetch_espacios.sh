#!/bin/sh

TODAY=$(date +%Y-%m-%d)
API_URL="http://django:8000/api/espacios/disponibles/"
COOKIES_FILE="/app/static/data/cookies.txt"
OUTPUT_FILE="/app/static/data/espacios_disponibles.json"

mkdir -p "$(dirname "$OUTPUT_FILE")"
chmod 777 "$(dirname "$OUTPUT_FILE")"

echo "Fetching data from API: $API_URL"
curl -c "$COOKIES_FILE" http://django:8000/api/csrf/
CSRF=$(grep csrftoken "$COOKIES_FILE" | awk '{print $7}')

curl -b "$COOKIES_FILE" -c "$COOKIES_FILE" \
  -X POST http://django:8000/api/espacios/disponibles/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-CSRFToken: $CSRF" \
  -H "X-Requested-With: XMLHttpRequest" \
  --data "fecha=$TODAY" \
  | jq '.' > "$OUTPUT_FILE"

echo "Archivo actualizado: $OUTPUT_FILE"
