#!/bin/bash
# monitor_cpu.sh
# Registra CPU, load y memoria

mkdir -p metrics
OUTFILE="metrics/cpu_metrics.csv"
export LC_NUMERIC=C

echo "--> Guardando métricas CPU en: $OUTFILE"
echo "Presiona Ctrl+C para detener."

echo "timestamp,cpu_user,cpu_system,cpu_iowait,load1,load5,load15,mem_used,mem_free" > "$OUTFILE"

trap "echo ' Deteniendo...'; exit" SIGINT SIGTERM

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 1. CPU: Usamos tail -1 para asegurar que tomamos la última línea (Average o el dato)
    # y tr -d para borrar cualquier salto de línea basura.
    cpu_stats=$(mpstat 1 1 | awk '/all/ {print $3","$5","$6}' | tail -n 1 | tr -d '\n')

    # 2. Load Average
    loadavg=$(awk '{print $1","$2","$3}' /proc/loadavg | tr -d '\n')

    # 3. Memoria
    mem=$(free -m | awk '/Mem:/ {print $3","$4}' | tr -d '\n')

    # Validación simple: si alguna variable está vacía, no escribimos la línea rota
    if [[ -n "$cpu_stats" && -n "$loadavg" && -n "$mem" ]]; then
        echo "$timestamp,$cpu_stats,$loadavg,$mem" >> "$OUTFILE"
    fi

    sleep 4
done