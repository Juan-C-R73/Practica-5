import serial
import time

PUERTO = 'COM7'  # Puerto del arduino
BAUDIOS = 115200
ARCHIVO_SALIDA = 'datos_acelerometro.txt'

try:
    #Abrir el puerto serie y activar DTR
    puerto_serie = serial.Serial(PUERTO, BAUDIOS, timeout=1)
    puerto_serie.dtr = True
    time.sleep(1)
    puerto_serie.reset_input_buffer()

    #Abrir el fichero .txt en modo escritura ('w' = crea o sobrescribe el archivo)
    with open(ARCHIVO_SALIDA, mode='w', encoding='utf-8') as fichero:
        #Se escribe la primera fila con los nombres de las columnas
        fichero.write("X;Y;Z\n")
        
        print(f"Conectado a {PUERTO}. Guardando datos en '{ARCHIVO_SALIDA}'...")
        print("Mueve la placa y pulsa Ctrl + C cuando quieras terminar de grabar.\n")

        #Bucle de lectura y almacenamiento
        #Bucle infinito hasta pulsar ctrl+c
        while True:
            if puerto_serie.in_waiting > 0:
                # Leer la línea de datos
                linea = puerto_serie.readline().decode('utf-8', errors='ignore').strip()

                if linea:
                    # Cambiar las comas por ";" 
                    linea_formato_excel = linea.replace(',', ';')

                    # Guardar en el fichero .txt añadiendo el retorno de carro (\n) al final
                    fichero.write(linea_formato_excel + "\n")
                    
                    # Para forzar a Python a guardar cada línea en el disco duro en tiempo real
                    fichero.flush()

                    # Mostrar también por pantalla para ver qué se está guardando
                    print(linea_formato_excel)

except serial.SerialException as e:
    print(f"Error en el puerto {PUERTO}: {e}")

except KeyboardInterrupt:
    print(f"\nGrabación finalizada. Los datos se han guardado en '{ARCHIVO_SALIDA}'.")

finally:
    if 'puerto_serie' in locals() and puerto_serie.is_open:
        puerto_serie.close()
        print("Puerto serie cerrado.")