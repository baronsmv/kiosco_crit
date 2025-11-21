#!/bin/sh

API_URL="http://django:8000/api/espacios/disponibles/"
OUTPUT_FILE="/app/static/data/espacios_disponibles.json"
MINUTES_TO_WAIT=30

mkdir -p "$(dirname "$OUTPUT_FILE")"
chmod 777 "$(dirname "$OUTPUT_FILE")"

if [ -f "$OUTPUT_FILE" ]; then
    file_mtime=$(stat -c %Y "$OUTPUT_FILE")
    now=$(date +%s)
    age=$((now - file_mtime))

    if [ "$age" -lt $((MINUTES_TO_WAIT * 60)) ]; then
        echo "Archivo ya actualizado hace menos de $MINUTES_TO_WAIT minutos, no se sobrescribe."
        exit 0
    fi
fi

echo "Obteniendo datos de API: $API_URL"
curl -s "$API_URL" | jq '.' > "$OUTPUT_FILE"
echo "Archivo actualizado: $OUTPUT_FILE"
