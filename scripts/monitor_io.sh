#!/bin/bash
# monitor_io.sh
# Registra métricas de I/O por dispositivo

# --- CONFIGURACIÓN ---
mkdir -p metrics
OUTFILE="metrics/io_metrics.csv"

export LC_NUMERIC=C

# --- MENSAJES DE INICIO ---
echo "--> Guardando métricas de I/O en: $OUTFILE"
echo "--> Intervalo de muestreo: ~5 segundos"
echo "Presiona Ctrl+C para detener."
OUTFILE="metrics/io_metrics.csv"


echo "timestamp,device,read_s,write_s,utilization" > "$OUTFILE"
# Control de salida limpia
trap "echo ' Deteniendo monitor I/O...'; exit" SIGINT SIGTERM

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    iostat -dx 1 1 | awk -v t="$timestamp" '/sd/ {print t","$1","$4","$5","$14}' >> "$OUTFILE"
    # Guardar en CSV
    echo "timestamp,device,read_s,write_s,utilization" >> "$OUTFILE"
    sleep 5
done

