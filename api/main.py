import fastapi
import uvicorn
import math
import time

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
    Este endpoint consume CPU realizando cálculos matemáticos
    en un bucle. La cantidad de trabajo es controlada por el
    parámetro 'iteraciones'.
    """
    
    start_time = time.time()

    resultado = 0
    for i in range(iteraciones):
        resultado += math.sqrt(i) * math.sin(i)

    end_time = time.time()
    execution_time = (end_time - start_time)

    # Devuelve una respuesta JSON
    return {
        "mensaje": "Carga procesada con FastAPI.",
        "iteraciones_realizadas": iteraciones,
        "tiempo_ejecucion_seg": execution_time
    }

# Ejecutar el script directamente con: python main.py
if __name__ == "__main__":
    # Esto hay que ajustarlo segun el script
    uvicorn.run(app, host="0.0.0.0", port=5000)