export interface SensorReading {
  station: string
  controller: string
  sensor_id: string
  source_id?: string
  sensor_type: string
  unit: string
  value: number
  pin: number
  timestamp: Date
  // Parsed fields from source_id
  locationNickname?: string
  stationLocation?: string
  controllerName?: string
  sensorTypeParsed?: string
  enumeratorOrName?: string
}

export interface StationData {
  id: string
  name: string
  sensors: SensorReading[]
  lastUpdate: Date
}

export interface GroupedSensors {
  [key: string]: SensorReading[]
}

export interface PhysicalGroup {
  [station: string]: {
    [controller: string]: SensorReading[]
  }
}

export interface LogicalGroup {
  [sensorType: string]: SensorReading[]
}
