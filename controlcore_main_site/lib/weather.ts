import { Pool } from 'pg'

const histPool = new Pool({
  host: process.env.PG_HOST || 'localhost',
  port: parseInt(process.env.PG_PORT || '5432', 10),
  user: process.env.OPENHIST_USER,
  password: process.env.OPENHIST_PW,
  database: 'openweather_historical',
})

const forePool = new Pool({
  host: process.env.PG_HOST || 'localhost',
  port: parseInt(process.env.PG_PORT || '5432', 10),
  user: process.env.OPENFORE_USER,
  password: process.env.OPENFORE_PW,
  database: 'openweather_forecast',
})

export async function fetchHistorical(limit = 24) {
  const { rows } = await histPool.query(
    `SELECT dt, lat, lon, temp, precipitation_total, wind_speed
     FROM hourly_data
     ORDER BY dt DESC
     LIMIT $1`,
    [limit],
  )
  return rows
}

export async function fetchForecast(limit = 1) {
  const { rows } = await forePool.query(
    `SELECT *
     FROM openweather_forecast_detail
     ORDER BY "timestamp" DESC
     LIMIT $1`,
    [limit],
  )
  return rows
}
