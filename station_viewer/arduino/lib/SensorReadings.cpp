#include "SensorConfig.h"
#include "SensorReadings.h"

extern bool valveOpen;

static float applyCalibration(const SensorConfig& cfg, float raw) {
  return (raw + cfg.offset) * cfg.scale;
}

float readValveState(const SensorConfig& sensor) {
  float raw = valveOpen ? 1.0f : 0.0f;
  return applyCalibration(sensor, raw);
}

float readWaterPressure(const SensorConfig& sensor) {
  float raw = analogRead(sensor.pin);  // Replace with conversion if needed
  return applyCalibration(sensor, raw);
}

float readWaterFlow(const SensorConfig& sensor) {
  float raw = analogRead(sensor.pin);  // Placeholder for pulse counting
  return applyCalibration(sensor, raw);
}

float readTemperatureSHT(const SensorConfig& sensor) {
  float raw = sht31.readTemperature();
  return applyCalibration(sensor, raw);
}

float readHumiditySHT(const SensorConfig& sensor) {
  float raw = sht31.readHumidity();
  return applyCalibration(sensor, raw);
}

float readPressureBMP(const SensorConfig& sensor) {
  float raw = bmp280.readPressure() / 100.0F;  // Convert Pa to hPa
  return applyCalibration(sensor, raw);
}

float readTemperatureBMP(const SensorConfig& sensor) {
  float raw = bmp280.readTemperature();
  return applyCalibration(sensor, raw);
}

float readSoilMoisture(const SensorConfig& sensor) {
  float raw = analogRead(sensor.pin);  // Consider mapping to percentage
  return applyCalibration(sensor, raw);
}

float readLightIntensity(const SensorConfig& sensor) {
  float raw = analogRead(sensor.pin);  // Consider voltage or lux conversion
  return applyCalibration(sensor, raw);
}
