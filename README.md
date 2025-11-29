# Proyecto de Monitoreo y Pruebas de Carga - Redes I

Este repositorio contiene la suite de herramientas desarrollada para el proyecto de **Redes I**. El objetivo es evaluar el comportamiento de un servidor web bajo condiciones de estrés, midiendo la degradación de métricas críticas como latencia, CPU y memoria.

Este conjunto de **scripts en Bash y Python** automatiza la recolección de métricas y la generación de tráfico, permitiendo registrar datos del sistema operativo en archivos CSV para su posterior análisis.

## Arquitectura del Sistema

El entorno de pruebas se basa en la siguiente pila tecnológica, tal como se detalla en el Informe Técnico:

* **Sistema Operativo:** Ubuntu 25.10 (Entorno de Simulación).
* **Servidor Web (Reverse Proxy):** Nginx (Puerto 80).
* **Servidor de Aplicación:** Python FastAPI + Uvicorn (Puerto 5000).
* **Red:** Configuración de Adaptador Puente (Bridge) para medición directa y Tailscale para acceso remoto seguro.
  
## Estructura del proyecto

```bash
proyecto-redes/
├── api/
│   └── main.py                     # API FastAPI
├── scripts/
│   ├── metrics/                    # Directorio de salida de los CSV (auto-generado)
│   ├── graficos/                   # Directorio de salida de los gráficos (auto-generado)
│   ├── load_test.py                # Generador de tráfico concurrente
│   ├── monitor_response_time.py    # Monitor de latencia continuo
│   ├── monitor_cpu.sh              # Métrica: CPU (user/sys), Load Avg, RAM
│   ├── monitor_io.sh               # Métrica: Lectura/Escritura disco
│   ├── monitor_net.sh              # Métrica: Tráfico RX/TX
│   ├── monitor_latency.sh          # Métrica: Tiempos HTTP (Connect/StartTransfer/Total)
│   ├── graficar.py                 # Genera gráficos desde CSVs
│   └── recolectar_todo.sh          # Inicia todos los monitores
├── README.md                       # Documentación del proyecto
├── venv/                           # Entorno virtual de Python
└── requirements.txt                # Dependencias de Python
```

## Configuración del Entorno

1. Dependencias del Sistema (Ubuntu)
Herramientas necesarias para los scripts de bash y el servidor web:

```bash
sudo apt update
sudo apt install sysstat curl nginx
```

2. Entorno Virtual de Python
Crea y activa un entorno virtual, luego instala las dependencias desde `requirements.txt`:

```bash
# Crear y activar entorno
python -m venv venv

# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Nota: Asegúrate de configurar tu .gitignore para excluir el entorno virtual y los datos generados:
venv/
metrics/*.csv
metrics/*.log
*.csv
*.log
*.tmp
*.bak
```

## Graficacion de metricas

El script `graficar.py` procesa los archivos CSV generados y crea visualizaciones en la carpeta `graficos/`.

Entradas (CSVs en scripts/metrics/):

- cpu_metrics.csv: CPU (usr/sys), load average y memoria.
- latency_metrics.csv: Tiempos internos (connect, processing).
- io_metrics.csv: Operaciones de disco (IOPS).
- net_metrics.csv: Tráfico de red (RX/TX).
- response_time_metrics.csv: Tiempos de respuesta HTTP (Cliente externo).
- load_test_results.csv: Estadísticas de la prueba de carga.

Salidas (scripts/graficos/):
  - `graficos/1_metrics_cpu_memoria.png`
  - `graficos/2_metrics_latencia.png`
  - `graficos/3_metrics_io.png`
  - `graficos/4_metrics_red.png`
  - `graficos/5_metrics_response_time.png`
  - `graficos/6_metrics_load_test.png`

## Guion de Ejecución

Pasos para capturar el escenario de **degradación completa del servidor** (Baseline → Carga → Recuperación).

Pre-requisito: El servidor de aplicación debe estar corriendo. Se recomienda usar 2 workers para saturar los núcleos de la VM:

```bash
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 2
```

### Paso 1: Iniciar Monitoreo (Servidor VM)

En la terminal de la Máquina Virtual, inicia la recolección de datos:

```bash
cd ../scripts
# Limpiar métricas anteriores para evitar ruido
rm metrics/*.csv

# Lanza todos los monitores en segundo plano
./recolectar_todo.sh
```

Estado: **Fase de Baseline**. Deja correr 30 segundos sin carga.

### Paso 2: PC Host

Desde otra máquina host para medir la latencia real:

```bash
cd scripts
python monitor_response_time.py
```

Espera 30 segundos después de iniciar el monitoreo

### Paso 3: Ejecutar la Prueba de Carga

Ejecuta la prueba de carga para saturar el servidor.

```bash
cd scripts
python load_test.py
```

Estado: **Fase de Degradación**
Duración: Espera a que termine el script (o déjalo correr 3-5 minutos).
Recuperación: Una vez finalice el script, espera 30 segundos extra para registrar cómo baja la carga.

### Paso 4: Finalización y Gráficos

Detén los procesos en todas las terminales (Ctrl + C).
En el servidor VM, asegura la detención de los monitores y genera el reporte visual:

```bash
# Detener monitores (si siguen corriendo)
./recolectar_todo.sh  # (Ctrl+C para detener)

# Generar los gráficos:
python graficar.py
```

### Descripción de los Scripts de Monitoreo

| Script | Frecuencia | Descripción | Archivo Salida |
| :--- | :--- | :--- | :--- |
| `monitor_cpu.sh` | 5 seg | Registra uso de CPU (usr/sys), Load Avg y Memoria RAM. | `cpu_metrics.csv` |
| `monitor_io.sh` | 5 seg | Mide operaciones de lectura/escritura (IOPS) en disco. | `io_metrics.csv` |
| `monitor_net.sh` | 5 seg | Registra ancho de banda (RX/TX) en la interfaz de red. | `net_metrics.csv` |
| `monitor_latency.sh` | 5 seg | Mide la latencia HTTP local (desglose DNS/Connect/Process). | `latency_metrics.csv` |
| `load_test.py` | N/A | Script de ataque. Genera concurrencia asíncrona contra `/cpu`. | `load_test_results.csv` |

#### Resultados Esperados

Si la prueba se ejecuta correctamente, las gráficas mostrarán:

1. Fase Baseline: CPU < 10%, Latencia < 100ms.
2. Fase Ramp-up: Aumento lineal de recursos.

3. Fase Sobrecarga:
   - CPU: > 95% de saturación.
   - Load Avg: Superando la cantidad de núcleos (ej. > 8.0).
   - Latencia: Degradación exponencial (> 2000ms).
   - Errores: Aparición de códigos HTTP 503/504 (Timeouts).

#### Troubleshooting

Si Los procesos de monitoreo siguen corriendo:
```bash
pkill -f uvicorn
# o reiniciar la VM
```
