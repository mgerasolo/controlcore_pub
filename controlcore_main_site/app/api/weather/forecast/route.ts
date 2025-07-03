import { NextResponse } from 'next/server'
import { fetchForecast } from '@/lib/weather'

export async function GET() {
  try {
    const data = await fetchForecast()
    return NextResponse.json({ success: true, data })
  } catch (err) {
    console.error('forecast api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
