import serial
import time

# Configuración del puerto serie (Ajusta 'COM7' si tu placa cambió de número)
PUERTO = 'COM7'
BAUDIOS = 115200

try:
    # 1. Abrir el puerto serie
    puerto_serie = serial.Serial(PUERTO, BAUDIOS, timeout=1)
    
    # IMPORTANTE para Arduino Nano 33 BLE: activar DTR para que envíe datos por USB nativo
    puerto_serie.dtr = True
    
    # Pausa breve para estabilizar la conexión y limpiar basura inicial del buffer
    time.sleep(1)
    puerto_serie.reset_input_buffer()

    print(f"Conectado a {PUERTO} a {BAUDIOS} baudios.")
    print("Mostrando datos en tiempo real (Pulsa Ctrl + C para detener):\n")

    # 2. Bucle infinito para leer y mostrar los datos en tiempo real
    while True:
        # Comprobar si hay bytes esperando en el buffer de entrada
        if puerto_serie.in_waiting > 0:
            # Leer una línea completa hasta el salto de línea (\n), decodificar a texto y quitar espacios/saltos finales
            linea = puerto_serie.readline().decode('utf-8', errors='ignore').strip()
            
            # Si la línea no está vacía, la imprimimos por pantalla
            if linea:
                print(linea)

except serial.SerialException as e:
    print(f"Error al abrir el puerto {PUERTO}: {e}")
    print("Asegúrate de haber cerrado Termite y el Monitor Serie de VS Code.")

except KeyboardInterrupt:
    print("\nLectura detenida por el usuario.")

finally:
    # 3. Cerrar el puerto limpiamente al salir del programa
    if 'puerto_serie' in locals() and puerto_serie.is_open:
        puerto_serie.close()
        print("Puerto serie cerrado correctamente.")