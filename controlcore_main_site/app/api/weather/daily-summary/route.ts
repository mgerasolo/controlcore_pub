import { NextResponse } from 'next/server'
import { fetchDailySummary } from '@/lib/weather'

export async function GET() {
  try {
    const data = await fetchDailySummary()
    return NextResponse.json({ success: true, data })
  } catch (err) {
    console.error('daily summary api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
