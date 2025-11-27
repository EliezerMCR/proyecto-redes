#!/bin/bash
# monitor_latency.sh
# Mide latencias HTTP (Connect, StartTransfer, Total)

# --- CONFIGURACIÓN ---
mkdir -p metrics
OUTFILE="metrics/latency_metrics.csv"
export LC_NUMERIC=C

# --- DEFINIR OBJETIVO ---
# Usamos la IP de la VM (interfaz puente) y el puerto 80 (Nginx)
# Ajusta el parámetro iteraciones=100 para que la respuesta sea rápida 
# y midamos latencia de red, no tiempo de procesamiento de CPU.
TARGET_URL="http://192.168.9.109/cpu?iteraciones=100"

echo "--> Guardando métricas en: $OUTFILE"
echo "--> Objetivo: $TARGET_URL"
echo "--> Intervalo: ~5 segundos"
echo "Presiona Ctrl+C para detener."

# Encabezado CSV
echo "timestamp,time_connect,time_starttransfer,time_total,http_code" > "$OUTFILE"

# Trap para salir limpio
trap "echo ' Deteniendo monitor latencia...'; exit" SIGINT SIGTERM

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # EXPLICACIÓN DEL CURL:
    # -o /dev/null: Descarta el cuerpo de la respuesta (el JSON)
    # -s: Silencioso (sin barra de progreso)
    # -w: Write-out, formato de salida personalizado con las métricas
    # %{http_code}: Para saber si dio error (200 es OK, 500 es error)
    
    metrics=$(curl -o /dev/null -s -w "%{time_connect},%{time_starttransfer},%{time_total},%{http_code}" "$TARGET_URL")

    # Si curl falla (ej. timeout), metrics estará vacío o incorrecto.
    # Validamos simple:
    if [ -n "$metrics" ]; then
        echo "$timestamp,$metrics" >> "$OUTFILE"
        # Opcional: Imprimir en pantalla para ver que funciona
        # echo "Ping: $metrics"
    else
        echo "$timestamp,ERROR,ERROR,ERROR,000" >> "$OUTFILE"
    fi

    sleep 5
done