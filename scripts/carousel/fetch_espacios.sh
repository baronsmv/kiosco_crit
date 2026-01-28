#!/bin/sh
umask 022

API_URL="http://django:8000/api/espacios/disponibles/"
OUTPUT_FILE="/app/static/data/espacios_disponibles.json"
TMP_FILE="$(mktemp)"

mkdir -p "$(dirname "$OUTPUT_FILE")"
chmod 755 "$(dirname "$OUTPUT_FILE")"

echo "[INFO] Obteniendo datos de API: $API_URL"

if curl -S -s --fail \
     --retry 5 \
     --retry-delay 10 \
     --retry-all-errors \
     --connect-timeout 10 \
     "$API_URL" | jq '.' > "$TMP_FILE"; then
    mv "$TMP_FILE" "$OUTPUT_FILE"
    chmod 644 "$OUTPUT_FILE"
    echo "[INFO] Archivo actualizado: $OUTPUT_FILE"
else
    echo "[ERROR] Error al obtener datos. Manteniendo archivo anterior."
    rm -f "$TMP_FILE"
fi
