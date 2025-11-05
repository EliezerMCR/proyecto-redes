#!/bin/bash
# recolectar_todo.sh - versión mejorada
mkdir -p metrics

# Iniciar monitores en background y guardar sus PIDs
bash monitor_cpu.sh > metrics/cpu.log 2>&1 &
PID_CPU=$!
bash monitor_io.sh > metrics/io.log 2>&1 &
PID_IO=$!
bash monitor_net.sh > metrics/net.log 2>&1 &
PID_NET=$!
bash monitor_latency.sh > metrics/latency.log 2>&1 &
PID_LAT=$!

echo "Monitoreo iniciado (PIDs: $PID_CPU $PID_IO $PID_NET $PID_LAT)"
echo "Presiona Ctrl+C para detener todo."

# Capturar señal Ctrl+C (SIGINT)
trap "echo 'Deteniendo monitores...'; kill $PID_CPU $PID_IO $PID_NET $PID_LAT; exit" INT

# Esperar a que todos terminen (hasta Ctrl+C)
wait
