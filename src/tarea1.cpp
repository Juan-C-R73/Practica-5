#include <Arduino.h>
#include <Arduino_LSM9DS1.h>

unsigned long ultimoMuestreo = 0;
const unsigned long intervalo = 50; // Muestreo cada 50 ms 

void setup() {
  
  Serial.begin(115200);
  while (!Serial); 

  
  if (!IMU.begin()) {
    Serial.println("Error al iniciar el sensor inercial LSM9DS1");
    while (1);
  }
}

void loop() {
  // Ejecutar cada 50 milisegundos exactos
  if (millis() - ultimoMuestreo >= intervalo) {
    ultimoMuestreo = millis();

    float x, y, z;

    // Comprobar si hay datos de aceleración listos y leerlos
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(x, y, z);

      // Enviar datos por UART en formato CSV (separados por comas)
      Serial.print(x, 4);
      Serial.print(",");
      Serial.print(y, 4);
      Serial.print(",");
      Serial.println(z, 4); // println añade el salto de línea (\r\n) al final de cada muestra
    }
  }
}