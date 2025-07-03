"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { TestTube, Zap, Info, CheckCircle, AlertTriangle } from "lucide-react"

interface DemoModeToggleProps {
  isDemoMode: boolean
  onToggle: (enabled: boolean) => void
  className?: string
}

export function DemoModeToggle({ isDemoMode, onToggle, className }: DemoModeToggleProps) {
  const [isToggling, setIsToggling] = useState(false)

  const handleToggle = async (enabled: boolean) => {
    setIsToggling(true)

    try {
      const res = await fetch("/api/user/demo-mode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ demo_mode: enabled }),
      })

      const data = await res.json()
      if (data.success) {
        onToggle(enabled)
      } else {
        console.error("Failed to update demo mode:", data.error)
      }
    } catch (err) {
      console.error("Error updating demo mode:", err)
    } finally {
      setIsToggling(false)
    }
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {isDemoMode ? <TestTube className="w-5 h-5 text-blue-500" /> : <Zap className="w-5 h-5 text-green-500" />}
          System Mode
        </CardTitle>
        <CardDescription>Switch between demo simulation and live system data</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-medium">{isDemoMode ? "Demo Mode" : "Live System"}</span>
              <Badge variant={isDemoMode ? "secondary" : "default"}>{isDemoMode ? "Simulated" : "Real-time"}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">
              {isDemoMode
                ? "Using simulated agricultural data for demonstration"
                : "Connected to live MQTT sensors and database"}
            </p>
          </div>
          <Switch checked={!isDemoMode} onCheckedChange={(checked) => handleToggle(!checked)} disabled={isToggling} />
        </div>

        {isDemoMode ? (
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              Demo mode shows realistic but simulated data. Perfect for testing features and training.
            </AlertDescription>
          </Alert>
        ) : (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              Live mode connected to your actual sensors, MQTT broker, and PostgreSQL database.
            </AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <h4 className="font-medium">Demo Mode Features</h4>
            <ul className="space-y-1 text-muted-foreground">
              <li>• Simulated sensor data</li>
              <li>• Safe testing environment</li>
              <li>• No real system impact</li>
              <li>• Training & demonstration</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">Live System Features</h4>
            <ul className="space-y-1 text-muted-foreground">
              <li>• Real MQTT sensor feeds</li>
              <li>• PostgreSQL data storage</li>
              <li>• Actual valve control</li>
              <li>• Production monitoring</li>
            </ul>
          </div>
        </div>

        {!isDemoMode && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Caution:</strong> Live mode controls real irrigation systems. Ensure proper safety measures are in
              place.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
