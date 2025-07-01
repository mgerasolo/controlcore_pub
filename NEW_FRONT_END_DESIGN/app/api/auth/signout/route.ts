import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { deleteSession } from "@/lib/auth"

export async function POST() {
  try {
    const cookieStore = await cookies()
    const token = cookieStore.get("auth-token")?.value
    if (token) {
      await deleteSession(token)
    }
    const response = NextResponse.json({ success: true })
    response.cookies.delete("auth-token", { path: "/" })
    return response
  } catch (error) {
    console.error("Sign out error:", error)
    return NextResponse.json({ success: false, error: "Internal server error" }, { status: 500 })
  }
}
