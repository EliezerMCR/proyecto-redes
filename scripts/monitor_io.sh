#!/bin/bash
# monitor_io.sh
# Registra métricas de I/O por dispositivo

# --- Creación de directorio de métricas ---
mkdir -p metrics

# --- MONITOREO ---
echo "--> Guardando en: $OUTFILE"
echo "Presiona Ctrl+C para detener todo.

OUTFILE="metrics/io_metrics.csv"
echo "timestamp,device,read_s,write_s,utilization" > "$OUTFILE"

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    iostat -dx 1 1 | awk -v t="$timestamp" '/sd/ {print t","$1","$4","$5","$14}' >> "$OUTFILE"
    sleep 5
done

