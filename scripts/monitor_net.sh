#!/bin/bash
# monitor_net.sh
# Registra bytes recibidos (RX) y enviados (TX) acumulados.

# --- CONFIGURACIÓN ---
OUTFILE="net_metrics.csv"
IFACE="enp0s3"

# --- MONITOREO ---
echo "--> Monitoreando interfaz: $IFACE"
echo "--> Guardando en: $OUTFILE"

# Crear cabecera CSV
echo "timestamp,rx_bytes,tx_bytes" > "$OUTFILE"

# Función para cerrar limpiamente con Ctrl+C
trap "echo ' Deteniendo monitoreo de red.'; exit" SIGINT SIGTERM

while true; do
    # Timestamp ISO 8601 UTC
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    # Verificamos que los archivos existan
    if [ -f "/sys/class/net/$IFACE/statistics/rx_bytes" ]; then
        # Leemos los contadores del Kernel
        rx=$(cat /sys/class/net/$IFACE/statistics/rx_bytes)
        tx=$(cat /sys/class/net/$IFACE/statistics/tx_bytes)
        
        echo "$timestamp,$rx,$tx" >> "$OUTFILE"
    else
        echo "Error: No se encuentra la interfaz $IFACE"
        exit 1
    fi
    
    sleep 5
done
