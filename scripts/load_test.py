#!/usr/bin/env python3
"""
Script de prueba de carga para sobrecargar el endpoint /cpu
Ejecuta múltiples usuarios concurrentes contra http://100.107.204.120/cpu
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from statistics import mean, median
import csv

# Configuración
SERVER_URL = "http://100.107.204.120/cpu"
OUTPUT_FILE = "load_test_results.csv"

# Aumentamos para saturar los 4 workers sugeridos
USUARIOS_CONCURRENTES = 5000

# Queremos que dure. Si cada request tarda 0.5s...
# 5000 requests / 50 users = 100 rondas. 100 * 0.5s = ~50 segundos.
# Pongamos 20,000 para asegurar unos 3-4 minutos de castigo.
TOTAL_REQUESTS = 200000

# Mantenemos esto alto para forzar CPU
ITERACIONES = 500000


async def hacer_request(session, user_id, request_num):
    """Hace un request y retorna las métricas"""
    start = time.time()

    try:
        params = {'iteraciones': ITERACIONES}
        async with session.get(SERVER_URL, params=params, timeout=aiohttp.ClientTimeout(total=60)) as response:
            data = await response.json()
            elapsed = time.time() - start

            return {
                'timestamp': datetime.utcnow().isoformat(),
                'user_id': user_id,
                'request_num': request_num,
                'status': response.status,
                'response_time': elapsed,
                'server_time': data.get('tiempo_ejecucion_seg', 0),
                'success': True
            }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'request_num': request_num,
            'status': f'ERROR: {str(e)}',
            'response_time': elapsed,
            'server_time': 0,
            'success': False
        }


async def simular_usuario(user_id, requests_por_usuario):
    """Simula un usuario haciendo requests"""
    async with aiohttp.ClientSession() as session:
        tasks = [hacer_request(session, user_id, i) for i in range(requests_por_usuario)]
        return await asyncio.gather(*tasks)


async def ejecutar_prueba():
    """Ejecuta la prueba de carga"""
    print(f"\n{'='*60}")
    print(f"SOBRECARGANDO SERVIDOR")
    print(f"{'='*60}")
    print(f"URL: {SERVER_URL}")
    print(f"Usuarios: {USUARIOS_CONCURRENTES}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Iteraciones por request: {ITERACIONES:,}")
    print(f"{'='*60}\n")

    start_time = time.time()

    # Distribuir requests entre usuarios
    requests_por_usuario = TOTAL_REQUESTS // USUARIOS_CONCURRENTES

    # Ejecutar todos los usuarios en paralelo
    print("Ejecutando requests concurrentes...")
    tasks = [simular_usuario(i, requests_por_usuario) for i in range(USUARIOS_CONCURRENTES)]
    resultados_por_usuario = await asyncio.gather(*tasks)

    # Aplanar resultados
    resultados = [r for usuario in resultados_por_usuario for r in usuario]

    end_time = time.time()
    total_time = end_time - start_time

    # Guardar CSV
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'user_id', 'request_num',
                                                'status', 'response_time', 'server_time', 'success'])
        writer.writeheader()
        writer.writerows(resultados)

    # Estadísticas
    exitosos = [r for r in resultados if r['success']]
    fallidos = [r for r in resultados if not r['success']]

    print(f"\n{'='*60}")
    print(f"RESULTADOS")
    print(f"{'='*60}")
    print(f"Tiempo total: {total_time:.2f}s")
    print(f"Throughput: {len(resultados)/total_time:.2f} req/s")
    print(f"Exitosos: {len(exitosos)} ({len(exitosos)/len(resultados)*100:.1f}%)")
    print(f"Fallidos: {len(fallidos)} ({len(fallidos)/len(resultados)*100:.1f}%)")

    if exitosos:
        tiempos = [r['response_time'] for r in exitosos]
        tiempos_sorted = sorted(tiempos)

        print(f"\nTIEMPOS DE RESPUESTA:")
        print(f"   Mínimo: {min(tiempos):.3f}s")
        print(f"   Máximo: {max(tiempos):.3f}s")
        print(f"   Media: {mean(tiempos):.3f}s")
        print(f"   Mediana: {median(tiempos):.3f}s")
        print(f"   P90: {tiempos_sorted[int(len(tiempos)*0.9)]:.3f}s")
        print(f"   P95: {tiempos_sorted[int(len(tiempos)*0.95)]:.3f}s")
        print(f"   P99: {tiempos_sorted[int(len(tiempos)*0.99)]:.3f}s")

    print(f"\nResultados guardados en: {OUTPUT_FILE}")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    print("\nTip: Puedes editar USUARIOS_CONCURRENTES, TOTAL_REQUESTS e ITERACIONES en el script\n")

    try:
        asyncio.run(ejecutar_prueba())
    except KeyboardInterrupt:
        print("\n\nPrueba interrumpida\n")
