import type { SensorReading, PhysicalGroup, LogicalGroup } from "@/types/station"

// Parse the fully qualified sensor string (source_id)
export function parseSensorId(id: string) {
  const parts = id.split("_")
  const [locationNickname = "", stationLocation = "", controllerName = "", sensorTypeParsed = "", ...rest] = parts
  const enumeratorOrName = rest.join("_")
  return { locationNickname, stationLocation, controllerName, sensorTypeParsed, enumeratorOrName }
}

export function groupSensorsPhysically(sensors: SensorReading[]): PhysicalGroup {
  const grouped: PhysicalGroup = {}

  sensors.forEach((sensor) => {
    if (!grouped[sensor.station]) {
      grouped[sensor.station] = {}
    }
    if (!grouped[sensor.station][sensor.controller]) {
      grouped[sensor.station][sensor.controller] = []
    }
    grouped[sensor.station][sensor.controller].push(sensor)
  })

  return grouped
}

export function groupSensorsLogically(sensors: SensorReading[]): LogicalGroup {
  const grouped: LogicalGroup = {}

  sensors.forEach((sensor) => {
    if (!grouped[sensor.sensor_type]) {
      grouped[sensor.sensor_type] = []
    }
    grouped[sensor.sensor_type].push(sensor)
  })

  return grouped
}

export function isDataFresh(timestamp: Date, maxAgeMinutes = 5): boolean {
  const now = new Date()
  const diffMinutes = (now.getTime() - timestamp.getTime()) / (1000 * 60)
  return diffMinutes <= maxAgeMinutes
}

const iconMap: { [key: string]: string } = {
  "water-flow": "🌊",
  "water-pressure": "💧",
  "barometric-pressure": "📈",
  temperature: "🌡️",
  humidity: "💦",
  "valve-state": "🔄",
  "soil-moisture": "🌱",
  "light-intensity": "☀️",
  default: "📡",
}

const labelMap: { [key: string]: string } = {
  "water-flow": "Water Flow Sensors",
  "water-pressure": "Water Pressure",
  "barometric-pressure": "Barometric Pressure",
  temperature: "Temperature",
  humidity: "Humidity",
  "valve-state": "Valve State",
  "soil-moisture": "Soil Moisture",
  "light-intensity": "Light Intensity",
}

export function getSensorTypeIcon(sensorType: string): string {
  return iconMap[sensorType] || iconMap.default
}

export function getSensorTypeLabel(sensorType: string): string {
  return labelMap[sensorType] || sensorType
}
