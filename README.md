# proyecto-redes

# 📊 Scripts de Monitoreo – Proyecto Redes de Computadoras I

Este conjunto de **scripts en Bash** automatiza la **recolección de métricas de rendimiento del servidor** durante pruebas de carga.
Los scripts permiten registrar datos del sistema operativo (CPU, I/O, red, memoria y latencia) en archivos CSV para su posterior análisis y graficación.

## 📈 Graficación de métricas (Python)

El script `graficos/graficar.py` genera gráficos a partir de los `.csv` producidos por los scripts de monitoreo.

- **Entrada esperada:**
  - `cpu_metrics.csv` (CPU, load average y memoria)
  - `latency_metrics.csv` (time_connect, time_starttransfer, time_total)
- **Salida:**
  - `graficos/1_carga_del_sistema.png`
  - `graficos/2_latencia_de_respuesta.png`

### Requisitos de Python

Con el entorno virtual activado:

```bash
(venv) $ pip install pandas matplotlib
```

### Cómo ejecutar

1. Tener los archivos `.csv` en el mismo directorio en el que ejecutaremos el script, o ajustar las rutas en `graficos/graficar.py`.
2. Ejecutar:

```bash
(venv) $ python graficos/graficar.py
```
---

## ⚙️ Estructura del proyecto

```
scripts/
│
├── utils.sh              # Configuración y funciones comunes
├── monitor_cpu.sh        # Registra uso de CPU, memoria y carga promedio
├── monitor_io.sh         # Registra métricas de E/S de disco
├── monitor_net.sh        # Registra tráfico de red (bytes RX/TX)
├── monitor_latency.sh    # Registra latencias HTTP hacia un endpoint
└── recolectar_todo.sh    # Lanza y controla todos los monitores a la vez
```

---

## Dependencias requeridas

Los scripts están diseñados para ejecutarse en **Ubuntu 22.04 LTS**, tanto en **WSL2** como en una **máquina virtual (VM)**.
Asegúrate de tener instaladas las siguientes herramientas:

```bash
sudo apt update
sudo apt install sysstat curl
```

---

## Uso individual de cada script

Todos los scripts se ejecutan desde la carpeta `scripts/` y generan archivos `.csv` con métricas y timestamps UTC.

### 1. `monitor_cpu.sh`

Registra el **uso de CPU, iowait, carga promedio y memoria**.

```bash
./monitor_cpu.sh
```

Genera: `cpu_metrics.csv`

Para detener: `Ctrl + C`

---

## 2. `monitor_io.sh`

Registra estadísticas de **lectura/escritura de disco** por dispositivo.

```bash
./monitor_io.sh
```

Genera: `io_metrics.csv`

Para detener: `Ctrl + C`

---

### 3. `monitor_net.sh`

Registra los **bytes recibidos (RX)** y **enviados (TX)** por una interfaz de red.

```bash
./monitor_net.sh
```

Genera: `net_metrics.csv`

Para detener: `Ctrl + C`

---

### 4. `monitor_latency.sh`

Mide **tiempos de conexión, inicio de transferencia y total** hacia una URL definida.

```bash
./monitor_latency.sh
```

Genera: `latency_metrics.csv`

Para detener: `Ctrl + C`


---

## 🚀 Monitoreo completo

Para ejecutar todos los scripts en paralelo:

```bash
./recolectar_todo.sh
```

El script:

* Lanza todos los monitores en segundo plano.
* Guarda logs en la carpeta `metrics/`.
* Captura `Ctrl + C` para detener todos los procesos de forma segura.

Salida esperada:

```
Monitoreo iniciado (PIDs: 125390 125391 125392 125393)
Presiona Ctrl+C para detener todo.
Deteniendo monitores...
```

---

## 🧹 Cómo detener manualmente todos los monitores

En caso de que algún proceso quede activo tras una interrupción:
```bash
pkill -f monitor_
```

Verifica que no quede ninguno ejecutándose:

```bash
ps aux | grep monitor_
```

### 1. La Aplicación Web (API de FastAPI)

