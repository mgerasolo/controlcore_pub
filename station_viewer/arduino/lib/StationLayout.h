#ifndef STATION_LAYOUT_H
#define STATION_LAYOUT_H

#include "SensorConfig.h"

// === Station Identity ===
#define LOCATION "excessus-home"
#define STATION_NAME "garden-hydrant"
#define CONTROLLER_ID "uno-r4-wifi-primary"
#define DEVICE_ID LOCATION "_" STATION_NAME "_" CONTROLLER_ID

#define ID(base, suffix) LOCATION "_" STATION_NAME "_" CONTROLLER_ID "_" base "_" suffix

// === Sensor Identifiers ===
#define VALVE_SENSOR_ID "BeetsTomatoes-USSolid"
#define WATER_PRESSURE_SENSOR_ID "BeetsTomatoes-Foush"
#define WATER_FLOW_SENSOR_ID "BeetsTomatoes-Grieda"
#define SHT_SENSOR_ID "StationExt-SHT-1"
#define BMP_SENSOR_ID "StationExt-BMP-1"
#define SOIL_SENSOR_ID "BeetsTomatoes-Soil"
#define LIGHT_SENSOR_ID "BeetsTomatoes-Light"

// === Sensor Layout ===
const SensorConfig sensors[] = {
  {
    VALVE_SENSOR_ID,
    ID("valve-state", VALVE_SENSOR_ID),
    "Water Regulator Valve",
    "state",
    -1,
    readValveState,
    "Derived from relay state on pin 8",
    "valve-state",
    0.0,
    1.0
  },
  {
    WATER_PRESSURE_SENSOR_ID,
    ID("water-pressure", WATER_PRESSURE_SENSOR_ID),
    "Pressure Sensor",
    "PSI",
    A0,
    readWaterPressure,
    "0.5–4.5V analog sensor on A0",
    "water-pressure",
    0.0,
    1.0
  },
  {
    WATER_FLOW_SENSOR_ID,
    ID("water-flow", WATER_FLOW_SENSOR_ID),
    "Flow Sensor",
    "L/min",
    2,
    readWaterFlow,
    "Pulse output sensor on pin 2",
    "water-flow",
    0.0,
    1.0
  },
  {
    SHT_SENSOR_ID,
    ID("temperature", SHT_SENSOR_ID),
    "Ambient Temperature",
    "\xC2\xB0C",
    -1,
    readTemperatureSHT,
    "SHT31-D over I2C (A4/A5)",
    "temperature",
    0.0,
    1.0
  },
  {
    SHT_SENSOR_ID,
    ID("humidity", SHT_SENSOR_ID),
    "Ambient Humidity",
    "%RH",
    -1,
    readHumiditySHT,
    "SHT31-D over I2C (A4/A5)",
    "humidity",
    0.0,
    1.0
  },
  {
    BMP_SENSOR_ID,
    ID("barometric-pressure", BMP_SENSOR_ID),
    "Barometric Pressure",
    "hPa",
    -1,
    readPressureBMP,
    "BMP280 over I2C (A4/A5)",
    "barometric-pressure",
    0.0,
    1.0
  },
  {
    BMP_SENSOR_ID,
    ID("temperature", BMP_SENSOR_ID),
    "Environmental Temperature",
    "\xC2\xB0C",
    -1,
    readTemperatureBMP,
    "BMP280 over I2C (A4/A5)",
    "temperature",
    0.0,
    1.0
  },
  {
    SOIL_SENSOR_ID,
    ID("soil-moisture", SOIL_SENSOR_ID),
    "Soil Moisture",
    "%",
    A3,
    readSoilMoisture,
    "Capacitive analog soil sensor on A3",
    "soil-moisture",
    0.0,
    1.0
  },
  {
    LIGHT_SENSOR_ID,
    ID("light-intensity", LIGHT_SENSOR_ID),
    "Light Intensity",
    "lux",
    A5,
    readLightIntensity,
    "LDR voltage divider on A5",
    "light-intensity",
    0.0,
    1.0
  }
};

const int numSensors = sizeof(sensors) / sizeof(sensors[0]);

#endif // STATION_LAYOUT_H
