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

# Archivos de pruebas de carga y monitoreo
LOAD_TEST_FILE = "load_test_results.csv"
RESPONSE_TIME_FILE = "response_time_metrics.csv"

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
        print(f"Error leyendo {filepath}: {e}")
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

def graficar_load_test():
    """Grafica los resultados de la prueba de carga (load_test_results.csv)"""
    if not os.path.exists(LOAD_TEST_FILE):
        print(f"Saltando {LOAD_TEST_FILE}: Archivo no encontrado.")
        return

    print(f"Graficando Load Test desde {LOAD_TEST_FILE}...")

    try:
        df = pd.read_csv(LOAD_TEST_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    except Exception as e:
        print(f"Error leyendo {LOAD_TEST_FILE}: {e}")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Tiempos de respuesta a lo largo del tiempo
    ax1 = axes[0, 0]
    df_success = df[df['success'] == True]
    if not df_success.empty:
        ax1.scatter(df_success['timestamp'], df_success['response_time'],
                   alpha=0.3, s=10, c='blue', label='Response Time')
        # Media móvil
        df_success_sorted = df_success.sort_values('timestamp').copy()
        df_success_sorted['rolling_mean'] = df_success_sorted['response_time'].rolling(window=50, min_periods=1).mean()
        ax1.plot(df_success_sorted['timestamp'], df_success_sorted['rolling_mean'],
                color='red', linewidth=2, label='Media móvil (50)')
    ax1.set_title('Tiempos de Respuesta durante Load Test')
    ax1.set_ylabel('Tiempo (s)')
    ax1.set_xlabel('Tiempo')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)

    # 2. Distribución de tiempos de respuesta (histograma)
    ax2 = axes[0, 1]
    if not df_success.empty:
        ax2.hist(df_success['response_time'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax2.axvline(df_success['response_time'].mean(), color='red', linestyle='--', label=f"Media: {df_success['response_time'].mean():.2f}s")
        ax2.axvline(df_success['response_time'].median(), color='green', linestyle='--', label=f"Mediana: {df_success['response_time'].median():.2f}s")
    ax2.set_title('Distribución de Tiempos de Respuesta')
    ax2.set_xlabel('Tiempo (s)')
    ax2.set_ylabel('Frecuencia')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # 3. Throughput (requests por segundo)
    ax3 = axes[1, 0]
    df['timestamp_rounded'] = df['timestamp'].dt.floor('1s')
    throughput = df.groupby('timestamp_rounded').size()
    ax3.plot(throughput.index, throughput.values, color='purple', linewidth=1)
    ax3.fill_between(throughput.index, throughput.values, alpha=0.3, color='purple')
    ax3.set_title('Throughput (Requests/segundo)')
    ax3.set_ylabel('Requests/s')
    ax3.set_xlabel('Tiempo')
    ax3.grid(True, alpha=0.3)
    ax3.tick_params(axis='x', rotation=45)

    # 4. Tasa de éxito/error
    ax4 = axes[1, 1]
    success_count = df['success'].sum()
    error_count = len(df) - success_count
    colors = ['#2ecc71', '#e74c3c']
    ax4.pie([success_count, error_count], labels=['Exitosos', 'Fallidos'],
           autopct='%1.1f%%', colors=colors, startangle=90)
    ax4.set_title(f'Tasa de Éxito ({len(df)} requests totales)')

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "5_load_test_results.png"))
    plt.close()

    # Imprimir estadísticas
    print(f"   Total requests: {len(df)}")
    print(f"   Exitosos: {success_count} ({success_count/len(df)*100:.1f}%)")
    print(f"   Fallidos: {error_count} ({error_count/len(df)*100:.1f}%)")
    if not df_success.empty:
        print(f"   Tiempo respuesta promedio: {df_success['response_time'].mean():.3f}s")

def graficar_response_time():
    """Grafica las métricas de tiempo de respuesta (response_time_metrics.csv)"""
    if not os.path.exists(RESPONSE_TIME_FILE):
        print(f"Saltando {RESPONSE_TIME_FILE}: Archivo no encontrado.")
        return

    print(f"Graficando Response Time desde {RESPONSE_TIME_FILE}...")

    try:
        df = pd.read_csv(RESPONSE_TIME_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    except Exception as e:
        print(f"Error leyendo {RESPONSE_TIME_FILE}: {e}")
        return

    df_success = df[df['success'] == True]

    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # 1. Desglose de tiempos (response, server, network)
    ax1 = axes[0]
    if not df_success.empty:
        ax1.plot(df_success['timestamp'], df_success['response_time'],
                label='Response Time (Total)', color='blue', linewidth=1.5, marker='o', markersize=3)
        ax1.plot(df_success['timestamp'], df_success['server_time'],
                label='Server Time', color='orange', linewidth=1.5, marker='s', markersize=3)
        ax1.plot(df_success['timestamp'], df_success['network_latency'],
                label='Network Latency', color='green', linewidth=1.5, marker='^', markersize=3)
    ax1.set_title('Desglose de Tiempos de Respuesta')
    ax1.set_ylabel('Tiempo (s)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # 2. Área apilada para visualizar proporción
    ax2 = axes[1]
    if not df_success.empty:
        ax2.fill_between(df_success['timestamp'], 0, df_success['server_time'],
                        label='Server Time', alpha=0.7, color='orange')
        ax2.fill_between(df_success['timestamp'], df_success['server_time'],
                        df_success['server_time'] + df_success['network_latency'],
                        label='Network Latency', alpha=0.7, color='green')
    ax2.set_title('Composición del Tiempo de Respuesta')
    ax2.set_ylabel('Tiempo (s)')
    ax2.set_xlabel('Tiempo')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "6_response_time_metrics.png"))
    plt.close()

    # Imprimir estadísticas
    if not df_success.empty:
        print(f"   Total muestras: {len(df_success)}")
        print(f"   Response time promedio: {df_success['response_time'].mean():.3f}s")
        print(f"   Server time promedio: {df_success['server_time'].mean():.3f}s")
        print(f"   Network latency promedio: {df_success['network_latency'].mean():.3f}s")

if __name__ == "__main__":
    print("--- Iniciando Generación de Gráficos ---")
    preparar_entorno()

    graficar_cpu()
    graficar_latencia()
    graficar_red()
    graficar_io()
    graficar_load_test()
    graficar_response_time()

    print(f"\n¡Proceso completado! Revisa la carpeta '{OUTPUT_DIR}'")