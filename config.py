"""
Configuración centralizada del proyecto de monitoreo.
Modifica estas variables según tu entorno.
"""

# =============================================================================
# MODO DE EJECUCIÓN
# =============================================================================
# True  = Todo corre en localhost (desarrollo/pruebas locales)
# False = Servidor remoto (VM con Nginx)
LOCAL_MODE = True

# =============================================================================
# CONFIGURACIÓN DEL SERVIDOR
# =============================================================================

if LOCAL_MODE:
    # Modo local: todo en localhost
    SERVER_IP = "localhost"
    SERVER_PORT = 5000  # Directo a Uvicorn
else:
    # Modo remoto: VM con Nginx
    SERVER_IP = "100.107.204.120"  # IP de Tailscale
    SERVER_PORT = 80  # A través de Nginx

# URL base del servidor (se construye automáticamente)
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}" if SERVER_PORT != 80 else f"http://{SERVER_IP}"

# IP para monitoreo interno (cuando el script corre en la misma VM)
SERVER_IP_LOCAL = "127.0.0.1" if LOCAL_MODE else "192.168.9.109"

# =============================================================================
# CONFIGURACIÓN DE RED
# =============================================================================

# Interfaz de red a monitorear (verificar con: ip link show)
NETWORK_INTERFACE = "enp0s3"

# =============================================================================
# CONFIGURACIÓN DE PRUEBAS DE CARGA
# =============================================================================

# Endpoint a usar para pruebas
STRESS_ENDPOINT = "/stress"
CPU_ENDPOINT = "/cpu"

# Parámetros default del endpoint /stress
DEFAULT_CPU_ITERATIONS = 500000
DEFAULT_MEMORY_MB = 10
DEFAULT_RESPONSE_KB = 512

# =============================================================================
# CONFIGURACIÓN DE MONITOREO
# =============================================================================

# Intervalo de muestreo en segundos
MONITOR_INTERVAL = 5

# Directorio de salida de métricas
METRICS_DIR = "metrics"
GRAPHS_DIR = "graficos"

# =============================================================================
# FASES DE RAMP-UP GRADUAL
# =============================================================================

RAMPUP_PHASES = [
    {"nombre": "Baseline",    "usuarios": 10,  "duracion": 30, "cpu": 100000,  "ram": 5,  "red": 256},
    {"nombre": "Moderada",    "usuarios": 50,  "duracion": 30, "cpu": 300000,  "ram": 10, "red": 512},
    {"nombre": "Alta",        "usuarios": 100, "duracion": 30, "cpu": 500000,  "ram": 15, "red": 768},
    {"nombre": "Sobrecarga",  "usuarios": 200, "duracion": 60, "cpu": 750000,  "ram": 20, "red": 1024},
    {"nombre": "Saturacion",  "usuarios": 500, "duracion": 60, "cpu": 1000000, "ram": 25, "red": 1024},
]
