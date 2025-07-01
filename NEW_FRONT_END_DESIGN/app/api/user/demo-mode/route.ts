import { NextRequest, NextResponse } from "next/server"
import { getCurrentUser } from "@/lib/server/auth-server"
import pool from "@/lib/db"

export async function POST(req: NextRequest) {
  const user = await getCurrentUser()
  if (!user) return NextResponse.json({ success: false }, { status: 401 })

  try {
    const { demo_mode } = await req.json()
    await pool.query("UPDATE users SET demo_mode = $1 WHERE id = $2", [demo_mode, user.id])

    return NextResponse.json({ success: true })
  } catch (err) {
    console.error("Failed to update demo mode:", err)
    return NextResponse.json({ success: false }, { status: 500 })
  }
}
