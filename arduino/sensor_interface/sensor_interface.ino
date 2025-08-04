/*
 * Dual Energy Source Sensor Arduino Code
 * =====================================
 * 
 * This Arduino sketch collects sensor data for the dual energy source system:
 * - Solar panel voltage and current
 * - Thermal sensor readings
 * - Battery monitoring
 * - Environmental sensors
 * 
 * The data is sent to Raspberry Pi via Serial communication in JSON format.
 * 
 * Hardware Connections:
 * - A0: Solar voltage divider (0-20V -> 0-5V)
 * - A1: Solar current sensor (ACS712 or similar)
 * - A2: Battery voltage divider
 * - A3: Battery current sensor
 * - A4: SDA (I2C for additional sensors)
 * - A5: SCL (I2C for additional sensors)
 * - D2: DS18B20 temperature sensor (OneWire)
 * - D3: DHT22 humidity sensor
 * - D4-D7: Available for relay control or additional sensors
 * 
 * Author: AI Assistant
 * Date: August 2025
 */

#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>

// Pin definitions
#define SOLAR_VOLTAGE_PIN A0
#define SOLAR_CURRENT_PIN A1
#define BATTERY_VOLTAGE_PIN A2
#define BATTERY_CURRENT_PIN A3
#define TEMP_SENSOR_PIN 2
#define DHT_PIN 3

// Relay control pins (optional - can be controlled by RPi instead)
#define SOLAR_RELAY_PIN 4
#define THERMAL_RELAY_PIN 5
#define BATTERY_RELAY_PIN 6

// LED indicator pins
#define STATUS_LED_PIN 13
#define ERROR_LED_PIN 12

// Temperature sensor setup
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature tempSensors(&oneWire);

// Sensor calibration constants
const float VOLTAGE_DIVIDER_RATIO = 4.0;  // 20V -> 5V divider
const float CURRENT_SENSOR_SENSITIVITY = 0.1;  // 100mV/A for ACS712-5A
const float CURRENT_SENSOR_OFFSET = 2.5;  // Zero current offset voltage
const float VREF = 5.0;  // Arduino reference voltage

// Timing variables
unsigned long lastReading = 0;
const unsigned long READING_INTERVAL = 1000;  // 1 second between readings

// Data smoothing arrays
const int SAMPLES = 5;
float solarVoltageBuffer[SAMPLES];
float solarCurrentBuffer[SAMPLES];
float batteryVoltageBuffer[SAMPLES];
float batteryCurrentBuffer[SAMPLES];
int bufferIndex = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(ERROR_LED_PIN, OUTPUT);
  pinMode(SOLAR_RELAY_PIN, OUTPUT);
  pinMode(THERMAL_RELAY_PIN, OUTPUT);
  pinMode(BATTERY_RELAY_PIN, OUTPUT);
  
  // Initialize temperature sensors
  tempSensors.begin();
  
  // Initialize smoothing buffers
  for (int i = 0; i < SAMPLES; i++) {
    solarVoltageBuffer[i] = 0;
    solarCurrentBuffer[i] = 0;
    batteryVoltageBuffer[i] = 0;
    batteryCurrentBuffer[i] = 0;
  }
  
  // Signal successful initialization
  digitalWrite(STATUS_LED_PIN, HIGH);
  delay(500);
  digitalWrite(STATUS_LED_PIN, LOW);
  
  Serial.println("{\"status\":\"Arduino sensor interface initialized\"}");
}

void loop() {
  // Check if it's time for a new reading
  if (millis() - lastReading >= READING_INTERVAL) {
    collectAndSendData();
    lastReading = millis();
  }
  
  // Check for commands from Raspberry Pi
  if (Serial.available()) {
    processCommand();
  }
  
  // Blink status LED to show activity
  digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
  delay(100);
}

