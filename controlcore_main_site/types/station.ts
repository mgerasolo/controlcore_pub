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
  error?: string
  locationNickname?: string
  stationLocation?: string
  controllerName?: string
  sensorTypeParsed?: string
  enumeratorOrName?: string
}
