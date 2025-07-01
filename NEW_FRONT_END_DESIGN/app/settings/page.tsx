"use client"

import { useState, useEffect } from "react"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Settings, Palette, TestTube } from "lucide-react"
import { ThemeSelector } from "@/components/theme-selector"
import { DemoModeToggle } from "@/components/demo-mode-toggle"
import { useControlCoreTheme } from "@/components/theme-provider"
import { getTheme } from "@/lib/themes"

export default function SettingsPage() {
  const [user, setUser] = useState(null)
  const { themeMode } = useControlCoreTheme()
  const theme = getTheme(themeMode)


  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("/api/auth/session", {
          credentials: "include",
        })
        const data = await res.json()
        setUser(data)
      } catch (error) {
        console.error("Failed to fetch user session:", error)
      }
    }

    fetchUser()
  }, [])

  const handleDemoModeToggle = (enabled) => {
    setDemoMode(enabled)
    // In real implementation, update user preference in database
    console.log("Demo mode toggled:", enabled)
  }

  return (
    <div className="min-h-screen enhanced-bg">
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Settings</h1>
          <p className="text-xl text-muted-foreground">Customize your ControlCore experience and system preferences</p>
        </div>

        <Tabs defaultValue="appearance" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="appearance" className="flex items-center gap-2">
              <Palette className="w-4 h-4" />
              <span className="hidden sm:inline">Appearance</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center gap-2">
              <TestTube className="w-4 h-4" />
              <span className="hidden sm:inline">System</span>
            </TabsTrigger>
            <TabsTrigger value="account" className="flex items-center gap-2">
              {/* User icon component */}
              <span className="hidden sm:inline">Account</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="flex items-center gap-2">
              {/* Shield icon component */}
              <span className="hidden sm:inline">Security</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="appearance" className="space-y-6">
            <ThemeSelector />

            <Card className={theme.features.glassEffect ? "glass-card" : ""}>
              <CardHeader>
                <CardTitle>Theme Features</CardTitle>
                <CardDescription>Current theme capabilities and optimizations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-2xl mb-2 ${theme.features.gradients ? "text-green-600" : "text-gray-400"}`}>
                      {theme.features.gradients ? "✓" : "✗"}
                    </div>
                    <div className="text-sm font-medium">Gradients</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-2xl mb-2 ${theme.features.animations ? "text-green-600" : "text-gray-400"}`}>
                      {theme.features.animations ? "✓" : "✗"}
                    </div>
                    <div className="text-sm font-medium">Animations</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-2xl mb-2 ${theme.features.shadows ? "text-green-600" : "text-gray-400"}`}>
                      {theme.features.shadows ? "✓" : "✗"}
                    </div>
                    <div className="text-sm font-medium">Shadows</div>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <div className={`text-2xl mb-2 ${theme.features.glassEffect ? "text-green-600" : "text-gray-400"}`}>
                      {theme.features.glassEffect ? "✓" : "✗"}
                    </div>
                    <div className="text-sm font-medium">Glass Effect</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-6">
            {user && <DemoModeToggle isDemoMode={demoMode} onToggle={handleDemoModeToggle} />}

            <Card className={theme.features.glassEffect ? "glass-card" : ""}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="w-5 h-5" />
                  System Information
                </CardTitle>
                <CardDescription>Current system status and configuration</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Connection Status</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>MQTT Broker</span>
                        <span className="text-green-600">Connected</span>
                      </div>
                      <div className="flex justify-between">
                        <span>PostgreSQL</span>
                        <span className="text-green-600">Online</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Weather API</span>
                        <span className="text-green-600">Active</span>
                      </div>
                      <div className="flex justify-between">
                        <span>AI Modules</span>
                        <span className="text-green-600">Running</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-medium">System Metrics</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Active Stations</span>
                        <span>2/3</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Sensors Online</span>
                        <span>8/12</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Data Points Today</span>
                        <span>2,847</span>
                      </div>
                      <div className="flex justify-between">
                        <span>System Uptime</span>
                        <span>99.8%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="account" className="space-y-6">
            <Card className={theme.features.glassEffect ? "glass-card" : ""}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {/* User icon component */}
                  Account Information
                </CardTitle>
                <CardDescription>Your ControlCore account details</CardDescription>
              </CardHeader>
              <CardContent>
                {user ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">First Name</label>
                        <div className="mt-1 p-2 border rounded-md bg-muted">{user.firstName}</div>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Last Name</label>
                        <div className="mt-1 p-2 border rounded-md bg-muted">{user.lastName}</div>
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Email</label>
                      <div className="mt-1 p-2 border rounded-md bg-muted">{user.email}</div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Role</label>
                      <div className="mt-1 p-2 border rounded-md bg-muted capitalize">{user.role}</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    Please sign in to view account information
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="security" className="space-y-6">
            <Card className={theme.features.glassEffect ? "glass-card" : ""}>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {/* Shield icon component */}
                  Security Settings
                </CardTitle>
                <CardDescription>Manage your account security and access</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Password Security</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Last Password Change</span>
                        <span className="text-muted-foreground">30 days ago</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Password Strength</span>
                        <span className="text-green-600">Strong</span>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h4 className="font-medium">Session Management</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Active Sessions</span>
                        <span>1</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Last Login</span>
                        <span className="text-muted-foreground">Today, 2:30 PM</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
