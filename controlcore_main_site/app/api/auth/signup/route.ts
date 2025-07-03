import { type NextRequest, NextResponse } from "next/server"
import { signUp, createSession } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const { email, password, firstName, lastName } = await request.json()

    if (!email || !password || !firstName || !lastName) {
      return NextResponse.json({ success: false, error: "All fields are required" }, { status: 400 })
    }

    if (password.length < 6) {
      return NextResponse.json({ success: false, error: "Password must be at least 6 characters" }, { status: 400 })
    }

    const result = await signUp(email, password, firstName, lastName)

    if (!result.success || !result.user) {
      return NextResponse.json(result, { status: 400 })
    }

    // Create JWT token and persist session
    const token = await createSession(result.user)

    // Construct response and set HTTP-only cookie
    const response = NextResponse.json({
      success: true,
      user: result.user,
    })
    response.cookies.set("auth-token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24, // 24 hours
      path: "/",
    })

    return response
  } catch (error) {
    console.error("Sign up error:", error)
    return NextResponse.json({ success: false, error: "Internal server error" }, { status: 500 })
  }
}
