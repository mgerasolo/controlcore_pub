import { NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function GET() {
  try {
    const { rows } = await pool.query(
      `SELECT id, zone_id, station, controller_id, start_time, duration_seconds, status
       FROM watering_schedule
       WHERE start_time >= now() - INTERVAL '1 day'
       ORDER BY start_time`
    )
    return NextResponse.json({ success: true, schedule: rows })
  } catch (err) {
    console.error('schedule api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 }
    )
  }
}
