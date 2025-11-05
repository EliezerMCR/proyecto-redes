#!/bin/bash
# monitor_cpu.sh
# Registra CPU%, load average y memoria usada

OUTFILE="cpu_metrics.csv"

# Encabezado
echo "timestamp,cpu_user,cpu_system,cpu_iowait,load1,load5,load15,mem_used,mem_free" > "$OUTFILE"

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # CPU y iowait
    cpu_stats=$(mpstat 1 1 | awk '/all/ {print $3","$5","$6}')
    # Load average
    loadavg=$(awk '{print $1","$2","$3}' /proc/loadavg)
    # Memoria
    mem=$(free -m | awk '/Mem:/ {print $3","$4}')

    echo "$timestamp,$cpu_stats,$loadavg,$mem" >> "$OUTFILE"
done
# Puedes detenerlo con Ctrl+C.
# Para correrlo cada 5 segundos, usa: watch -n 5 ./monitor_cpu.sh o un sleep dentro del loop.