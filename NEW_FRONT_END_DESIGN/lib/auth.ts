import { cookies } from "next/headers"
import bcrypt from "bcryptjs"
import { SignJWT, jwtVerify } from "jose"

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

// Mock database functions - replace with real PostgreSQL queries
const mockUsers: (User & { passwordHash: string })[] = [
  {
    id: 1,
    email: "demo@controlcore.com",
    passwordHash: "$2a$10$rOzJqQZQQQQQQQQQQQQQQu", // 'demo123'
    firstName: "Demo",
    lastName: "User",
    role: "admin",
    demoMode: true,
    isActive: true,
  },
  {
    id: 2,
    email: "admin@controlcore.com",
    passwordHash: "$2a$10$rOzJqQZQQQQQQQQQQQQQQu", // 'admin123'
    firstName: "System",
    lastName: "Administrator",
    role: "admin",
    demoMode: false,
    isActive: true,
  },
]

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

    // In real implementation, fetch user from database
    const user = mockUsers.find((u) => u.id === payload.userId)
    if (!user || !user.isActive) return null

    return {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      demoMode: user.demoMode,
      isActive: user.isActive,
    }
  } catch {
    return null
  }
}

export async function getCurrentUser(): Promise<User | null> {
  const cookieStore = await cookies()
  const token = cookieStore.get("auth-token")?.value

  if (!token) return null

  return verifyJWT(token)
}

export async function signIn(email: string, password: string): Promise<AuthResult> {
  // In real implementation, query PostgreSQL
  const user = mockUsers.find((u) => u.email === email)

  if (!user) {
    return { success: false, error: "Invalid email or password" }
  }

  // For demo, accept any password for demo users
  const isValidPassword = user.demoMode ? true : await verifyPassword(password, user.passwordHash)

  if (!isValidPassword) {
    return { success: false, error: "Invalid email or password" }
  }

  if (!user.isActive) {
    return { success: false, error: "Account is deactivated" }
  }

  return {
    success: true,
    user: {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      demoMode: user.demoMode,
      isActive: user.isActive,
    },
  }
}

export async function signUp(
  email: string,
  password: string,
  firstName: string,
  lastName: string,
): Promise<AuthResult> {
  // Check if user already exists
  const existingUser = mockUsers.find((u) => u.email === email)
  if (existingUser) {
    return { success: false, error: "User already exists" }
  }

  // In real implementation, insert into PostgreSQL
  const passwordHash = await hashPassword(password)
  const newUser: User & { passwordHash: string } = {
    id: mockUsers.length + 1,
    email,
    passwordHash,
    firstName,
    lastName,
    role: "user",
    demoMode: true, // New users start in demo mode
    isActive: true,
  }

  mockUsers.push(newUser)

  return {
    success: true,
    user: {
      id: newUser.id,
      email: newUser.email,
      firstName: newUser.firstName,
      lastName: newUser.lastName,
      role: newUser.role,
      demoMode: newUser.demoMode,
      isActive: newUser.isActive,
    },
  }
}
