#!/usr/bin/env python3
"""
Dashboard de Monitoreo en Tiempo Real
Servidor Flask con Server-Sent Events (SSE) para streaming de métricas.
"""

from flask import Flask, render_template, Response, jsonify
import json
import time
import sys
import os

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metrics_reader import get_all_metrics

app = Flask(__name__)

# Intervalo de actualización en segundos
UPDATE_INTERVAL = 2


@app.route('/')
def index():
    """Página principal del dashboard"""
    return render_template('index.html')


@app.route('/api/metrics')
def api_metrics():
    """Endpoint REST para obtener métricas actuales"""
    return jsonify(get_all_metrics())


@app.route('/api/stream')
def stream():
    """
    Server-Sent Events (SSE) para streaming de métricas en tiempo real.
    El cliente se conecta una vez y recibe actualizaciones automáticas.
    """
    def generate():
        while True:
            try:
                metrics = get_all_metrics()
                # Formato SSE: data: {json}\n\n
                yield f"data: {json.dumps(metrics)}\n\n"
                time.sleep(UPDATE_INTERVAL)
            except GeneratorExit:
                # Cliente desconectado
                break
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                time.sleep(UPDATE_INTERVAL)

    return Response(
        generate(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # Para Nginx
        }
    )


@app.route('/health')
def health():
    """Health check del dashboard"""
    return jsonify({"status": "ok", "service": "dashboard"})


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  DASHBOARD DE MONITOREO EN TIEMPO REAL")
    print("="*60)
    print(f"\n  URL: http://localhost:5001")
    print(f"  Intervalo de actualización: {UPDATE_INTERVAL}s")
    print("\n  Presiona Ctrl+C para detener")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
