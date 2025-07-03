import { Pool } from "pg";
import pool from "./db";

const histPool = new Pool({
  host: process.env.PG_HOST || "localhost",
  port: parseInt(process.env.PG_PORT || "5432", 10),
  user: process.env.OPENHIST_USER,
  password: process.env.OPENHIST_PW,
  database: "openweather_historical",
});

const forePool = new Pool({
  host: process.env.PG_HOST || "localhost",
  port: parseInt(process.env.PG_PORT || "5432", 10),
  user: process.env.OPENFORE_USER,
  password: process.env.OPENFORE_PW,
  database: "openweather_forecast",
});

export async function fetchHistorical(limit = 24) {
  const { rows } = await histPool.query(
    `SELECT h.dt,
            h.lat,
            h.lon,
            h.temp,
            d.precipitation_total,
            h.wind_speed
       FROM hourly_data h
       LEFT JOIN daily_summary_data d
              ON to_timestamp(h.dt)::date = to_timestamp(d.date)::date
             AND h.location_id = d.location_id
      ORDER BY h.dt DESC
      LIMIT $1`,
    [limit],
  );
  return rows;
}

export async function fetchForecast(limit = 1) {
  const { rows } = await forePool.query(
    `SELECT *
     FROM openweather_forecast_detail
     ORDER BY "timestamp" DESC
     LIMIT $1`,
    [limit],
  );
  return rows;
}

export async function fetchDailySummary(limit = 20) {
  const { rows } = await histPool.query(
    `SELECT date,
            lat,
            lon,
            temperature_min,
            temperature_max,
            precipitation_total,
            wind_max_speed,
            wind_max_direction,
            humidity_afternoon,
            cloud_cover_afternoon
       FROM daily_summary_data
      ORDER BY date DESC
      LIMIT $1`,
    [limit],
  );
  return rows;
}

export async function fetchOverview(limit = 2) {
  const rowCount = Math.max(2, limit);
  const { rows } = await forePool.query(
    `SELECT date,
            weather_overview,
            day
       FROM overview_data
      ORDER BY date DESC
      LIMIT $1`,
    [rowCount],
  );
  return rows;
}

export async function fetchBaselineSensor(sourceId: string) {
  const { rows } = await pool.query(
    `SELECT sensor_type, value, unit, received_at
       FROM sensor_data
      WHERE source_id = $1
      ORDER BY received_at DESC
      LIMIT 1`,
    [sourceId],
  );
  return rows[0] || null;
}
