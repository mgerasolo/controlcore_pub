import bcrypt from "bcryptjs"
import { SignJWT, jwtVerify } from "jose"
import pool from "./db"

const JWT_SECRET = new TextEncoder().encode(process.env.JWT_SECRET || "your-secret-key")

export interface User {
  id: number
  email: string
  firstName: string | null
  lastName: string | null
  role: string
  demoMode: boolean
  isActive: boolean
}

export interface AuthResult {
  success: boolean
  user?: User
  error?: string
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export async function createJWT(user: User): Promise<string> {
  return new SignJWT({
    userId: user.id,
    email: user.email,
    role: user.role,
    demoMode: user.demoMode,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setExpirationTime("24h")
    .setIssuedAt()
    .sign(JWT_SECRET)
}

export async function verifyJWT(token: string): Promise<User | null> {
  try {
    const { payload } = await jwtVerify(token, JWT_SECRET)
    const { rows } = await pool.query(
      "SELECT id, email, first_name, last_name, role, demo_mode, is_active FROM users WHERE id = $1",
      [payload.userId],
    )
    const user = rows[0]
    if (!user || !user.is_active) return null

    return {
      id: user.id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      role: user.role,
      demoMode: user.demo_mode,
      isActive: user.is_active,
    }
  } catch {
    return null
  }
}

export async function signIn(email: string, password: string): Promise<AuthResult> {
  const { rows } = await pool.query(
    "SELECT id, email, password_hash, first_name, last_name, role, demo_mode, is_active FROM users WHERE email = $1",
    [email],
  )
  const user = rows[0]
  if (!user) {
    return { success: false, error: "Invalid email or password" }
  }

  const isValidPassword = user.demo_mode ? true : await verifyPassword(password, user.password_hash)
  if (!isValidPassword) {
    return { success: false, error: "Invalid email or password" }
  }

  if (!user.is_active) {
    return { success: false, error: "Account is deactivated" }
  }

  return {
    success: true,
    user: {
      id: user.id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      role: user.role,
      demoMode: user.demo_mode,
      isActive: user.is_active,
    },
  }
}

export async function signUp(
  email: string,
  password: string,
  firstName: string,
  lastName: string,
): Promise<AuthResult> {
  const existing = await pool.query("SELECT id FROM users WHERE email = $1", [email])
  if (existing.rows.length > 0) {
    return { success: false, error: "User already exists" }
  }

  const passwordHash = await hashPassword(password)
  const { rows } = await pool.query(
    `INSERT INTO users (email, password_hash, first_name, last_name) \
     VALUES ($1, $2, $3, $4) \
     RETURNING id, email, first_name, last_name, role, demo_mode, is_active`,
    [email, passwordHash, firstName, lastName],
  )
  const newUser = rows[0]

  return {
    success: true,
    user: {
      id: newUser.id,
      email: newUser.email,
      firstName: newUser.first_name,
      lastName: newUser.last_name,
      role: newUser.role,
      demoMode: newUser.demo_mode,
      isActive: newUser.is_active,
    },
  }
}
