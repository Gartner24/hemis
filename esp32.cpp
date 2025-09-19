#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"
#include "Adafruit_MLX90614.h"
#include <ArduinoJson.h>
#include <time.h>

// ======= WiFi =======
const char* ssidList[] = {
  "RYGREDES",       // 1ra opción
  "RYGREDES PLUS",  // 2da opción
  "TECNOLOGICA"     // 3ra opción
};
const char* passList[] = {
  "erikaleon",
  "erikaleon",
  "tecnologica"
};
const int wifiCount = 3;

// ======= Backend =======
const char* backendUrl = "https://hemis.gartnercodes.com/api/telemetry/receive"; // Back to HTTPS
const int DEVICE_ID = 1;

// ======= Sensores =======
MAX30105 particleSensor;
Adafruit_MLX90614 mlx = Adafruit_MLX90614();

// ======= Buffers para cálculo SpO2 =======
#define BUFFER_SIZE 100
uint32_t irBuffer[BUFFER_SIZE];
uint32_t redBuffer[BUFFER_SIZE];
int32_t bufferLength;
int32_t spo2;
int8_t validSPO2;
int32_t heartRate;
int8_t validHeartRate;

// ======= Timing =======
unsigned long lastSensorRead = 0;
unsigned long lastDataSend = 0;
const unsigned long SENSOR_READ_INTERVAL = 2000; // Read sensors every 2 seconds
const unsigned long DATA_SEND_INTERVAL = 1000;   // Send data every 1 second

void connectWiFi() {
  for (int i = 0; i < wifiCount; i++) {
    Serial.print("Conectando a WiFi: ");
    Serial.println(ssidList[i]);

    WiFi.begin(ssidList[i], passList[i]);
    unsigned long startAttempt = millis();

    while (WiFi.status() != WL_CONNECTED && millis() - startAttempt < 10000) {
      delay(500);
      Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\nWiFi conectado!");
      Serial.print("SSID: ");
      Serial.println(ssidList[i]);
      Serial.print("IP del ESP32: ");
      Serial.println(WiFi.localIP());
      
      // Configure time for proper timestamps
      configTime(0, 0, "pool.ntp.org");
      return;
    }

    Serial.println("\nNo se pudo conectar, intentando siguiente...");
  }

  Serial.println("No se pudo conectar a ninguna red WiFi.");
}

String getCurrentTimestamp() {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    // Fallback to millis if time not available
    return String(millis());
  }
  
  char buffer[30];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &timeinfo);
  return String(buffer);
}

bool readSensors() {
  // Only read sensors every SENSOR_READ_INTERVAL
  if (millis() - lastSensorRead < SENSOR_READ_INTERVAL) {
    return false;
  }
  
  lastSensorRead = millis();
  
  bufferLength = BUFFER_SIZE;
  
  // Collect sensor data with proper timing
  for (int i = 0; i < bufferLength; i++) {
    int attempts = 0;
    while (!particleSensor.available() && attempts < 100) {
      particleSensor.check();
      delay(10); // Small delay to prevent overwhelming the sensor
      attempts++;
    }
    
    if (!particleSensor.available()) {
      Serial.println("Sensor timeout - no data available");
      return false;
    }
    
    redBuffer[i] = particleSensor.getRed();
    irBuffer[i] = particleSensor.getIR();
    particleSensor.nextSample();
    delay(5); // Small delay between samples
  }

  // Calculate heart rate and SpO2
  maxim_heart_rate_and_oxygen_saturation(
    irBuffer, bufferLength,
    redBuffer,
    &spo2, &validSPO2,
    &heartRate, &validHeartRate
  );

  return true;
}

void sendDataToBackend() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado, reconectando...");
    connectWiFi();
    return;
  }

  HTTPClient http;
  http.begin(backendUrl);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(10000); // 10 second timeout for HTTPS

  // Create JSON payload
  DynamicJsonDocument doc(200);
  doc["device_id"] = DEVICE_ID;
  doc["heart_rate"] = validHeartRate ? heartRate : 0;
  doc["spo2"] = validSPO2 ? spo2 : 0;
  doc["temp_skin"] = mlx.readObjectTempC();
  doc["timestamp"] = getCurrentTimestamp();

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  Serial.println("Enviando datos:");
  Serial.println(jsonPayload);

  // Send with retry logic
  int retryCount = 0;
  int maxRetries = 3;
  int httpResponseCode = -1;

  while (retryCount < maxRetries) {
    httpResponseCode = http.POST(jsonPayload);
    
    if (httpResponseCode > 0) {
      Serial.print("HTTP Response Code: ");
      Serial.println(httpResponseCode);
      
      if (httpResponseCode == 200 || httpResponseCode == 201) {
        Serial.println("Datos enviados exitosamente!");
        Serial.println("Response: " + http.getString());
        break;
      } else if (httpResponseCode == 301 || httpResponseCode == 302) {
        Serial.println("Redirección detectada - posible problema de URL");
        Serial.println("Response: " + http.getString());
        break; // Don't retry on redirect
      } else {
        Serial.println("Error en servidor: " + String(httpResponseCode));
        Serial.println("Response: " + http.getString());
        retryCount++;
        if (retryCount < maxRetries) {
          delay(2000); // Wait longer before retry
        }
      }
    } else {
      Serial.print("Error en POST (intento ");
      Serial.print(retryCount + 1);
      Serial.print("): ");
      Serial.println(http.errorToString(httpResponseCode));
      retryCount++;
      if (retryCount < maxRetries) {
        delay(2000); // Wait longer before retry
      }
    }
  }

  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(1000); // Give time for serial to initialize

  Serial.println("=== ESP32 HEMIS Device Starting ===");
  
  connectWiFi();

  // Initialize I2C
  Wire.begin(21, 22);
  delay(100);

  // Initialize MAX30105
  if (!particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
    Serial.println("ERROR: MAX30105 no encontrado!");
    while (1) {
      delay(1000);
      Serial.println("Reintentando inicializar MAX30105...");
      if (particleSensor.begin(Wire, I2C_SPEED_STANDARD)) {
        Serial.println("MAX30105 inicializado exitosamente!");
        break;
      }
    }
  }
  
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
  Serial.println("MAX30105 configurado correctamente");

  // Initialize MLX90614
  if (!mlx.begin()) {
    Serial.println("ERROR: MLX90614 no encontrado!");
    while (1) {
      delay(1000);
      Serial.println("Reintentando inicializar MLX90614...");
      if (mlx.begin()) {
        Serial.println("MLX90614 inicializado exitosamente!");
        break;
      }
    }
  }
  
  Serial.println("MLX90614 configurado correctamente");
  Serial.println("=== Todos los sensores listos! ===");
  
  // Initialize timing
  lastSensorRead = 0;
  lastDataSend = 0;
}

void loop() {
  unsigned long currentTime = millis();
  
  // Read sensors periodically
  if (readSensors()) {
    float tempSkin = mlx.readObjectTempC();
    
    Serial.print("Datos del sensor - HR: ");
    Serial.print(validHeartRate ? heartRate : 0);
    Serial.print(" | SpO2: ");
    Serial.print(validSPO2 ? spo2 : 0);
    Serial.print(" | Temp: ");
    Serial.println(tempSkin);
  }
  
  // Send data every second
  if (currentTime - lastDataSend >= DATA_SEND_INTERVAL) {
    lastDataSend = currentTime;
    sendDataToBackend();
  }
  
  // Small delay to prevent overwhelming the system
  delay(100);
}
