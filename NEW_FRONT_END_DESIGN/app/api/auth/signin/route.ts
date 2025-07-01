import { type NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import { signIn, createSession } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json({ success: false, error: "Email and password are required" }, { status: 400 })
    }

    const result = await signIn(email, password)

    if (!result.success || !result.user) {
      return NextResponse.json(result, { status: 401 })
    }

    // Create JWT token and persist session
    const token = await createSession(result.user)

    // Set HTTP-only cookie
    const response = NextResponse.json({
      success: true,
      user: result.user,
    })

    response.cookies.set("auth-token", token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24,
      path: "/",
      credentials: "include"
    })

    return response

  } catch (error) {
    console.error("Sign in error:", error)
    return NextResponse.json({ success: false, error: "Internal server error" }, { status: 500 })
  }
}
