#!/bin/bash
# monitor_net.sh
# Registra bytes recibidos (RX) y enviados (TX) acumulados.

# --- CONFIGURACIÓN ---
mkdir -p metrics
OUTFILE="metrics/net_metrics.csv"

# Interfaz de red: usa variable de entorno o detecta automáticamente
# Para especificar manualmente: export NETWORK_IFACE="eth0"
if [ -z "$NETWORK_IFACE" ]; then
    # Detectar la interfaz principal (la que tiene IP, excluyendo lo)
    IFACE=$(ip route | grep default | awk '{print $5}' | head -1)
    if [ -z "$IFACE" ]; then
        IFACE="eth0"  # Fallback
    fi
else
    IFACE="$NETWORK_IFACE"
fi

export LC_NUMERIC=C

# --- MENSAJES DE INICIO ---
echo "--> Monitoreando interfaz: $IFACE"
echo "--> Guardando en: $OUTFILE"
echo "Presiona Ctrl+C para detener todo."

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
