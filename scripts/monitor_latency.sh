#!/bin/bash
# monitor_latency.sh
# Mide latencias hacia el endpoint de Flask

# --- Creación de directorio de métricas ---
mkdir -p metrics

# --- MONITOREO ---
echo "--> Guardando en: $OUTFILE"
echo "Presiona Ctrl+C para detener todo.

OUTFILE="metrics/latency_metrics.csv"
URL="http://localhost:5000/cpu"  # o la IP de tu servidor
echo "timestamp,time_connect,time_starttransfer,time_total" > "$OUTFILE"

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    metrics=$(curl -w "@curl-format.txt" -o /dev/null -s $URL | tr -d '\n' | awk '{print $2","$4","$6}')
    echo "$timestamp,$metrics" >> "$OUTFILE"
    sleep 2
done
