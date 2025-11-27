import pandas as pd
import matplotlib.pyplot as plt
import os

OUTPUT_DIR = "graficos"
CPU_FILE = "cpu_metrics.csv"
LATENCY_FILE = "latency_metrics.csv"

def crear_directorio():
    """Crea el directorio de salida si no existe."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Directorio '{OUTPUT_DIR}' creado.")

def graficar_carga_sistema():
    """Crea gráficos para CPU, Carga Promedio y Memoria."""
    try:
        df = pd.read_csv(CPU_FILE)
        
        # Convertir el timestamp a datetime para usarlo como índice
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        print(f"Graficando datos de {CPU_FILE}...")
        
        # Crear una figura con 3 subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 12), sharex=True)
        
        # 1. Gráfico de CPU
        df[['cpu_user', 'cpu_system', 'cpu_iowait']].plot(ax=ax1)
        ax1.set_title('Uso de CPU (%)')
        ax1.set_ylabel('% CPU')
        ax1.legend()
        ax1.grid(True)
        
        # 2. Gráfico de Load Average
        df[['load1', 'load5', 'load15']].plot(ax=ax2)
        ax2.set_title('Carga Promedio del Sistema (Load Average)')
        ax2.set_ylabel('Load')
        ax2.legend()
        ax2.grid(True)
        
        # 3. Gráfico de Memoria
        df[['mem_used', 'mem_free']].plot(ax=ax3)
        ax3.set_title('Uso de Memoria (MB)')
        ax3.set_ylabel('MB')
        ax3.legend()
        ax3.grid(True)
        
        # Guardar el gráfico
        plt.tight_layout() # Ajusta el layout
        output_path = os.path.join(OUTPUT_DIR, "1_carga_del_sistema.png")
        plt.savefig(output_path)
        plt.close(fig) # Cierra la figura para liberar memoria
        print(f"Gráfico guardado en: {output_path}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {CPU_FILE}")
    except Exception as e:
        print(f"Error graficando la carga del sistema: {e}")

def graficar_latencia():
    """Crea un gráfico para la latencia de respuesta."""
    try:
        df = pd.read_csv(LATENCY_FILE)
        
        # Convertir timestamp a datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        df['time_total'] = pd.to_numeric(df['time_total'], errors='coerce')
        df['time_starttransfer'] = pd.to_numeric(df['time_starttransfer'], errors='coerce')
        df['time_connect'] = pd.to_numeric(df['time_connect'], errors='coerce')
        
        print(f"Graficando datos de {LATENCY_FILE}...")
        
        # Crear una figura
        fig, ax = plt.subplots(figsize=(15, 6))
        
        # Graficar las 3 métricas de tiempo
        df[['time_total', 'time_starttransfer', 'time_connect']].plot(ax=ax)
        
        ax.set_title('Latencia de Respuesta del Servidor (Tiempos de Curl)')
        ax.set_ylabel('Segundos')
        ax.legend()
        ax.grid(True)
        
        # Guardar el gráfico
        plt.tight_layout()
        output_path = os.path.join(OUTPUT_DIR, "2_latencia_de_respuesta.png")
        plt.savefig(output_path)
        plt.close(fig)
        print(f"Gráfico guardado en: {output_path}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {LATENCY_FILE}")
    except Exception as e:
        print(f"Error graficando la latencia: {e}")

if __name__ == "__main__":
    crear_directorio()
    graficar_carga_sistema()
    graficar_latencia()
    print("\n¡Proceso de graficación completado!")