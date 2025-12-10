#!/usr/bin/env python3
"""
Prueba de carga con Ramp-Up Gradual
Incrementa progresivamente la carga para observar la degradación del sistema.

Usa el endpoint /stress que estresa CPU, RAM y RED simultáneamente.
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from statistics import mean, median
import csv
import sys
import os

# Agregar el directorio padre al path para importar config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import SERVER_URL, RAMPUP_PHASES
except ImportError:
    # Valores por defecto si no existe config.py
    SERVER_URL = "http://100.107.204.120"
    RAMPUP_PHASES = [
        {"nombre": "Baseline",    "usuarios": 10,  "duracion": 30, "cpu": 100000,  "ram": 5,  "red": 256},
        {"nombre": "Moderada",    "usuarios": 50,  "duracion": 30, "cpu": 300000,  "ram": 10, "red": 512},
        {"nombre": "Alta",        "usuarios": 100, "duracion": 30, "cpu": 500000,  "ram": 15, "red": 768},
        {"nombre": "Sobrecarga",  "usuarios": 200, "duracion": 60, "cpu": 750000,  "ram": 20, "red": 1024},
        {"nombre": "Saturacion",  "usuarios": 500, "duracion": 60, "cpu": 1000000, "ram": 25, "red": 1024},
    ]

# Configuración
ENDPOINT = "/stress"
OUTPUT_FILE = "load_test_gradual_results.csv"
TIMEOUT_SECONDS = 300


async def hacer_request(session, fase_nombre, user_id, cpu, ram, red):
    """Hace un request al endpoint /stress y retorna métricas"""
    url = f"{SERVER_URL}{ENDPOINT}"
    params = {
        'cpu_iterations': cpu,
        'memory_mb': ram,
        'response_kb': red
    }

    start = time.time()

    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)) as response:
            # Leer el contenido para medir el tiempo completo de transferencia
            data = await response.read()
            elapsed = time.time() - start

            # Obtener métricas de los headers
            server_time = float(response.headers.get('X-Server-Time', 0))

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'fase': fase_nombre,
                'user_id': user_id,
                'status': response.status,
                'response_time': round(elapsed, 6),
                'server_time': round(server_time, 6),
                'network_time': round(elapsed - server_time, 6),
                'response_bytes': len(data),
                'success': True,
                'error': ''
            }
    except asyncio.TimeoutError:
        elapsed = time.time() - start
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'fase': fase_nombre,
            'user_id': user_id,
            'status': 'TIMEOUT',
            'response_time': round(elapsed, 6),
            'server_time': 0,
            'network_time': 0,
            'response_bytes': 0,
            'success': False,
            'error': 'Timeout'
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'fase': fase_nombre,
            'user_id': user_id,
            'status': 'ERROR',
            'response_time': round(elapsed, 6),
            'server_time': 0,
            'network_time': 0,
            'response_bytes': 0,
            'success': False,
            'error': str(e)[:100]
        }


async def ejecutar_fase(fase, writer, stats):
    """Ejecuta una fase de la prueba de carga"""
    nombre = fase['nombre']
    usuarios = fase['usuarios']
    duracion = fase['duracion']
    cpu = fase['cpu']
    ram = fase['ram']
    red = fase['red']

    print(f"\n{'='*70}")
    print(f"FASE: {nombre.upper()}")
    print(f"{'='*70}")
    print(f"  Usuarios concurrentes: {usuarios}")
    print(f"  Duración: {duracion}s")
    print(f"  Parámetros: cpu={cpu:,} | ram={ram}MB | red={red}KB")
    print(f"{'='*70}")

    fase_inicio = time.time()
    resultados_fase = []
    request_count = 0

    # Crear sesión compartida para la fase
    connector = aiohttp.TCPConnector(limit=usuarios * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        while (time.time() - fase_inicio) < duracion:
            # Lanzar requests concurrentes
            tasks = [
                hacer_request(session, nombre, i, cpu, ram, red)
                for i in range(usuarios)
            ]

            resultados = await asyncio.gather(*tasks)

            for r in resultados:
                writer.writerow(r)
                resultados_fase.append(r)
                request_count += 1

            # Mostrar progreso
            exitosos = sum(1 for r in resultados if r['success'])
            tiempo_promedio = mean([r['response_time'] for r in resultados])
            elapsed = time.time() - fase_inicio

            print(f"  [{elapsed:5.1f}s] Requests: {request_count:4d} | "
                  f"OK: {exitosos}/{usuarios} | "
                  f"Tiempo promedio: {tiempo_promedio:.3f}s")

    # Estadísticas de la fase
    exitosos_fase = [r for r in resultados_fase if r['success']]
    fallidos_fase = len(resultados_fase) - len(exitosos_fase)

    if exitosos_fase:
        tiempos = [r['response_time'] for r in exitosos_fase]
        tiempos.sort()

        stats[nombre] = {
            'total': len(resultados_fase),
            'exitosos': len(exitosos_fase),
            'fallidos': fallidos_fase,
            'tiempo_min': min(tiempos),
            'tiempo_max': max(tiempos),
            'tiempo_mean': mean(tiempos),
            'tiempo_median': median(tiempos),
            'tiempo_p95': tiempos[int(len(tiempos) * 0.95)] if len(tiempos) > 1 else tiempos[0],
        }

        print(f"\n  Resumen fase {nombre}:")
        print(f"    Total: {len(resultados_fase)} | Exitosos: {len(exitosos_fase)} | Fallidos: {fallidos_fase}")
        print(f"    Tiempo min: {min(tiempos):.3f}s | max: {max(tiempos):.3f}s | media: {mean(tiempos):.3f}s")
    else:
        stats[nombre] = {
            'total': len(resultados_fase),
            'exitosos': 0,
            'fallidos': fallidos_fase,
        }
        print(f"\n  ADVERTENCIA: Todos los requests fallaron en esta fase")

    return resultados_fase


async def ejecutar_prueba():
    """Ejecuta la prueba completa con todas las fases"""
    print(f"\n{'#'*70}")
    print(f"#  PRUEBA DE CARGA CON RAMP-UP GRADUAL")
    print(f"{'#'*70}")
    print(f"\nServidor: {SERVER_URL}{ENDPOINT}")
    print(f"Fases: {len(RAMPUP_PHASES)}")
    print(f"Duración total estimada: {sum(f['duracion'] for f in RAMPUP_PHASES)}s")

    # Preparar CSV
    fieldnames = ['timestamp', 'fase', 'user_id', 'status', 'response_time',
                  'server_time', 'network_time', 'response_bytes', 'success', 'error']

    csvfile = open(OUTPUT_FILE, 'w', newline='')
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    stats = {}
    inicio_total = time.time()

    try:
        for fase in RAMPUP_PHASES:
            await ejecutar_fase(fase, writer, stats)
            csvfile.flush()
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida por el usuario")
    finally:
        csvfile.close()

    tiempo_total = time.time() - inicio_total

    # Resumen final
    print(f"\n{'#'*70}")
    print(f"#  RESUMEN FINAL")
    print(f"{'#'*70}")
    print(f"\nTiempo total de ejecución: {tiempo_total:.1f}s")
    print(f"\nEstadísticas por fase:")
    print(f"{'Fase':<15} {'Total':>8} {'OK':>8} {'Fail':>8} {'Media':>10} {'P95':>10}")
    print(f"{'-'*15} {'-'*8} {'-'*8} {'-'*8} {'-'*10} {'-'*10}")

    for nombre, s in stats.items():
        if s['exitosos'] > 0:
            print(f"{nombre:<15} {s['total']:>8} {s['exitosos']:>8} {s['fallidos']:>8} "
                  f"{s['tiempo_mean']:>9.3f}s {s['tiempo_p95']:>9.3f}s")
        else:
            print(f"{nombre:<15} {s['total']:>8} {s['exitosos']:>8} {s['fallidos']:>8} {'N/A':>10} {'N/A':>10}")

    print(f"\nResultados guardados en: {OUTPUT_FILE}")
    print(f"{'#'*70}\n")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Tip: Puedes modificar las fases en config.py (RAMPUP_PHASES)")
    print("="*70 + "\n")

    try:
        asyncio.run(ejecutar_prueba())
    except KeyboardInterrupt:
        print("\n\nPrueba cancelada\n")
