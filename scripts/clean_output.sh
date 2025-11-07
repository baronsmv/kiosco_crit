#!/bin/sh

# Usa 300 por defecto si la variable no está definida
INTERVAL=${PDF_CLEAN_INTERVAL_SECONDS:-7200}
MINUTES=${PDF_CLEAN_MINUTES:-120}

echo "[CLEANER] Iniciando limpieza de PDFs cada $INTERVAL segundos..."

while true; do
  echo "[CLEANER] ⏰ Ejecutando limpieza: $(date)"
  find /media/pdf -type f -name "*.pdf" -mmin +$MINUTES -print -delete
  echo "[CLEANER] Limpieza completada. Esperando $INTERVAL segundos..."
  sleep "$INTERVAL"
done
