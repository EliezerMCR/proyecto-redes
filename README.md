# proyecto-redes

# 📊 Scripts de Monitoreo – Proyecto Redes de Computadoras I

Este conjunto de **scripts en Bash** automatiza la **recolección de métricas de rendimiento del servidor** durante pruebas de carga.
Los scripts permiten registrar datos del sistema operativo (CPU, I/O, red, memoria y latencia) en archivos CSV para su posterior análisis y graficación.

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