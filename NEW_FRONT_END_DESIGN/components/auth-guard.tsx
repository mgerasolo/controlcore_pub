"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import type { User } from "@/lib/types"
import { Loader2 } from "lucide-react"

interface AuthGuardProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/session", { credentials: "include" })
        const currentUser = await res.json()
        setUser(currentUser)

        if (requireAuth && !currentUser) {
          router.push("/auth/signin")
          return
        }

        if (!requireAuth && currentUser) {
          router.push("/dashboard")
          return
        }
      } catch (error) {
        console.error("Auth check failed:", error)
        if (requireAuth) {
          router.push("/auth/signin")
        }
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [requireAuth, router])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="h-8 w-8 animate-spin mx-auto" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (requireAuth && !user) {
    return null // Will redirect to signin
  }

  if (!requireAuth && user) {
    return null // Will redirect to dashboard
  }

  return <>{children}</>
}
