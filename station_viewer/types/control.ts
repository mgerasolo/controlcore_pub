export interface ControlMessage {
  station: string
  controller: string
  sensor_id: string
  sensor_type: string
  unit: string
  value: number
  command: string
  source: string
  requestor_id: string
  timestamp: number
}
