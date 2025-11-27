import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# --- CONFIGURACIÓN DE RUTAS ---
# Carpeta donde están los CSV (generados por los scripts .sh)
INPUT_DIR = "metrics"
# Carpeta donde se guardarán las imágenes
OUTPUT_DIR = "graficos"

# Nombres de archivos esperados
CPU_FILE = os.path.join(INPUT_DIR, "cpu_metrics.csv")
LATENCY_FILE = os.path.join(INPUT_DIR, "latency_metrics.csv")
NET_FILE = os.path.join(INPUT_DIR, "net_metrics.csv")
IO_FILE = os.path.join(INPUT_DIR, "io_metrics.csv")

def preparar_entorno():
    """Crea los directorios necesarios."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")
    
    if not os.path.exists(INPUT_DIR):
        print(f"ADVERTENCIA: No existe el directorio '{INPUT_DIR}'. Asegúrate de ejecutar los scripts de monitoreo primero.")

def leer_csv(filepath):
    """Función auxiliar para leer CSV y configurar el índice de tiempo."""
    if not os.path.exists(filepath):
        print(f"Saltando {filepath}: Archivo no encontrado.")
        return None
    
    try:
        df = pd.read_csv(filepath)
        # Convertir timestamp a objeto datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"❌ Error leyendo {filepath}: {e}")
        return None

def graficar_cpu():
    df = leer_csv(CPU_FILE)
    if df is None: return

    print(f"Graficando CPU desde {CPU_FILE}...")
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12), sharex=True)
    
    # 1. Uso de CPU
    # Aseguramos que sean numéricos
    cols_cpu = ['cpu_user', 'cpu_system', 'cpu_iowait']
    df[cols_cpu] = df[cols_cpu].apply(pd.to_numeric, errors='coerce')
    df[cols_cpu].plot(ax=ax1, linewidth=1.5)
    ax1.set_title('Uso de CPU (%)')
    ax1.set_ylabel('Porcentaje')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left')

    # 2. Load Average
    cols_load = ['load1', 'load5', 'load15']
    df[cols_load] = df[cols_load].apply(pd.to_numeric, errors='coerce')
    df[cols_load].plot(ax=ax2, linewidth=1.5)
    ax2.set_title('Carga Promedio (Load Average)')
    ax2.set_ylabel('Carga')
    ax2.grid(True, alpha=0.3)

    # 3. Memoria
    cols_mem = ['mem_used', 'mem_free']
    df[cols_mem] = df[cols_mem].apply(pd.to_numeric, errors='coerce')
    df[cols_mem].plot(ax=ax3, kind='area', stacked=True, alpha=0.4)
    ax3.set_title('Uso de Memoria (MB)')
    ax3.set_ylabel('Megabytes')
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "1_metrics_cpu_memoria.png"))
    plt.close()

def graficar_latencia():
    df = leer_csv(LATENCY_FILE)
    if df is None: return

    print(f"Graficando Latencia desde {LATENCY_FILE}...")
    
    # Convertir a segundos (si vienen en formato texto)
    cols = ['time_total', 'time_starttransfer', 'time_connect']
    df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Graficamos time_total como línea principal
    df['time_total'].plot(ax=ax, label='Total Response Time', color='blue', linewidth=1)
    # Rellenamos el área de connect para ver cuánto toma la red vs el proceso
    ax.fill_between(df.index, 0, df['time_connect'], color='green', alpha=0.3, label='Connection Time (Network)')
    
    ax.set_title('Latencia HTTP (Cliente -> Nginx -> API)')
    ax.set_ylabel('Segundos')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "2_metrics_latencia.png"))
    plt.close()

def graficar_red():
    df = leer_csv(NET_FILE)
    if df is None: return

    print(f"Graficando Red desde {NET_FILE}...")
    
    # EL CSV TIENE VALORES ACUMULADOS. NECESITAMOS LA VELOCIDAD.
    # 1. Calculamos la diferencia de bytes entre filas
    df_diff = df[['rx_bytes', 'tx_bytes']].diff()
    
    # 2. Calculamos la diferencia de tiempo en segundos entre filas
    # Esto es vital porque el sleep no siempre es exactamente 5.00s
    time_diff = df.index.to_series().diff().dt.total_seconds()
    
    # 3. Calculamos la velocidad (Bytes / Segundos)
    # Convertimos a Kilobytes por segundo (KB/s) para leerlo mejor
    df['rx_kbs'] = (df_diff['rx_bytes'] / time_diff) / 1024
    df['tx_kbs'] = (df_diff['tx_bytes'] / time_diff) / 1024

    # Limpiar posibles valores infinitos o NaN del primer registro
    df = df.dropna()

    fig, ax = plt.subplots(figsize=(12, 6))
    
    df['rx_kbs'].plot(ax=ax, label='Descarga (RX)', color='green', linewidth=1.5)
    df['tx_kbs'].plot(ax=ax, label='Subida (TX)', color='blue', linewidth=1.5)
    
    ax.set_title('Tráfico de Red (Velocidad)')
    ax.set_ylabel('Velocidad (KB/s)')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "3_metrics_red.png"))
    plt.close()

def graficar_io():
    """
    Nota: Esta función asume que monitor_io.sh genera columnas estándar de iostat.
    Si usas 'iostat -dx 1 1', espera columnas como r/s, w/s, %util, etc.
    Ajustaremos nombres genéricos, verifica tu CSV de IO.
    """
    df = leer_csv(IO_FILE)
    if df is None: 
        return

    print(f"Graficando Disco desde {IO_FILE}...")
    
    # Intentar detectar columnas comunes de iostat
    # Si usaste un script personalizado, ajusta estos nombres
    possible_read_cols = [c for c in df.columns if 'read' in c.lower() or 'r/s' in c or 'rkB' in c]
    possible_write_cols = [c for c in df.columns if 'write' in c.lower() or 'w/s' in c or 'wkB' in c]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if possible_read_cols and possible_write_cols:
        # Tomamos la primera columna que parezca de lectura y escritura
        r_col = possible_read_cols[0]
        w_col = possible_write_cols[0]
        
        df[r_col] = pd.to_numeric(df[r_col], errors='coerce')
        df[w_col] = pd.to_numeric(df[w_col], errors='coerce')
        
        df[r_col].plot(ax=ax, label=f'Lectura ({r_col})', color='orange')
        df[w_col].plot(ax=ax, label=f'Escritura ({w_col})', color='purple')
        
        ax.set_title('Actividad de Disco (I/O)')
        ax.set_ylabel('Operaciones o KB/s')
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        print("No se detectaron columnas obvias de lectura/escritura en io_metrics.csv")
        # Graficamos todo lo que haya si no sabemos qué es
        df.plot(ax=ax)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "4_metrics_disco.png"))
    plt.close()

if __name__ == "__main__":
    print("--- Iniciando Generación de Gráficos ---")
    preparar_entorno()
    
    graficar_cpu()
    graficar_latencia()
    graficar_red()
    graficar_io()
    
    print(f"\n¡Proceso completado! Revisa la carpeta '{OUTPUT_DIR}'")