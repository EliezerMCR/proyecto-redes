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
    - RAM: O(N) lineal con iteraciones (~400 bytes por iteración)

    Consumo aproximado:
    - 100,000 iteraciones → ~40 MB RAM
    - 500,000 iteraciones → ~200 MB RAM
    - 1,000,000 iteraciones → ~400 MB RAM
    - 5,000,000 iteraciones → ~2 GB RAM
    """

    start_time = time.time()

    # Lista para almacenar resultados (consumo de RAM proporcional)
    resultados_memoria = []
    resultado = 0

    for i in range(iteraciones):
        # Cálculo CPU-intensivo
        valor = math.sqrt(i) * math.sin(i)
        resultado += valor

        # Consumo de RAM lineal: almacenar múltiples copias del resultado
        # para incrementar el consumo de memoria de forma significativa
        # Cada diccionario consume ~400 bytes aproximadamente
        datos = {
            'iteracion': i,
            'valor': valor,
            'sqrt': math.sqrt(i),
            'sin': math.sin(i),
            'cos': math.cos(i),
            'tan': math.tan(i) if math.cos(i) != 0 else 0,
            'resultado_acumulado': resultado,
            'duplicado_1': valor,
            'duplicado_2': valor,
            'duplicado_3': valor
        }
        resultados_memoria.append(datos)

    end_time = time.time()
    execution_time = (end_time - start_time)

    # Calcular memoria utilizada
    # Cada dict con 10 elementos: ~400 bytes aproximadamente
    memoria_bytes = len(resultados_memoria) * 400
    memoria_mb = memoria_bytes / (1024 * 1024)

    # Devuelve una respuesta JSON
    response = {
        "mensaje": "Carga procesada con FastAPI.",
        "iteraciones_realizadas": iteraciones,
        "tiempo_ejecucion_seg": execution_time,
        "elementos_en_memoria": len(resultados_memoria),
        "memoria_consumida_mb": round(memoria_mb, 2)
    }

    # Limpiar memoria explícitamente antes de retornar
    del resultados_memoria

    return response

# Ejecutar el script directamente con: python main.py
if __name__ == "__main__":
    # Esto hay que ajustarlo segun el script
    uvicorn.run(app, host="0.0.0.0", port=5000)