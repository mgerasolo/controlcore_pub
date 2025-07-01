import { NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import { verifyJWT } from "@/lib/auth"

export async function GET(req: NextRequest) {
  try {
    const cookieStore = cookies()
    const token = cookieStore.get("auth-token")?.value

    if (!token) {
      return NextResponse.json({ success: false, error: "No token provided" }, { status: 401 })
    }

    const user = await verifyJWT(token)

    if (!user) {
      return NextResponse.json({ success: false, error: "Invalid or expired session" }, { status: 401 })
    }

    return NextResponse.json({ success: true, user })
  } catch (error) {
    console.error("Session retrieval error:", error)
    return NextResponse.json({ success: false, error: "Internal server error" }, { status: 500 })
  }
}
