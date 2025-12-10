# Proyecto de Monitoreo y Pruebas de Carga - Redes I

Este repositorio contiene la suite de herramientas desarrollada para el proyecto de **Redes I (CI-4835)**. El objetivo es evaluar el comportamiento de un servidor web bajo condiciones de estrés, midiendo la degradación de métricas críticas como latencia, CPU, memoria y tráfico de red.

## Arquitectura del Sistema

| Componente | Tecnología | Puerto |
|------------|------------|--------|
| Sistema Operativo | Ubuntu 25.10 | - |
| Reverse Proxy | Nginx | 80 |
| Servidor de Aplicación | FastAPI + Uvicorn | 5000 |
| Dashboard de Monitoreo | Flask | 5001 |
| Red | Adaptador Puente + Tailscale | - |

## Estructura del Proyecto

```
proyecto-redes/
├── api/
│   └── main.py                     # API FastAPI con endpoints /health, /cpu, /stress
├── scripts/
│   ├── metrics/                    # CSVs generados (auto-generado)
│   ├── graficos/                   # Gráficos PNG (auto-generado)
│   ├── load_test.py                # Prueba de carga (concurrencia fija)
│   ├── load_test_gradual.py        # Prueba de carga con ramp-up progresivo
│   ├── monitor_response_time.py    # Monitor de tiempos de respuesta
│   ├── monitor_cpu.sh              # Métrica: CPU, Load Avg, RAM
│   ├── monitor_io.sh               # Métrica: Lectura/Escritura disco
│   ├── monitor_net.sh              # Métrica: Tráfico RX/TX
│   ├── monitor_latency.sh          # Métrica: Latencia HTTP
│   ├── graficar.py                 # Generador de gráficos
│   └── recolectar_todo.sh          # Inicia todos los monitores
├── dashboard/
│   ├── app.py                      # Servidor Flask del dashboard
│   ├── metrics_reader.py           # Lector de métricas en tiempo real
│   └── templates/
│       └── index.html              # Interfaz del dashboard
├── config.py                       # Configuración centralizada
├── requirements.txt                # Dependencias de Python
└── README.md
```

## Endpoints de la API

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check del servidor |
| `/cpu` | GET | Carga de CPU con operaciones matemáticas |
| `/stress` | GET | **Estrés combinado: CPU + RAM + RED** |

### Endpoint `/stress`

Endpoint principal para pruebas de carga que estresa CPU, memoria y red simultáneamente.

```
GET /stress?cpu_iterations=500000&memory_mb=10&response_kb=512
```

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `cpu_iterations` | 500,000 | Operaciones matemáticas (más = más CPU) |
| `memory_mb` | 10 | MB de datos en memoria (más = más RAM) |
| `response_kb` | 512 | KB en la respuesta (más = más tráfico de red) |

## Configuración del Entorno

### 1. Dependencias del Sistema (Ubuntu)

```bash
sudo apt update
sudo apt install sysstat curl nginx
```

### 2. Entorno Virtual de Python

```bash
# Crear y activar entorno virtual
python -m venv venv

# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración (`config.py`)

Editar `config.py` para ajustar el modo de ejecución:

```python
# Para pruebas locales:
LOCAL_MODE = True

# Para producción en VM:
LOCAL_MODE = False
```

## Guía de Ejecución

### Distribución de Componentes

| Componente | Dónde se ejecuta | Propósito |
|------------|------------------|-----------|
| API (Uvicorn) | VM Servidor | Servir la aplicación |
| Nginx | VM Servidor | Reverse proxy |
| Scripts de monitoreo | VM Servidor | Recolectar métricas del sistema |
| Dashboard | VM Servidor | Visualizar métricas en tiempo real |
| Pruebas de carga | **Host externo** | Simular tráfico real por red |
| Monitor de respuesta | **Host externo** | Medir latencia real de red |

### Opción A: Prueba con Ramp-Up Gradual (Recomendado)

Esta prueba incrementa progresivamente la carga en 5 fases para observar la degradación del sistema.

#### En la VM (Servidor)

**Terminal 1 - Servidor:**
```bash
cd api
uvicorn main:app --host 0.0.0.0 --port 5000 --workers 2
```

**Terminal 2 - Monitoreo:**
```bash
cd scripts
rm -f metrics/*.csv    # Limpiar métricas anteriores
./recolectar_todo.sh
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard
python app.py
# Acceder en navegador: http://IP_VM:5001
```

#### Desde el Host (Cliente externo)

**Terminal 1 - Monitor de Latencia Real:**
```bash
cd scripts
python monitor_response_time.py
```

**Terminal 2 - Prueba de Carga:**
```bash
cd scripts
python load_test_gradual.py
```

> **Nota:** Ejecutar las pruebas desde un host externo permite medir la latencia real de red, simulando usuarios reales accediendo al servidor por internet.

**Fases del Ramp-Up:**

| Fase | Usuarios | Duración | CPU | RAM | RED |
|------|----------|----------|-----|-----|-----|
| Baseline | 10 | 30s | 100K | 5MB | 256KB |
| Moderada | 50 | 30s | 300K | 10MB | 512KB |
| Alta | 100 | 30s | 500K | 15MB | 768KB |
| Sobrecarga | 200 | 60s | 750K | 20MB | 1MB |
| Saturación | 500 | 60s | 1M | 25MB | 1MB |

### Opción B: Prueba con Carga Fija

```bash
cd scripts
python load_test.py
```

### Finalización y Gráficos

```bash
# Detener monitores (Ctrl+C en cada terminal)

# Generar gráficos
cd scripts
python graficar.py
```

## Dashboard en Tiempo Real

El dashboard muestra métricas del servidor en tiempo real:

- **CPU:** Uso porcentual y load average
- **Memoria:** MB usados/libres
- **Red:** Tráfico RX/TX en KB/s
- **Latencia:** Tiempo de respuesta HTTP

Acceder en: `http://IP_VM:5001`

## Scripts de Monitoreo

| Script | Frecuencia | Métricas | Archivo de Salida |
|--------|------------|----------|-------------------|
| `monitor_cpu.sh` | 5s | CPU (usr/sys), Load Avg, RAM | `cpu_metrics.csv` |
| `monitor_io.sh` | 5s | IOPS lectura/escritura | `io_metrics.csv` |
| `monitor_net.sh` | 5s | Bytes RX/TX | `net_metrics.csv` |
| `monitor_latency.sh` | 5s | Tiempos HTTP | `latency_metrics.csv` |

## Gráficos Generados

| Archivo | Contenido |
|---------|-----------|
| `1_metrics_cpu_memoria.png` | CPU, Load Average y Memoria |
| `2_metrics_latencia.png` | Latencia HTTP |
| `3_metrics_red.png` | Tráfico de Red (KB/s) |
| `4_metrics_disco.png` | Actividad de Disco |
| `5_load_test_results.png` | Resultados prueba de carga |
| `6_response_time_metrics.png` | Tiempos de respuesta |
| `7_load_test_gradual.png` | Resultados por fase (ramp-up) |

## Troubleshooting

```bash
# Detener procesos de monitoreo
pkill -f monitor_
pkill -f uvicorn
# o reiniciar la VM
```
