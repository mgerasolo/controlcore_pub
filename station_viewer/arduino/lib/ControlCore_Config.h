#ifndef CONTROL_CORE_CONFIG_H
#define CONTROL_CORE_CONFIG_H

#include <PubSubClient.h>
#include <math.h>

// 💧 Station + Controller Identity
#define LOCATION "excessus-home"
#define STATION_NAME "garden-hydrant"
#define CONTROLLER_ID "uno-r4-wifi-primary"

// 🔐 Max MQTT topic length guard
#define MAX_TOPIC_LEN 128

// 🔧 Build sensor_id string (in-place)
inline void buildSensorID(char* buffer, const char* sensorType, const char* logicalName) {
  snprintf(buffer, 128, "%s_%s_%s_%s_%s", LOCATION, STATION_NAME, CONTROLLER_ID, sensorType, logicalName);
}

// 📨 Publish single sensor message
inline void publishSensorReading(PubSubClient& client, const char* sensor_id, const char* type, float value, const char* unit, int pin, unsigned long timestamp) {
  char topic[MAX_TOPIC_LEN];
  snprintf(topic, sizeof(topic), "controlcore/data/%s/%s", STATION_NAME, sensor_id);

  char payload[256];
  if (isnan(value)) {
    snprintf(payload, sizeof(payload),
      "{\"station\":\"%s\",\"controller\":\"%s\",\"sensor_id\":\"%s\",\"unit\":\"%s\",\"type\":\"%s\",\"pin\":%d,\"timestamp\":%lu,\"error\":\"read_failure\"}",
      STATION_NAME, CONTROLLER_ID, sensor_id, unit, type, pin, timestamp);
  } else {
    snprintf(payload, sizeof(payload),
      "{\"station\":\"%s\",\"controller\":\"%s\",\"sensor_id\":\"%s\",\"value\":%.2f,\"unit\":\"%s\",\"type\":\"%s\",\"pin\":%d,\"timestamp\":%lu}",
      STATION_NAME, CONTROLLER_ID, sensor_id, value, unit, type, pin, timestamp);
  }

  client.publish(topic, payload);
}

#endif // CONTROL_CORE_CONFIG_H
