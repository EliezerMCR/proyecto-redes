#!/bin/bash
# monitor_io.sh
# Registra métricas de I/O por dispositivo

OUTFILE="io_metrics.csv"
echo "timestamp,device,read_s,write_s,utilization" > "$OUTFILE"

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    iostat -dx 1 1 | awk -v t="$timestamp" '/sd/ {print t","$1","$4","$5","$14}' >> "$OUTFILE"
    sleep 5
done

