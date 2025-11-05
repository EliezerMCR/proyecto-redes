#!/bin/bash
# monitor_net.sh
# Registra bytes recibidos y enviados por interfaz

OUTFILE="net_metrics.csv"
IFACE="eth0"  # cambia según tu VM
echo "timestamp,rx_bytes,tx_bytes" > "$OUTFILE"

while true; do
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    stats=$(cat /sys/class/net/$IFACE/statistics/{rx_bytes,tx_bytes} | xargs | awk '{print $1","$2}')
    echo "$timestamp,$stats" >> "$OUTFILE"
    sleep 5
done
