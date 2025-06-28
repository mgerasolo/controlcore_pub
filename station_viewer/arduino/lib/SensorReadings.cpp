#include "SensorConfig.h"
#include "SensorReadings.h"

float readValveState(const SensorConfig& sensor) {
  return 0;  // Replace with real logic
}

float readWaterPressure(const SensorConfig& sensor) {
  return analogRead(sensor.pin);  // Replace with conversion if needed
}

float readWaterFlow(const SensorConfig& sensor) {
  return 0;  // Replace with pulse counting logic
}

float readTemperatureSHT(const SensorConfig& sensor) {
  return sht31.readTemperature();
}

float readHumiditySHT(const SensorConfig& sensor) {
  return sht31.readHumidity();
}

float readPressureBMP(const SensorConfig& sensor) {
  return bmp280.readPressure() / 100.0F;  // Convert Pa to hPa
}

float readTemperatureBMP(const SensorConfig& sensor) {
  return bmp280.readTemperature();
}

float readSoilMoisture(const SensorConfig& sensor) {
  return analogRead(sensor.pin);  // Consider mapping to percentage
}

float readLightIntensity(const SensorConfig& sensor) {
  return analogRead(sensor.pin);  // Consider voltage or lux conversion
}
