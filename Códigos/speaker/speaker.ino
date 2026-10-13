#include <WiFi.h>
#include <WiFiUdp.h>
#include <I2S.h> // Librería oficial simplificada de Arduino ESP32

//Información sobre el Hotspot
const char* ssid     = "HOTSPOT";
const char* password = "CONTRASEÑA";

WiFiUDP udp;
unsigned int localPort = 1234;
uint8_t buffer[1024];

void setup() {
    Serial.begin(115200);

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) delay(500);

    udp.begin(localPort);

    // Asignación de pines
    I2S.setSckPin(27); // BCLK
    I2S.setFsPin(25);  // LRC / WS
    I2S.setDataPin(22);// DIN

    // Inicializar I2S: (Modo, Frecuencia de muestreo, Bits por muestra)
    // Debe coincidir con la frecuencia del audio transmitido por Python
    if (!I2S.begin(I2S_PHILIPS_MODE, 22050, I2S_16_BIT)) {
        Serial.println("Error al inicializar I2S");
        while (1);
    }
}

void loop() {
    int packetSize = udp.parsePacket();
    if (packetSize > 0) {
        int len = udp.read(buffer, sizeof(buffer));
        
        // Escribe los datos de audio en bruto directamente al MAX98357A
        I2S.write(buffer, len);
    }
}