Es el "consumidor de CPU" diseñado para cumplir con la Tarea 1.

* **Archivo:** `main.py`
* **Servidor:** Se ejecuta con `uvicorn`.
* **Endpoint:** `GET /cpu`
* **Parámetro:** `iteraciones` (ej. `/cpu?iteraciones=5000000`)
* **Funcionamiento:** Al recibir una petición, la API ejecuta un bucle `for` que calcula `math.sqrt(i) * math.sin(i)` un número `iteraciones` de veces.
    * **Complejidad:** Esta operación tiene una complejidad temporal **O(n)**, donde `n` es el número de `iteraciones`. Esto nos da un control lineal y predecible sobre la cantidad de carga de CPU que queremos generar.

### 2. Los Scripts de Monitoreo

Estos scripts (`.sh`) cumplen con las Tareas 2 y 3, recolectando datos en formato `.csv` para su posterior análisis.

* `monitor_cpu.sh`:
    * **Propósito:** Mide la carga interna del servidor.
    * **Métricas:** `% CPU (user, system, iowait)`, `load average` (1, 5, 15 min) y uso de `memoria` (usada, libre).
    * **Salida:** `cpu_metrics.csv`

* `monitor_io.sh`:
    * **Propósito:** Mide la actividad de entrada/salida del disco.
    * **Métricas:** `lecturas/s`, `escrituras/s` y `% de utilización` del disco.
    * **Salida:** `io_metrics.csv`

* `monitor_net.sh`:
    * **Propósito:** Mide el tráfico de red de la interfaz.
    * **Métricas:** `bytes recibidos (rx_bytes)` y `bytes enviados (tx_bytes)`.
    * **Salida:** `net_metrics.csv`

* `monitor_latency.sh`:
    * **Propósito:** Mide el rendimiento de la red desde la perspectiva del cliente (Tarea 3).
    * **Métricas:** `time_connect`, `time_starttransfer` y `time_total` de la respuesta.
    * **Importante:** Este script está configurado para apuntar al **Servidor Apache (Puerto 80)**, midiendo así el tiempo de respuesta total del sistema, incluyendo la latencia de red y el proxy.

* `recolectar_todo.sh`:
    * **Propósito:** Es el script maestro para iniciar y detener todas las recolecciones de datos.
    * **Funcionamiento:** Lanza todos los scripts `monitor_*.sh` como procesos en segundo plano. Al presionar `Ctrl+C`, captura la señal y detiene todos los procesos de monitoreo de forma limpia.

---

## Configuración e Instalación

1.  **Dependencias del Sistema:**
    Asegúrate de tener instaladas las herramientas de monitoreo. En sistemas basados en Debian/Ubuntu:
    ```bash
    sudo apt update
    sudo apt install sysstat curl
    ```

2.  **Entorno Virtual de Python:**
    Este proyecto usa un entorno virtual para gestionar las dependencias de Python y evitar conflictos con el sistema

    ```bash
    # 1. Crear el entorno virtual
    python3 -m venv venv

    # 2. Activar el entorno 
    source venv/bin/activate
    ```

3.  **Dependencias de Python:**
    Con el entorno activado, instala FastAPI y Uvicorn.

    ```bash
    (venv) $ pip install fastapi uvicorn
    ```

4.  **Archivo `.gitignore`:**
    Asegúrate de que tu `.gitignore` incluya la carpeta `venv/` y los archivos de datos generados:
    ```gitignore
    # Entorno virtual de Python
    venv/

    # Ignorar archivos de datos y logs
    *.csv
    *.log
    *.tmp
    *.bak
    metrics/
    ```

---

## Flujo de Trabajo para una Prueba

Este es el proceso para ejecutar un experimento completo y "sobresaturar al sistema" (Tarea 4).

**Paso 1: Iniciar el Servidor de Aplicación (Tu Máquina)**
En una terminal, activa el entorno virtual y ejecuta la API de FastAPI. Es crucial usar `0.0.0.0` para que sea visible para el servidor Apache.

```bash
source venv/bin/activate
(venv) $ uvicorn main:app --host 0.0.0.0 --port 5000