#!/bin/bash
# monitor_cpu.sh
# Registra CPU%, load average y memoria usada

# --- CONFIGURACIÓN ---
mkdir -p metrics
OUTFILE="metrics/cpu_metrics.csv"

export LC_NUMERIC=C

# --- MENSAJES DE INICIO ---
echo "--> Guardando métricas de CPU en: $OUTFILE"
echo "--> Intervalo de muestreo: ~5 segundos"
echo "Presiona Ctrl+C para detener."

OUTFILE="metrics/cpu_metrics.csv"

# --- ENCABEZADO CSV ---
# cpu_user, cpu_system, cpu_iowait, load1, load5, load15, mem_used, mem_free
echo "timestamp,cpu_user,cpu_system,cpu_iowait,load1,load5,load15,mem_used,mem_free" > "$OUTFILE"

# Control de salida limpia
trap "echo ' Deteniendo monitor CPU...'; exit" SIGINT SIGTERM

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 1. CPU & IOWait
    # mpstat 1 1 ejecuta durante 1 segundo para medir.
    # Columnas típicas: %usr(3), %sys(5), %iowait(6)
    cpu_stats=$(mpstat 1 1 | awk '/all/ {print $3","$5","$6}')

    # 2. Load Average
    loadavg=$(awk '{print $1","$2","$3}' /proc/loadavg)

    # 3. Memoria (en MB)
    mem=$(free -m | awk '/Mem:/ {print $3","$4}')

    # Guardar en CSV
    echo "$timestamp,$cpu_stats,$loadavg,$mem" >> "$OUTFILE"

    # Sincronización: mpstat tarda 1s + sleep 4s = 5s total
    sleep 4
done