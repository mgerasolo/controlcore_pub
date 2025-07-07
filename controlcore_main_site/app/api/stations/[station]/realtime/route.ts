import { NextRequest, NextResponse } from 'next/server'
import pool from '@/lib/db'

export async function GET(
  _req: NextRequest,
  { params }: { params: { station: string } },
) {
  try {
    const { rows } = await pool.query(
      `SELECT sensor_id,
              sensor_type,
              value,
              unit,
              EXTRACT(EPOCH FROM received_at) * 1000 AS timestamp
         FROM sensor_data
        WHERE station_id = $1
          AND received_at > now() - INTERVAL '1 minute'
        ORDER BY received_at`,
      [params.station],
    )
    return NextResponse.json({ success: true, data: rows })
  } catch (err) {
    console.error('realtime api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
