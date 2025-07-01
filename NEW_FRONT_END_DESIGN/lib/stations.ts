import pool from './db'

export interface Sensor {
  station_id: string
  controller_id: string
  sensor_id: string
  sensor_type: string
  value: number | null
  unit: string | null
  pin: number | null
  source_id: string
  timestamp: number
}

export interface StationData {
  station: string
  controller_id: string
  status: 'online' | 'offline'
  sensors: Sensor[]
  lastUpdate: Date | null
}

export async function fetchStations(): Promise<StationData[]> {
  const { rows: controllers } = await pool.query(
    'SELECT controller_id, station_id, last_seen FROM controllers'
  )

  const { rows: sensors } = await pool.query(`
    SELECT DISTINCT ON (station_id, controller_id, sensor_id, sensor_type)
      station_id,
      controller_id,
      sensor_id,
      sensor_type,
      value,
      unit,
      pin,
      source_id,
      EXTRACT(EPOCH FROM received_at) * 1000 AS timestamp
    FROM sensor_data
    ORDER BY station_id, controller_id, sensor_id, sensor_type, received_at DESC
  `)

  const stationMap: Record<string, StationData> = {}

  for (const c of controllers) {
    const stationId = c.station_id || 'unknown'
    const last = c.last_seen ? new Date(c.last_seen) : null
    const status = last && Date.now() - last.getTime() < 5 * 60 * 1000 ? 'online' : 'offline'
    stationMap[`${stationId}`] = {
      station: stationId,
      controller_id: c.controller_id,
      status,
      sensors: [],
      lastUpdate: last,
    }
  }

  for (const s of sensors) {
    const station = stationMap[s.station_id]
    if (!station) continue
    station.sensors.push({
      station_id: s.station_id,
      controller_id: s.controller_id,
      sensor_id: s.sensor_id,
      sensor_type: s.sensor_type,
      value: s.value,
      unit: s.unit,
      pin: s.pin,
      source_id: s.source_id,
      timestamp: s.timestamp,
    })
  }

  return Object.values(stationMap)
}