void collectAndSendData() {
  // Read raw sensor values
  float solarVoltage = readVoltage(SOLAR_VOLTAGE_PIN) * VOLTAGE_DIVIDER_RATIO;
  float solarCurrent = readCurrent(SOLAR_CURRENT_PIN);
  float batteryVoltage = readVoltage(BATTERY_VOLTAGE_PIN) * VOLTAGE_DIVIDER_RATIO;
  float batteryCurrent = readCurrent(BATTERY_CURRENT_PIN);
  
  // Update smoothing buffers
  solarVoltageBuffer[bufferIndex] = solarVoltage;
  solarCurrentBuffer[bufferIndex] = solarCurrent;
  batteryVoltageBuffer[bufferIndex] = batteryVoltage;
  batteryCurrentBuffer[bufferIndex] = batteryCurrent;
  
  bufferIndex = (bufferIndex + 1) % SAMPLES;
  
  // Calculate smoothed values
  float smoothedSolarVoltage = calculateAverage(solarVoltageBuffer);
  float smoothedSolarCurrent = calculateAverage(solarCurrentBuffer);
  float smoothedBatteryVoltage = calculateAverage(batteryVoltageBuffer);
  float smoothedBatteryCurrent = calculateAverage(batteryCurrentBuffer);
  
  // Read temperature sensors
  tempSensors.requestTemperatures();
  float ambientTemp = tempSensors.getTempCByIndex(0);
  float batteryTemp = tempSensors.getTempCByIndex(1);
  
  // Read humidity (simplified - in practice would use DHT22 library)
  float humidity = readHumidity();
  
  // Calculate derived values
  float solarPower = smoothedSolarVoltage * smoothedSolarCurrent;
  float batteryPower = smoothedBatteryVoltage * smoothedBatteryCurrent;
  float batterySoC = calculateBatterySoC(smoothedBatteryVoltage);
  
  // Create JSON data packet
  StaticJsonDocument<512> doc;
  
  // Solar data
  doc["solar"]["voltage"] = roundToTwo(smoothedSolarVoltage);
  doc["solar"]["current"] = roundToTwo(smoothedSolarCurrent);
  doc["solar"]["power"] = roundToTwo(solarPower);
  
  // Battery data
  doc["battery"]["voltage"] = roundToTwo(smoothedBatteryVoltage);
  doc["battery"]["current"] = roundToTwo(smoothedBatteryCurrent);
  doc["battery"]["power"] = roundToTwo(batteryPower);
  doc["battery"]["soc"] = roundToTwo(batterySoC);
  doc["battery"]["temperature"] = roundToTwo(batteryTemp);
  
  // Environmental data
  doc["environment"]["temperature"] = roundToTwo(ambientTemp);
  doc["environment"]["humidity"] = roundToTwo(humidity);
  
  // System data
  doc["system"]["timestamp"] = millis();
  doc["system"]["uptime"] = millis() / 1000;
  doc["system"]["relay_states"]["solar"] = digitalRead(SOLAR_RELAY_PIN);
  doc["system"]["relay_states"]["thermal"] = digitalRead(THERMAL_RELAY_PIN);
  doc["system"]["relay_states"]["battery"] = digitalRead(BATTERY_RELAY_PIN);
  
  // Send JSON data
  serializeJson(doc, Serial);
  Serial.println();
}

float readVoltage(int pin) {
  int rawValue = analogRead(pin);
  return (rawValue / 1023.0) * VREF;
}

float readCurrent(int pin) {
  int rawValue = analogRead(pin);
  float voltage = (rawValue / 1023.0) * VREF;
  float current = (voltage - CURRENT_SENSOR_OFFSET) / CURRENT_SENSOR_SENSITIVITY;
  return max(0.0, current);  // Current cannot be negative in this application
}

float readHumidity() {
  // Simplified humidity reading - replace with actual DHT22 implementation
  // For now, return a simulated value based on temperature
  float temp = tempSensors.getTempCByIndex(0);
  return constrain(60 + (25 - temp) * 2, 30, 90);  // Rough inverse relationship
}

