import { NextResponse } from 'next/server'
import { fetchStations } from '@/lib/stations'

export async function GET() {
  try {
    const stations = await fetchStations()
    const serialized = stations.map((s) => ({
      ...s,
      lastUpdate: s.lastUpdate ? s.lastUpdate.toISOString() : null,
      health: s.health.map((h) => ({
        ...h,
        last_reported: h.last_reported ? h.last_reported.toISOString() : null,
      })),
    }))
    return NextResponse.json({ success: true, stations: serialized })
  } catch (err) {
    console.error('stations api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
