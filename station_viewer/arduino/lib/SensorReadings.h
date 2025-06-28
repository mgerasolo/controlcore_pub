#ifndef SENSOR_READINGS_H
#define SENSOR_READINGS_H

#include "SensorConfig.h"

float readValveState(const SensorConfig& sensor);
float readWaterPressure(const SensorConfig& sensor);
float readWaterFlow(const SensorConfig& sensor);
float readTemperatureSHT(const SensorConfig& sensor);
float readHumiditySHT(const SensorConfig& sensor);
float readPressureBMP(const SensorConfig& sensor);
float readTemperatureBMP(const SensorConfig& sensor);
float readSoilMoisture(const SensorConfig& sensor);
float readLightIntensity(const SensorConfig& sensor);

#endif // SENSOR_READINGS_H
