"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Progress } from "@/components/ui/progress"
import { Droplets, Thermometer, Zap, Gauge, Power, AlertCircle, CheckCircle, Clock } from "lucide-react"

interface StationData {
  id: string
  name: string
  status: "online" | "offline" | "maintenance"
  soilMoisture: number
  temperature: number
  humidity: number
  waterFlow: number
  powerUsage: number
  isIrrigating: boolean
  lastUpdate: Date
}

export default function StationPage() {
  const [stations] = useState<StationData[]>([
    {
      id: "1",
      name: "Zone A - North Field",
      status: "online",
      soilMoisture: 68,
      temperature: 24.5,
      humidity: 72,
      waterFlow: 15.2,
      powerUsage: 2.4,
      isIrrigating: true,
      lastUpdate: new Date(),
    },
    {
      id: "2",
      name: "Zone B - South Field",
      status: "online",
      soilMoisture: 45,
      temperature: 26.1,
      humidity: 65,
      waterFlow: 0,
      powerUsage: 0.8,
      isIrrigating: false,
      lastUpdate: new Date(),
    },
    {
      id: "3",
      name: "Zone C - Greenhouse",
      status: "maintenance",
      soilMoisture: 82,
      temperature: 28.3,
      humidity: 85,
      waterFlow: 0,
      powerUsage: 0,
      isIrrigating: false,
      lastUpdate: new Date(Date.now() - 300000),
    },
  ])

  const getStatusColor = (status: string) => {
    switch (status) {
      case "online":
        return "bg-green-500"
      case "offline":
        return "bg-red-500"
      case "maintenance":
        return "bg-yellow-500"
      default:
        return "bg-gray-500"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return CheckCircle
      case "offline":
        return AlertCircle
      case "maintenance":
        return Clock
      default:
        return AlertCircle
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Station Monitor</h1>
          <p className="text-muted-foreground">Real-time status of all irrigation stations</p>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {stations.map((station) => {
            const StatusIcon = getStatusIcon(station.status)

            return (
              <Card key={station.id} className="relative">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{station.name}</CardTitle>
                    <div className="flex items-center space-x-2">
                      <div className={`h-2 w-2 rounded-full ${getStatusColor(station.status)}`}></div>
                      <StatusIcon className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                  <Badge variant={station.status === "online" ? "default" : "secondary"} className="w-fit">
                    {station.status.charAt(0).toUpperCase() + station.status.slice(1)}
                  </Badge>
                </CardHeader>

                <CardContent className="space-y-4">
                  {/* Soil Moisture */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <div className="flex items-center space-x-2">
                        <Droplets className="h-4 w-4 text-blue-500" />
                        <span>Soil Moisture</span>
                      </div>
                      <span className="font-medium">{station.soilMoisture}%</span>
                    </div>
                    <Progress value={station.soilMoisture} className="h-2" />
                  </div>

                  {/* Temperature */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm">
                      <Thermometer className="h-4 w-4 text-orange-500" />
                      <span>Temperature</span>
                    </div>
                    <span className="font-medium">{station.temperature}°C</span>
                  </div>

                  {/* Humidity */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm">
                      <Gauge className="h-4 w-4 text-green-500" />
                      <span>Humidity</span>
                    </div>
                    <span className="font-medium">{station.humidity}%</span>
                  </div>

                  {/* Water Flow */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm">
                      <Droplets className="h-4 w-4 text-cyan-500" />
                      <span>Water Flow</span>
                    </div>
                    <span className="font-medium">{station.waterFlow} L/min</span>
                  </div>

                  {/* Power Usage */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 text-sm">
                      <Zap className="h-4 w-4 text-yellow-500" />
                      <span>Power</span>
                    </div>
                    <span className="font-medium">{station.powerUsage} kW</span>
                  </div>

                  {/* Irrigation Control */}
                  <div className="flex items-center justify-between pt-2 border-t">
                    <div className="flex items-center space-x-2">
                      <Power className="h-4 w-4" />
                      <span className="text-sm font-medium">Irrigation</span>
                    </div>
                    <Switch checked={station.isIrrigating} disabled={station.status !== "online"} />
                  </div>

                  {/* Last Update */}
                  <div className="text-xs text-muted-foreground pt-2">
                    {station.lastUpdate
                      ? new Date(station.lastUpdate).toLocaleTimeString()
                      : 'N/A'}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <Button variant="outline" size="sm" className="h-auto py-3 flex-col space-y-1 bg-transparent">
                  <Droplets className="h-4 w-4" />
                  <span className="text-xs">Start All</span>
                </Button>
                <Button variant="outline" size="sm" className="h-auto py-3 flex-col space-y-1 bg-transparent">
                  <Power className="h-4 w-4" />
                  <span className="text-xs">Stop All</span>
                </Button>
                <Button variant="outline" size="sm" className="h-auto py-3 flex-col space-y-1 bg-transparent">
                  <Gauge className="h-4 w-4" />
                  <span className="text-xs">Auto Mode</span>
                </Button>
                <Button variant="outline" size="sm" className="h-auto py-3 flex-col space-y-1 bg-transparent">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-xs">Alerts</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
