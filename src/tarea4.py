import serial
import time
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

#Configuración del puerto serie
PUERTO = 'COM7'
BAUDIOS = 115200

DURACION_SEGUNDOS = 5.0

# Listas para acumular los datos de cada barrido de 5 seg
datos_x, datos_y, datos_z, eje_tiempo = [], [], [], []

capturando = True
tiempo_inicio = 0

# Abrir puerto serie y activar DTR
puerto_serie = serial.Serial(PUERTO, BAUDIOS, timeout=0.1)
puerto_serie.dtr = True
time.sleep(1)


# Configuración de la ventana gráfica (Matplotlib)
fig, ax = plt.subplots(figsize=(10, 6))
linea_x, = ax.plot([], [], label='Eje X', color='red')
linea_y, = ax.plot([], [], label='Eje Y', color='green')
linea_z, = ax.plot([], [], label='Eje Z', color='blue')
ax.set_xlim(0, DURACION_SEGUNDOS)
ax.set_ylim(-2.5, 2.5) # Rango de aceleración
ax.set_xlabel('Tiempo (s)')
ax.set_ylabel('Aceleración (g)')
ax.set_title('Datos Acelerómetro')
ax.legend(loc='upper right')
ax.grid(True)

# Cuadro de texto dentro de la gráfica para mostrar Promedio y Desviación Estándar
texto_estadisticas = ax.text(
    0.02, 0.95, '', transform=ax.transAxes, verticalalignment='top',
    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
    fontfamily='monospace'
)

#Función para iniciar una captura de 5 segundos
def iniciar_captura():
    global capturando, tiempo_inicio
    datos_x.clear()
    datos_y.clear()
    datos_z.clear()
    eje_tiempo.clear()
    
    linea_x.set_data([], [])
    linea_y.set_data([], [])
    linea_z.set_data([], [])
    ax.set_xlim(0, DURACION_SEGUNDOS)
    puerto_serie.reset_input_buffer() # Limpiar datos antiguos acumulados
    tiempo_inicio = time.time()
    capturando = True
    ax.set_title('CAPTURANDO DATOS (5 segundos)...', color='green', fontweight='bold')
    print("\n--- Nueva captura de 5 segundos iniciada ---")

# Al pulsar ESPACIO o ENTER en la gráfica, vuelve a capturar
def pulsar_tecla(event):
    if event.key in [' ', 'enter', 'r'] and not capturando:
        iniciar_captura()

fig.canvas.mpl_connect('key_press_event', pulsar_tecla)


#Función de actualización llamada por FuncAnimation
def actualizar_grafica(frame):
    global capturando

    # Si ya terminaron los 5 segundos, no se lee nada y se mantiene la gráfica fija
    if not capturando:
        return linea_x, linea_y, linea_z, texto_estadisticas

    tiempo_actual = time.time() - tiempo_inicio

    # Comprobar si ya han pasado los 5 segundos
    if tiempo_actual >= DURACION_SEGUNDOS:
        capturando = False
        ax.set_title('CAPTURA FINALIZADA (Pulsa ESPACIO en esta ventana para repetir)', color='red', fontweight='bold')
        print("--- 5 segundos completados. Captura en pausa (Pulsa ESPACIO en la gráfica para otra tanda) ---")
        return linea_x, linea_y, linea_z, texto_estadisticas

    # Mientras estemos dentro de los 5 segundos, leemos las muestras del Arduino
    while puerto_serie.in_waiting > 0:
        linea = puerto_serie.readline().decode('utf-8', errors='ignore').strip()
        if linea:
            partes = linea.split(',')
            if len(partes) == 3:
                try:
                    t_muestra = time.time() - tiempo_inicio
                    if t_muestra <= DURACION_SEGUNDOS:
                        datos_x.append(float(partes[0]))
                        datos_y.append(float(partes[1]))
                        datos_z.append(float(partes[2]))
                        eje_tiempo.append(t_muestra)
                except ValueError:
                    pass

    # Actualizar curvas y calcular Promedio y Desviación Estándar en tiempo real
    if len(eje_tiempo) > 0:
        linea_x.set_data(eje_tiempo, datos_x)
        linea_y.set_data(eje_tiempo, datos_y)
        linea_z.set_data(eje_tiempo, datos_z)

        prom_x, std_x = np.mean(datos_x), np.std(datos_x)
        prom_y, std_y = np.mean(datos_y), np.std(datos_y)
        prom_z, std_z = np.mean(datos_z), np.std(datos_z)

        estado_txt = "CAPTURANDO..." if capturando else "FINALIZADO"
        info = (
            f"Estado: {estado_txt} ({eje_tiempo[-1]:.1f}s / 5.0s | {len(eje_tiempo)} muestras)\n"
            f"X -> Promedio: {prom_x:+.3f} g | Desv. Est.: {std_x:.3f} g\n"
            f"Y -> Promedio: {prom_y:+.3f} g | Desv. Est.: {std_y:.3f} g\n"
            f"Z -> Promedio: {prom_z:+.3f} g | Desv. Est.: {std_z:.3f} g"
        )
        texto_estadisticas.set_text(info)

    return linea_x, linea_y, linea_z, texto_estadisticas

# Iniciar la primera captura y lanzar FuncAnimation
iniciar_captura()
animacion = FuncAnimation(fig, actualizar_grafica, interval=50, cache_frame_data=False)

try:
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    if puerto_serie.is_open:
        puerto_serie.close()
        print("Puerto serie cerrado.")