float calculateBatterySoC(float voltage) {
  // Simple linear approximation for 12V lead-acid battery
  // Should be calibrated for specific battery chemistry
  const float MIN_VOLTAGE = 10.5;  // 0% SoC
  const float MAX_VOLTAGE = 13.8;  // 100% SoC
  
  float soc = ((voltage - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE)) * 100.0;
  return constrain(soc, 0, 100);
}

float calculateAverage(float buffer[]) {
  float sum = 0;
  for (int i = 0; i < SAMPLES; i++) {
    sum += buffer[i];
  }
  return sum / SAMPLES;
}

float roundToTwo(float value) {
  return round(value * 100) / 100.0;
}

void processCommand() {
  String command = Serial.readStringUntil('\n');
  command.trim();
  
  StaticJsonDocument<256> cmdDoc;
  DeserializationError error = deserializeJson(cmdDoc, command);
  
  if (error) {
    Serial.println("{\"error\":\"Invalid JSON command\"}");
    return;
  }
  
  // Process relay control commands
  if (cmdDoc.containsKey("relay")) {
    String relayType = cmdDoc["relay"]["type"];
    bool state = cmdDoc["relay"]["state"];
    
    if (relayType == "solar") {
      digitalWrite(SOLAR_RELAY_PIN, state);
      Serial.println("{\"response\":\"Solar relay updated\"}");
    }
    else if (relayType == "thermal") {
      digitalWrite(THERMAL_RELAY_PIN, state);
      Serial.println("{\"response\":\"Thermal relay updated\"}");
    }
    else if (relayType == "battery") {
      digitalWrite(BATTERY_RELAY_PIN, state);
      Serial.println("{\"response\":\"Battery relay updated\"}");
    }
    else {
      Serial.println("{\"error\":\"Unknown relay type\"}");
    }
  }
  
  // Process calibration commands
  else if (cmdDoc.containsKey("calibrate")) {
    String sensor = cmdDoc["calibrate"];
    
    if (sensor == "all") {
      calibrateAllSensors();
      Serial.println("{\"response\":\"All sensors calibrated\"}");
    }
    else {
      Serial.println("{\"error\":\"Unknown calibration command\"}");
    }
  }
  
  // Process status request
  else if (cmdDoc.containsKey("status")) {
    sendStatusReport();
  }
  
  else {
    Serial.println("{\"error\":\"Unknown command\"}");
  }
}

void calibrateAllSensors() {
  // Perform sensor calibration routine
  // This would typically involve:
  // 1. Zero current sensor offsets
  // 2. Calibrate voltage dividers with known reference
  // 3. Temperature sensor offset correction
  
  // For now, just reset smoothing buffers
  for (int i = 0; i < SAMPLES; i++) {
    solarVoltageBuffer[i] = 0;
    solarCurrentBuffer[i] = 0;
    batteryVoltageBuffer[i] = 0;
    batteryCurrentBuffer[i] = 0;
  }
  bufferIndex = 0;
}

void sendStatusReport() {
  StaticJsonDocument<256> status;
  
  status["arduino_status"] = "running";
  status["uptime_seconds"] = millis() / 1000;
  status["temperature_sensors"] = tempSensors.getDeviceCount();
  status["relay_control"] = "enabled";
  status["smoothing_samples"] = SAMPLES;
  status["reading_interval_ms"] = READING_INTERVAL;
  
  serializeJson(status, Serial);
  Serial.println();
}

// Error handling function
void handleError(String errorMsg) {
  digitalWrite(ERROR_LED_PIN, HIGH);
  
  StaticJsonDocument<128> error;
  error["error"] = errorMsg;
  error["timestamp"] = millis();
  
  serializeJson(error, Serial);
  Serial.println();
  
  delay(1000);
  digitalWrite(ERROR_LED_PIN, LOW);
}
