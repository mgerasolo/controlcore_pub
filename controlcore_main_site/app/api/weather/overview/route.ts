import { NextResponse } from 'next/server'
import { fetchOverview } from '@/lib/weather'

export async function GET() {
  try {
    const data = await fetchOverview()
    return NextResponse.json({ success: true, data })
  } catch (err) {
    console.error('overview api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
