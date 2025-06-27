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

#define LOCATION "excessus-home"
#define STATION_NAME "garden-hydrant"
#define CONTROLLER_ID "uno-r4-wifi-primary"
#define DEVICE_ID "excessus-home_garden-hydrant_uno-r4-wifi-primary"


#define ID(base, suffix) LOCATION "_" STATION_NAME "_" CONTROLLER_ID "_" base "_" suffix

#define VALVE_SENSOR_ID "BeetsTomatoes-Valve"
#define WATER_PRESSURE_SENSOR_ID "BeetsTomatoes-USSolid"
#define WATER_FLOW_SENSOR_ID "BeetsTomatoes-Grieda"
#define SHT_SENSOR_ID "StationExt-SHT-1"
#define BMP_SENSOR_ID "StationExt-BMP-1"
#define SOIL_SENSOR_ID "BeetsTomatoes-Soil"
#define LIGHT_SENSOR_ID "BeetsTomatoes-Light"

const SensorConfig sensors[] = {
  {
    VALVE_SENSOR_ID,
    ID("valve-state", VALVE_SENSOR_ID),
    "Water Regulator Valve",
    "state",
    -1,
    readValveState,
    "Derived from relay state on pin 8",
    "valve-state"
  },
  {
    WATER_PRESSURE_SENSOR_ID,
    ID("water-pressure", WATER_PRESSURE_SENSOR_ID),
    "Pressure Sensor",
    "PSI",
    A0,
    readWaterPressure,
    "0.5–4.5V analog sensor on A0",
    "water-pressure"
  },
  {
    WATER_FLOW_SENSOR_ID,
    ID("water-flow", WATER_FLOW_SENSOR_ID),
    "Flow Sensor",
    "L/min",
    2,
    readWaterFlow,
    "Pulse output sensor on pin 2",
    "water-flow"
  },
  {
    SHT_SENSOR_ID,
    ID("temperature", SHT_SENSOR_ID),
    "Ambient Temperature",
    "°C",
    -1,
    readTemperatureSHT,
    "SHT31-D over I2C (A4/A5)",
    "temperature"
  },
  {
    SHT_SENSOR_ID,
    ID("humidity", SHT_SENSOR_ID),
    "Ambient Humidity",
    "%RH",
    -1,
    readHumiditySHT,
    "SHT31-D over I2C (A4/A5)",
    "humidity"
  },
  {
    BMP_SENSOR_ID,
    ID("barometric-pressure", BMP_SENSOR_ID),
    "Barometric Pressure",
    "hPa",
    -1,
    readPressureBMP,
    "BMP280 over I2C (A4/A5)",
    "barometric-pressure"
  },
  {
    BMP_SENSOR_ID,
    ID("temperature", BMP_SENSOR_ID),
    "Environmental Temperature",
    "°C",
    -1,
    readTemperatureBMP,
    "BMP280 over I2C (A4/A5)",
    "temperature"
  },
  {
    SOIL_SENSOR_ID,
    ID("soil-moisture", SOIL_SENSOR_ID),
    "Soil Moisture",
    "%",
    A3,
    readSoilMoisture,
    "Capacitive analog soil sensor on A3",
    "soil-moisture"
  },
  {
    LIGHT_SENSOR_ID,
    ID("light-intensity", LIGHT_SENSOR_ID),
    "Light Intensity",
    "lux",
    A5,
    readLightIntensity,
    "LDR voltage divider on A5",
    "light-intensity"
  }
};

const int numSensors = sizeof(sensors) / sizeof(sensors[0]);

#endif // SENSOR_CONFIG_H
