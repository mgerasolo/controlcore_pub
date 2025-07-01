"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  ArrowRight,
  Activity,
  Brain,
  Shield,
  Smartphone,
  BarChart3,
  Leaf,
  Users,
  CheckCircle,
  Droplets,
  Database,
  Wifi,
  Cloud,
} from "lucide-react"
import { Navigation } from "@/components/navigation"
import { useControlCoreTheme } from "@/components/theme-provider"
import { getTheme } from "@/lib/themes"

export default function HomePage() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const { themeMode } = useControlCoreTheme()
  const theme = getTheme(themeMode)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/session", {
          credentials: "include",
        })
        const data = await res.json()
        setUser(data.success ? data.user : null)
      } catch (error) {
        console.error("Auth check failed:", error)
      } finally {
        setLoading(false)
      }
    }

    checkAuth()
  }, [])

  const features = [
    {
      icon: Activity,
      title: "Real-time Monitoring",
      description: "MQTT-powered sensor data with 30-second updates from your irrigation stations",
    },
    {
      icon: Brain,
      title: "AI-Powered Decisions",
      description: "Machine learning algorithms optimize water usage and predict maintenance needs",
    },
    {
      icon: Smartphone,
      title: "Mobile-First Design",
      description: "Control and monitor your systems from anywhere with responsive interface",
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "PostgreSQL-backed historical analysis and trend visualization",
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Secure authentication with role-based access and audit logging",
    },
    {
      icon: Users,
      title: "Multi-User Support",
      description: "Team collaboration with demo mode for training and live system access",
    },
  ]

  if (loading) {
    return (
      <div className="min-h-screen enhanced-bg">
        <Navigation />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="animate-pulse">Loading...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen enhanced-bg">
      <Navigation />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <Badge variant="secondary" className="w-fit">
                <Leaf className="h-3 w-3 mr-1" />
                Professional Agricultural Management
              </Badge>
              <h1 className="text-4xl lg:text-6xl font-bold tracking-tight">
                Smart Irrigation
                <span className="text-primary block">Control System</span>
              </h1>
              <p className="text-xl text-muted-foreground max-w-lg">
                Complete agricultural automation with MQTT real-time control, AI optimization, and weather integration.
                Start with demo mode or connect your live system.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              {user ? (
                <Button size="lg" asChild className={theme.features.animations ? "enhanced-hover" : ""}>
                  <Link href="/dashboard">
                    Go to Dashboard
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
              ) : (
                <>
                  <Button size="lg" asChild className={theme.features.animations ? "enhanced-hover" : ""}>
                    <Link href="/auth/signup">
                      Start Free Trial
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Link>
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    asChild
                    className={theme.features.animations ? "enhanced-hover" : ""}
                  >
                    <Link href="/auth/signin">Sign In</Link>
                  </Button>
                </>
              )}
            </div>

            {!user && (
              <div className="flex items-center space-x-8 pt-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">Demo</div>
                  <div className="text-sm text-muted-foreground">Mode Available</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">24/7</div>
                  <div className="text-sm text-muted-foreground">Monitoring</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">AI</div>
                  <div className="text-sm text-muted-foreground">Optimized</div>
                </div>
              </div>
            )}
          </div>

          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <Card
                className={`bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0 ${theme.features.animations ? "float-animation" : ""} ${theme.features.shadows ? "enhanced-shadow" : ""}`}
              >
                <CardContent className="p-6">
                  <Wifi className="h-8 w-8 mb-4" />
                  <div className="text-2xl font-bold">MQTT</div>
                  <div className="text-blue-100">Real-time Control</div>
                  <div className="mt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white border-0">
                      Live & Demo
                    </Badge>
                  </div>
                </CardContent>
              </Card>
              <Card
                className={`bg-gradient-to-br from-green-500 to-green-600 text-white border-0 ${theme.features.animations ? "float-animation" : ""} ${theme.features.shadows ? "enhanced-shadow" : ""}`}
              >
                <CardContent className="p-6">
                  <Database className="h-8 w-8 mb-4" />
                  <div className="text-2xl font-bold">PostgreSQL</div>
                  <div className="text-green-100">Data Storage</div>
                  <div className="mt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white border-0">
                      Production Ready
                    </Badge>
                  </div>
                </CardContent>
              </Card>
              <Card
                className={`bg-gradient-to-br from-orange-500 to-orange-600 text-white border-0 ${theme.features.animations ? "float-animation" : ""} ${theme.features.shadows ? "enhanced-shadow" : ""}`}
              >
                <CardContent className="p-6">
                  <Cloud className="h-8 w-8 mb-4" />
                  <div className="text-2xl font-bold">Weather</div>
                  <div className="text-orange-100">API Integration</div>
                  <div className="mt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white border-0">
                      OpenWeather
                    </Badge>
                  </div>
                </CardContent>
              </Card>
              <Card
                className={`bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0 ${theme.features.animations ? "float-animation" : ""} ${theme.features.shadows ? "enhanced-shadow" : ""}`}
              >
                <CardContent className="p-6">
                  <Brain className="h-8 w-8 mb-4" />
                  <div className="text-2xl font-bold">AI Core</div>
                  <div className="text-purple-100">Smart Decisions</div>
                  <div className="mt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white border-0">
                      Machine Learning
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="text-center space-y-4 mb-16">
          <h2 className="text-3xl lg:text-4xl font-bold">Complete Agricultural Solution</h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Professional-grade irrigation management with demo mode for training and live system integration
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card
                key={index}
                className={`border-0 ${theme.features.glassEffect ? "glass-card" : ""} ${theme.features.shadows ? "enhanced-shadow" : "shadow-lg"} ${theme.features.animations ? "enhanced-hover" : "hover:shadow-xl"} transition-shadow`}
              >
                <CardHeader>
                  <div
                    className={`h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 ${theme.features.animations ? "pulse-glow" : ""}`}
                  >
                    <Icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* Demo vs Live Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid lg:grid-cols-2 gap-8">
          <Card
            className={`border-blue-200 ${theme.features.animations ? "enhanced-hover" : ""}`}
            style={{
              background: themeMode.includes("dark")
                ? "linear-gradient(135deg, hsl(217 91% 15%) 0%, hsl(217 91% 20%) 100%)"
                : "linear-gradient(135deg, hsl(214 100% 97%) 0%, hsl(214 100% 95%) 100%)",
            }}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className={`w-6 h-6 ${themeMode.includes("dark") ? "text-blue-400" : "text-blue-600"}`} />
                Demo Mode
              </CardTitle>
              <CardDescription>Perfect for learning and demonstration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-blue-400" : "text-blue-600"}`}
                  />
                  Simulated agricultural data
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-blue-400" : "text-blue-600"}`}
                  />
                  Safe testing environment
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-blue-400" : "text-blue-600"}`}
                  />
                  Full feature access
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-blue-400" : "text-blue-600"}`}
                  />
                  No hardware required
                </li>
              </ul>
              {!user && (
                <Button asChild className="w-full">
                  <Link href="/auth/signup">Try Demo Mode</Link>
                </Button>
              )}
            </CardContent>
          </Card>

          <Card
            className={`border-green-200 ${theme.features.animations ? "enhanced-hover" : ""}`}
            style={{
              background: themeMode.includes("dark")
                ? "linear-gradient(135deg, hsl(142 76% 15%) 0%, hsl(142 76% 20%) 100%)"
                : "linear-gradient(135deg, hsl(142 100% 97%) 0%, hsl(142 100% 95%) 100%)",
            }}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Droplets className={`w-6 h-6 ${themeMode.includes("dark") ? "text-green-400" : "text-green-600"}`} />
                Live System
              </CardTitle>
              <CardDescription>Production-ready agricultural control</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-green-400" : "text-green-600"}`}
                  />
                  Real MQTT sensor integration
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-green-400" : "text-green-600"}`}
                  />
                  PostgreSQL data persistence
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-green-400" : "text-green-600"}`}
                  />
                  Actual irrigation control
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle
                    className={`w-4 h-4 ${themeMode.includes("dark") ? "text-green-400" : "text-green-600"}`}
                  />
                  Weather API integration
                </li>
              </ul>
              {!user && (
                <Button asChild variant="outline" className="w-full bg-transparent">
                  <Link href="/auth/signin">Access Live System</Link>
                </Button>
              )}
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card
          className={`${theme.features.gradients ? "animated-gradient" : "bg-gradient-to-r from-primary to-primary/80"} text-primary-foreground border-0 ${theme.features.shadows ? "enhanced-shadow" : ""}`}
        >
          <CardContent className="p-12 text-center">
            <h2 className="text-3xl lg:text-4xl font-bold mb-4">
              {user ? `Welcome back, ${user.firstName}!` : "Ready to Get Started?"}
            </h2>
            <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
              {user
                ? `Your account is in ${user.demoMode ? "demo" : "live"} mode. Access your dashboard to manage your agricultural operations.`
                : "Join agricultural professionals using ControlCore for intelligent irrigation management. Start with demo mode or connect your live system."}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <>
                  <Button
                    size="lg"
                    variant="secondary"
                    asChild
                    className={theme.features.animations ? "enhanced-hover" : ""}
                  >
                    <Link href="/dashboard">Go to Dashboard</Link>
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className={`border-white text-white hover:bg-white hover:text-primary bg-transparent ${theme.features.animations ? "enhanced-hover" : ""}`}
                    asChild
                  >
                    <Link href="/stations">Monitor Stations</Link>
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    size="lg"
                    variant="secondary"
                    asChild
                    className={theme.features.animations ? "enhanced-hover" : ""}
                  >
                    <Link href="/auth/signup">Start Free Trial</Link>
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className={`border-white text-white hover:bg-white hover:text-primary bg-transparent ${theme.features.animations ? "enhanced-hover" : ""}`}
                    asChild
                  >
                    <Link href="/auth/signin">Sign In</Link>
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
