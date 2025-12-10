"""
Lector de métricas en tiempo real desde los CSVs generados por los scripts de monitoreo.
"""

import os
import csv
from datetime import datetime
from collections import deque

# Directorio donde están los CSVs
METRICS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts', 'metrics')

# Archivos de métricas
FILES = {
    'cpu': os.path.join(METRICS_DIR, 'cpu_metrics.csv'),
    'net': os.path.join(METRICS_DIR, 'net_metrics.csv'),
    'io': os.path.join(METRICS_DIR, 'io_metrics.csv'),
    'latency': os.path.join(METRICS_DIR, 'latency_metrics.csv'),
}

# Cache de posiciones de archivo para leer solo nuevas líneas
file_positions = {}

# Historial de métricas (últimos N valores)
MAX_HISTORY = 100
metrics_history = {
    'cpu': deque(maxlen=MAX_HISTORY),
    'memory': deque(maxlen=MAX_HISTORY),
    'load': deque(maxlen=MAX_HISTORY),
    'net_rx': deque(maxlen=MAX_HISTORY),
    'net_tx': deque(maxlen=MAX_HISTORY),
    'latency': deque(maxlen=MAX_HISTORY),
}

# Variables para calcular velocidad de red
last_net_values = {'rx': None, 'tx': None, 'time': None}


def read_latest_cpu():
    """Lee la última línea del CSV de CPU"""
    filepath = FILES['cpu']
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return None

            # Última línea de datos
            last_line = lines[-1].strip()
            parts = last_line.split(',')

            if len(parts) >= 8:
                return {
                    'timestamp': parts[0],
                    'cpu_user': float(parts[1]) if parts[1] else 0,
                    'cpu_system': float(parts[2]) if parts[2] else 0,
                    'cpu_iowait': float(parts[3]) if parts[3] else 0,
                    'load1': float(parts[4]) if parts[4] else 0,
                    'load5': float(parts[5]) if parts[5] else 0,
                    'load15': float(parts[6]) if parts[6] else 0,
                    'mem_used': float(parts[7]) if parts[7] else 0,
                    'mem_free': float(parts[8]) if len(parts) > 8 and parts[8] else 0,
                }
    except Exception as e:
        print(f"Error reading CPU metrics: {e}")

    return None


def read_latest_net():
    """Lee las últimas dos líneas del CSV de red para calcular velocidad"""
    global last_net_values

    filepath = FILES['net']
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) < 3:  # Header + al menos 2 líneas de datos
                return None

            # Últimas 2 líneas de datos para calcular diferencia
            prev_line = lines[-2].strip().split(',')
            last_line = lines[-1].strip().split(',')

            if len(prev_line) >= 3 and len(last_line) >= 3:
                try:
                    prev_time = datetime.fromisoformat(prev_line[0].replace('Z', '+00:00'))
                    last_time = datetime.fromisoformat(last_line[0].replace('Z', '+00:00'))
                    time_diff = (last_time - prev_time).total_seconds()

                    if time_diff > 0:
                        prev_rx = int(prev_line[1])
                        prev_tx = int(prev_line[2])
                        last_rx = int(last_line[1])
                        last_tx = int(last_line[2])

                        # Velocidad en KB/s
                        rx_kbs = (last_rx - prev_rx) / time_diff / 1024
                        tx_kbs = (last_tx - prev_tx) / time_diff / 1024

                        return {
                            'timestamp': last_line[0],
                            'rx_kbs': round(rx_kbs, 2),
                            'tx_kbs': round(tx_kbs, 2),
                            'rx_total_mb': round(last_rx / 1024 / 1024, 2),
                            'tx_total_mb': round(last_tx / 1024 / 1024, 2),
                        }
                except (ValueError, IndexError):
                    pass
    except Exception as e:
        print(f"Error reading NET metrics: {e}")

    return None


def read_latest_latency():
    """Lee la última línea del CSV de latencia"""
    filepath = FILES['latency']
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            if len(lines) < 2:
                return None

            last_line = lines[-1].strip().split(',')

            if len(last_line) >= 5:
                return {
                    'timestamp': last_line[0],
                    'time_connect': float(last_line[1]) if last_line[1] != 'ERROR' else 0,
                    'time_starttransfer': float(last_line[2]) if last_line[2] != 'ERROR' else 0,
                    'time_total': float(last_line[3]) if last_line[3] != 'ERROR' else 0,
                    'http_code': last_line[4],
                }
    except Exception as e:
        print(f"Error reading LATENCY metrics: {e}")

    return None


def get_all_metrics():
    """Obtiene todas las métricas actuales"""
    cpu_data = read_latest_cpu()
    net_data = read_latest_net()
    latency_data = read_latest_latency()

    # Calcular CPU total (user + system)
    cpu_total = 0
    mem_used = 0
    mem_free = 0
    load1 = 0

    if cpu_data:
        cpu_total = cpu_data['cpu_user'] + cpu_data['cpu_system']
        mem_used = cpu_data['mem_used']
        mem_free = cpu_data['mem_free']
        load1 = cpu_data['load1']

        # Agregar al historial
        metrics_history['cpu'].append(cpu_total)
        metrics_history['memory'].append(mem_used)
        metrics_history['load'].append(load1)

    # Red
    rx_kbs = 0
    tx_kbs = 0
    if net_data:
        rx_kbs = net_data['rx_kbs']
        tx_kbs = net_data['tx_kbs']
        metrics_history['net_rx'].append(rx_kbs)
        metrics_history['net_tx'].append(tx_kbs)

    # Latencia
    latency_ms = 0
    if latency_data:
        latency_ms = latency_data['time_total'] * 1000  # Convertir a ms
        metrics_history['latency'].append(latency_ms)

    return {
        'timestamp': datetime.utcnow().isoformat(),
        'cpu': {
            'total': round(cpu_total, 1),
            'user': cpu_data['cpu_user'] if cpu_data else 0,
            'system': cpu_data['cpu_system'] if cpu_data else 0,
            'iowait': cpu_data['cpu_iowait'] if cpu_data else 0,
        },
        'memory': {
            'used_mb': round(mem_used, 1),
            'free_mb': round(mem_free, 1),
            'total_mb': round(mem_used + mem_free, 1),
            'percent': round((mem_used / (mem_used + mem_free) * 100) if (mem_used + mem_free) > 0 else 0, 1),
        },
        'load': {
            'load1': load1,
            'load5': cpu_data['load5'] if cpu_data else 0,
            'load15': cpu_data['load15'] if cpu_data else 0,
        },
        'network': {
            'rx_kbs': rx_kbs,
            'tx_kbs': tx_kbs,
        },
        'latency': {
            'total_ms': round(latency_ms, 2),
            'http_code': latency_data['http_code'] if latency_data else 'N/A',
        },
        'history': {
            'cpu': list(metrics_history['cpu']),
            'memory': list(metrics_history['memory']),
            'load': list(metrics_history['load']),
            'net_rx': list(metrics_history['net_rx']),
            'net_tx': list(metrics_history['net_tx']),
            'latency': list(metrics_history['latency']),
        }
    }


if __name__ == '__main__':
    # Test
    import json
    metrics = get_all_metrics()
    print(json.dumps(metrics, indent=2))
