import fastapi
import uvicorn
import math
import time
import sys

app = fastapi.FastAPI()

@app.get("/health")
def health_check():
    """
    Endpoint de 'health check'.
    Confirma si la app está viva.
    """
    return {"status": "ok"}

@app.get("/cpu")
def procesar_carga(iteraciones: int = 1000000):
    """
    Este endpoint consume CPU y RAM de manera proporcional y controlada.

    Parámetros:
    - iteraciones: Número de operaciones matemáticas (controla CPU y RAM)

    Complejidad:
    - CPU: O(N) lineal con iteraciones
    - RAM: O(N/1000) - almacena solo 1 de cada 1000 iteraciones
    """

    start_time = time.time()

    # Lista para almacenar resultados (consumo de RAM proporcional)
    # resultados_memoria = []
    resultado = 0

    for i in range(iteraciones):
        # Cálculo CPU-intensivo
        valor = math.sqrt(i) * math.sin(i)
        resultado += valor

        # Consumo de RAM reducido: almacenar solo 1 de cada 1000 valores
        # Cada float consume ~28 bytes aproximadamente
        if i % 1000 == 0:
            resultados_memoria.append(valor)

    end_time = time.time()
    execution_time = (end_time - start_time)

    # Calcular memoria utilizada (solo guardamos 1 de cada 1000)
    # Cada float: ~28 bytes aproximadamente
    memoria_bytes = len(resultados_memoria) * 28
    memoria_kb = memoria_bytes / 1024

    # Devuelve una respuesta JSON
    response = {
        "mensaje": "Carga procesada con FastAPI.",
        "iteraciones_realizadas": iteraciones,
        "tiempo_ejecucion_seg": execution_time,
        "elementos_en_memoria": len(resultados_memoria),
        "memoria_consumida_kb": round(memoria_kb, 2)
    }

    # # Limpiar memoria explícitamente antes de retornar
    # del resultados_memoria

    return response

# Ejecutar el script directamente con: python main.py
if __name__ == "__main__":
    # Esto hay que ajustarlo segun el script
    uvicorn.run(app, host="0.0.0.0", port=5000)