#!/bin/bash
# monitor_io.sh
# Registra métricas de I/O por dispositivo

# --- CONFIGURACIÓN ---
mkdir -p metrics
OUTFILE="metrics/io_metrics.csv"
export LC_NUMERIC=C

echo "--> Guardando métricas de I/O en: $OUTFILE"
echo "--> Intervalo: ~5 segundos"
echo "Presiona Ctrl+C para detener."

# 1. ENCABEZADO (SOLO UNA VEZ FUERA DEL LOOP)
echo "timestamp,device,read_s,write_s,utilization" > "$OUTFILE"

trap "echo ' Deteniendo monitor I/O...'; exit" SIGINT SIGTERM

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # 2. CAPTURA DE DATOS
    # Usamos grep para filtrar sda (VirtualBox estándar) o vda (VirtIO)
    # Si no te sale nada en el CSV, cambia 'sd[a-z]' por 'dm-[0-9]' o el nombre de tu disco.
    stats=$(iostat -dx 1 1 | awk -v t="$timestamp" '/sd[a-z]|vd[a-z]/ {print t","$1","$4","$5","$14}')
    
    # Solo escribir si se encontraron datos para evitar líneas vacías
    if [ ! -z "$stats" ]; then
        echo "$stats" >> "$OUTFILE"
    fi

    sleep 5
done