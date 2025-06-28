
#include <Wire.h>
#include <Adafruit_SHT31.h>
#include <Adafruit_BMP280.h>
#include <WiFiS3.h>
#include <PubSubClient.h>
#include <math.h>
#include <ArduinoJson.h>
#include <WiFiUdp.h>
#include <NTPClient.h>

#include "lib/ControlCore_Config.h"
#include "lib/SensorConfig.h"
#include "lib/WiFiCredentials.h"
#include "lib/SensorReadings.h"

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");
bool timeSynced = false;
unsigned long lastNtpSync = 0;
const unsigned long NTP_SYNC_INTERVAL = 3600000UL; // 1 hour

// Relay Control
const int RELAY_PIN = 8;
bool valveOpen = false;
unsigned long valveCloseAt = 0;
const unsigned long MAX_VALVE_DURATION = 15 * 60;

// I2C Sensors
Adafruit_SHT31 sht31 = Adafruit_SHT31();
Adafruit_BMP280 bmp280;

void setValveState(bool open, unsigned long duration = MAX_VALVE_DURATION) {
  valveOpen = open;
  digitalWrite(RELAY_PIN, open ? HIGH : LOW);
  if (open) {
    unsigned long now = millis() / 1000;
    if (duration == 0 || duration > MAX_VALVE_DURATION) duration = MAX_VALVE_DURATION;
    valveCloseAt = now + duration;
  } else {
    valveCloseAt = 0;
  }
}

unsigned long getTimestamp() {
  if (timeSynced) {
    timeClient.update();
    return timeClient.getEpochTime();
  }
  return millis() / 1000;
}


void publishSensorReading(const SensorConfig& sensor, float value) {
  StaticJsonDocument<512> doc;
  doc["station"] = STATION_NAME;
  doc["controller"] = CONTROLLER_ID;
  doc["sensor_id"] = sensor.sensor_id;
  doc["sensor_type"] = sensor.type;
  doc["source_id"] = sensor.source_id;
  doc["unit"] = sensor.unit;
  doc["value"] = value;
  if (isnan(value)) {
    doc["error"] = "read_failure";
  }
  doc["pin"] = sensor.pin;
  doc["timestamp"] = getTimestamp();

  char buffer[512];
  serializeJson(doc, buffer);
  String topic = "controlcore/data/" + String(STATION_NAME) + "/" + String(sensor.sensor_id);
  mqttClient.publish(topic.c_str(), buffer);
}

void reconnectMQTT() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect(DEVICE_ID)) {
      mqttClient.subscribe("controlcore/command/#");
    } else delay(2000);
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<512> doc;
  deserializeJson(doc, payload, length);
  const char* command = doc["command"];
  const char* sensorId = doc["sensor_id"];
  if (!command || !sensorId) return;

  if (strcmp(command, "open") == 0 || strcmp(command, "on") == 0) {
    unsigned long duration = doc["value"] | 0;
    if (duration == 0 || duration > MAX_VALVE_DURATION)
      duration = MAX_VALVE_DURATION;
    setValveState(true, duration);
  } else if (strcmp(command, "close") == 0 || strcmp(command, "off") == 0) {
    setValveState(false);
  }
}

void setup() {

  Serial.begin(115200);
  delay(1500);

  Wire.begin();
  delay(1500);
  pinMode(RELAY_PIN, OUTPUT);
  setValveState(false);

  sht31.begin(0x44);
  bmp280.begin(0x76);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(500);

  delay(5000);  // NTP Init
  timeClient.begin();
  while (!(timeSynced = timeClient.forceUpdate())) {
    delay(500);
  }
  lastNtpSync = millis();

  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
}

void loop() {
  if (!mqttClient.connected()) reconnectMQTT();
  mqttClient.loop();

  if (millis() - lastNtpSync >= NTP_SYNC_INTERVAL) {
    timeSynced = timeClient.forceUpdate();
    lastNtpSync = millis();
  }

  if (valveOpen && valveCloseAt > 0 && getTimestamp() >= valveCloseAt) {
    setValveState(false);
  }

  static unsigned long lastPublish = 0;
  if (millis() - lastPublish > 10000) {
    lastPublish = millis();
    for (int i = 0; i < numSensors; ++i) {
      float val = sensors[i].readFunc(sensors[i]);
      publishSensorReading(sensors[i], val);
    }
  }
}
