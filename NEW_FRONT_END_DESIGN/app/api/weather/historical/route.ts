import { NextResponse } from 'next/server'
import { fetchHistorical } from '@/lib/weather'

export async function GET() {
  try {
    const data = await fetchHistorical()
    return NextResponse.json({ success: true, data })
  } catch (err) {
    console.error('historical api error', err)
    return NextResponse.json(
      { success: false, error: 'Internal server error' },
      { status: 500 },
    )
  }
}
