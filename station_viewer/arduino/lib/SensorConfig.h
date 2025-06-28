#ifndef SENSOR_CONFIG_H
#define SENSOR_CONFIG_H

#include <Adafruit_SHT31.h>
#include <Adafruit_BMP280.h>
#include <Wire.h>

// === I2C Sensors (shared bus) ===
extern Adafruit_SHT31 sht31;
extern Adafruit_BMP280 bmp280;

struct SensorConfig {
  const char* sensor_id;
  const char* source_id;
  const char* name;
  const char* unit;
  int pin;  // -1 for I2C-based sensors
  float (*readFunc)(const SensorConfig&);
  const char* notes;
  const char* type;  // Canonical sensor_type
  float offset;      // calibration offset added to raw reading
  float scale;       // calibration multiplier applied after offset
};

// === Function declarations ===
float readValveState(const SensorConfig& sensor);
float readWaterPressure(const SensorConfig& sensor);
float readWaterFlow(const SensorConfig& sensor);
float readTemperatureSHT(const SensorConfig& sensor);
float readHumiditySHT(const SensorConfig& sensor);
float readPressureBMP(const SensorConfig& sensor);
float readTemperatureBMP(const SensorConfig& sensor);
float readSoilMoisture(const SensorConfig& sensor);
float readLightIntensity(const SensorConfig& sensor);

extern const SensorConfig sensors[];
extern const int numSensors;



#endif // SENSOR_CONFIG_H
