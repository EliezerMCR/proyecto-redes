#!/usr/bin/env python3
"""
Monitoreo continuo de tiempos de respuesta
Hace requests periódicos al servidor y registra los tiempos
"""

import requests
import time
import csv
from datetime import datetime
import signal
import sys
import os

# Agregar el directorio padre al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import SERVER_URL as BASE_URL, LOCAL_MODE
except ImportError:
    BASE_URL = "http://localhost:5000"
    LOCAL_MODE = True

# Configuración
SERVER_URL = f"{BASE_URL}/stress"
INTERVALO_SEGUNDOS = 5
# Parámetros ligeros para monitoreo (no sobrecargar)
STRESS_PARAMS = {
    'cpu_iterations': 1000,
    'memory_mb': 1,
    'response_kb': 1
}
OUTPUT_FILE = "response_time_metrics.csv"

# Variables globales
running = True
csv_file = None


def signal_handler(sig, frame):
    """Maneja Ctrl+C para detener limpiamente"""
    global running, csv_file
    print("\n\nDeteniendo monitoreo...")
    running = False
    if csv_file:
        csv_file.close()
    sys.exit(0)


def hacer_request():
    """Hace un request y retorna las métricas"""
    start = time.time()

    try:
        response = requests.get(SERVER_URL, params=STRESS_PARAMS, timeout=300)
        elapsed = time.time() - start

        if response.status_code == 200:
            # /stress devuelve datos binarios, el tiempo está en el header
            server_time = float(response.headers.get('X-Server-Time', 0))
            network_latency = elapsed - server_time

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'status': response.status_code,
                'response_time': round(elapsed, 6),
                'server_time': round(server_time, 6),
                'network_latency': round(network_latency, 6),
                'success': True,
                'error': ''
            }
        else:
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'status': response.status_code,
                'response_time': round(elapsed, 6),
                'server_time': 0,
                'network_latency': 0,
                'success': False,
                'error': f'HTTP {response.status_code}'
            }

    except Exception as e:
        elapsed = time.time() - start
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'ERROR',
            'response_time': round(elapsed, 6),
            'server_time': 0,
            'network_latency': 0,
            'success': False,
            'error': str(e)
        }


def main():
    global running, csv_file

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print(f"\n{'='*70}")
    print(f"MONITOREO DE TIEMPOS DE RESPUESTA")
    print(f"{'='*70}")
    print(f"URL: {SERVER_URL}")
    print(f"Intervalo: {INTERVALO_SEGUNDOS}s")
    print(f"Params: cpu={STRESS_PARAMS['cpu_iterations']}, ram={STRESS_PARAMS['memory_mb']}MB, red={STRESS_PARAMS['response_kb']}KB")
    print(f"Archivo: {OUTPUT_FILE}")
    print(f"{'='*70}")
    print(f"\nPresiona Ctrl+C para detener\n")
    print(f"{'Timestamp':<27} {'Status':<8} {'Response':<12} {'Server':<12} {'Network':<12}")
    print(f"{'-'*27} {'-'*8} {'-'*12} {'-'*12} {'-'*12}")

    # Inicializar CSV
    csv_file = open(OUTPUT_FILE, 'w', newline='')
    writer = csv.DictWriter(csv_file, fieldnames=['timestamp', 'status', 'response_time',
                                                    'server_time', 'network_latency', 'success', 'error'])
    writer.writeheader()
    csv_file.flush()

    request_count = 0
    success_count = 0

    while running:
        result = hacer_request()

        # Escribir a CSV
        writer.writerow(result)
        csv_file.flush()

        # Contadores
        request_count += 1
        if result['success']:
            success_count += 1

        # Mostrar en consola
        icon = "OK" if result['success'] else "ERROR"
        print(f"{result['timestamp']:<27} "
              f"{str(result['status']):<8} "
              f"{result['response_time']:>10.3f}s "
              f"{result['server_time']:>10.3f}s "
              f"{result['network_latency']:>10.3f}s {icon}")

        # Estadísticas cada 10 requests
        if request_count % 10 == 0:
            success_rate = (success_count / request_count) * 100
            print(f"\n{request_count} requests | {success_rate:.1f}% exito\n")

        time.sleep(INTERVALO_SEGUNDOS)

    csv_file.close()


if __name__ == '__main__':
    print("\nTip: Puedes editar INTERVALO_SEGUNDOS e ITERACIONES en el script\n")
    main()
