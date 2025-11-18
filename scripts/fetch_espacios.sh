#!/bin/sh

TODAY=$(date +%Y-%m-%d)
API_URL="http://django:8000/api/espacios/disponibles/"
OUTPUT_FILE="/app/static/data/espacios_disponibles.json"

mkdir -p "$(dirname "$OUTPUT_FILE")"
chmod 777 "$(dirname "$OUTPUT_FILE")"

echo "Fetching data from API: $API_URL"

curl -v -X POST http://django:8000/api/espacios/disponibles/ \
  -H "Content-Type: application/json" \
  -d "{\"fecha\": \"$TODAY\"}" \
  | jq '.' > "$OUTPUT_FILE"

echo "Archivo actualizado: $OUTPUT_FILE"
