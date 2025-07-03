import { NextResponse } from 'next/server'
import { fetchStations } from '@/lib/stations'

export async function GET() {
  try {
    const stations = await fetchStations()
    return NextResponse.json({ success: true, stations })
  } catch (err) {
    console.error('stations api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
