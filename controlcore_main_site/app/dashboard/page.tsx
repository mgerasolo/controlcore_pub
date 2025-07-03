"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Droplets,
  Thermometer,
  Zap,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Activity,
  Cloud,
  Calendar,
  Database,
  Brain,
  Settings,
} from "lucide-react"
import Link from "next/link"

interface SystemMetrics {
  totalWaterUsage: number
  avgSoilTemp: number
  powerConsumption: number
  activeStations: number
  totalStations: number
  scheduledTasks: number
  completedTasks: number
  weatherAlerts: number
}

interface StationStatus {
  station: string
  status: "Active" | "Standby" | "Maintenance" | "Offline"
  moisture: number
  lastWatering: Date
  nextScheduled: Date | null
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    totalWaterUsage: 2847,
    avgSoilTemp: 24.2,
    powerConsumption: 12.4,
    activeStations: 2,
    totalStations: 3,
    scheduledTasks: 5,
    completedTasks: 12,
    weatherAlerts: 1,
  })

  const [stationStatus, setStationStatus] = useState<StationStatus[]>([
    {
      station: "garden-hydrant",
      status: "Active",
      moisture: 68,
      lastWatering: new Date(Date.now() - 3600000), // 1 hour ago
      nextScheduled: new Date(Date.now() + 7200000), // 2 hours from now
    },
    {
      station: "greenhouse-zone",
      status: "Maintenance",
      moisture: 82,
      lastWatering: new Date(Date.now() - 86400000), // 1 day ago
      nextScheduled: null,
    },
    {
      station: "north-field",
      status: "Offline",
      moisture: 45,
      lastWatering: new Date(Date.now() - 172800000), // 2 days ago
      nextScheduled: null,
    },
  ])

  const alerts = [
    {
      type: "warning",
      message: "greenhouse-zone controller requires maintenance check",
      time: "2 hours ago",
      source: "controller_health",
    },
    {
      type: "info",
      message: "AI advisor optimized watering schedule for garden-hydrant",
      time: "4 hours ago",
      source: "controlcore_ai",
    },
    {
      type: "success",
      message: "Water usage reduced by 15% this week",
      time: "1 day ago",
      source: "analytics",
    },
    {
      type: "info",
      message: "Weather forecast updated - rain expected tomorrow",
      time: "6 hours ago",
      source: "openweather",
    },
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Active":
        return "bg-green-500"
      case "Standby":
        return "bg-blue-500"
      case "Maintenance":
        return "bg-yellow-500"
      case "Offline":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">System Dashboard</h1>
          <p className="text-muted-foreground">Comprehensive overview of your ControlCore agricultural system</p>
        </div>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="stations">Stations</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="system">System</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Water Usage</CardTitle>
                  <Droplets className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.totalWaterUsage}L</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      -12% from yesterday
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Soil Temperature</CardTitle>
                  <Thermometer className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.avgSoilTemp}°C</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-green-600 flex items-center">
                      <CheckCircle className="h-3 w-3 mr-1" />
                      Optimal range
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Power Consumption</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metrics.powerConsumption}kW</div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-red-600 flex items-center">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      +5% from yesterday
                    </span>
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Stations</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {metrics.activeStations}/{metrics.totalStations}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    <span className="text-yellow-600 flex items-center">
                      <AlertTriangle className="h-3 w-3 mr-1" />1 in maintenance
                    </span>
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Station Status & Recent Alerts */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Station Status</CardTitle>
                  <CardDescription>Current status of all irrigation stations</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {stationStatus.map((station, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className={`h-3 w-3 rounded-full ${getStatusColor(station.status)}`}></div>
                        <div>
                          <div className="font-medium text-sm">{station.station}</div>
                          <div className="text-xs text-muted-foreground">{station.status}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-medium">{station.moisture}%</div>
                        <div className="text-xs text-muted-foreground">Moisture</div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Alerts</CardTitle>
                  <CardDescription>Latest system notifications and events</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {alerts.map((alert, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 border rounded-lg">
                      <div
                        className={`h-2 w-2 rounded-full mt-2 ${
                          alert.type === "warning"
                            ? "bg-yellow-500"
                            : alert.type === "info"
                              ? "bg-blue-500"
                              : "bg-green-500"
                        }`}
                      ></div>
                      <div className="flex-1">
                        <div className="text-sm">{alert.message}</div>
                        <div className="text-xs text-muted-foreground">
                          {alert.source} • {alert.time}
                        </div>
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="stations" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {stationStatus.map((station, index) => (
                <Card key={index}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {station.station}
                      <Badge variant={station.status === "Active" ? "default" : "secondary"}>{station.status}</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Soil Moisture</span>
                        <span className="font-medium">{station.moisture}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${station.moisture}%` }}></div>
                      </div>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Last Watering</span>
                        <span>{station.lastWatering.toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Next Scheduled</span>
                        <span>
                          {station.nextScheduled ? station.nextScheduled.toLocaleTimeString() : "Not scheduled"}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Calendar className="w-5 h-5" />
                    Scheduled Tasks
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{metrics.scheduledTasks}</div>
                  <p className="text-sm text-muted-foreground">Pending watering tasks</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Completed Today
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{metrics.completedTasks}</div>
                  <p className="text-sm text-muted-foreground">Successfully executed</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Cloud className="w-5 h-5" />
                    Weather Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{metrics.weatherAlerts}</div>
                  <p className="text-sm text-muted-foreground">Active weather warnings</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Efficiency
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">92%</div>
                  <p className="text-sm text-muted-foreground">Water usage efficiency</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Analytics Integration</CardTitle>
                <CardDescription>Ready for historical data analysis and forecasting</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Historical Data</h4>
                    <p className="text-sm text-muted-foreground">
                      sensor_data table contains timestamped readings for trend analysis
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Weather Integration</h4>
                    <p className="text-sm text-muted-foreground">
                      OpenWeather API provides forecast data for predictive scheduling
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">AI Insights</h4>
                    <p className="text-sm text-muted-foreground">
                      controlcore_ai module provides optimization recommendations
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="system" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Database Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>PostgreSQL Connection</span>
                    <Badge variant="default" className="bg-green-500">
                      Connected
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Tables</span>
                    <span className="text-sm">14 tables active</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Recent Records</span>
                    <span className="text-sm">sensor_data, control_log</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    MQTT Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Broker Connection</span>
                    <Badge variant="default" className="bg-green-500">
                      Connected
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Data Topic</span>
                    <span className="text-sm">controlcore/data/#</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Command Topic</span>
                    <span className="text-sm">controlcore/command/#</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Module Status</CardTitle>
                <CardDescription>Status of all ControlCore suite components</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">station_viewer</h4>
                      <Badge variant="default" className="bg-green-500">
                        Active
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Web interface for monitoring and control</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">controlcore_ai</h4>
                      <Badge variant="default" className="bg-blue-500">
                        Running
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">AI advisor and decision engine</p>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium">openweather</h4>
                      <Badge variant="default" className="bg-orange-500">
                        Synced
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">Weather data collection service</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common system management tasks</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button asChild variant="outline" className="h-20 flex-col bg-transparent">
                <Link href="/stations">
                  <Activity className="w-6 h-6 mb-2" />
                  Monitor Stations
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-20 flex-col bg-transparent">
                <Link href="/ai">
                  <Brain className="w-6 h-6 mb-2" />
                  AI Assistant
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-20 flex-col bg-transparent">
                <Link href="/schedule">
                  <Calendar className="w-6 h-6 mb-2" />
                  View Schedule
                </Link>
              </Button>
              <Button asChild variant="outline" className="h-20 flex-col bg-transparent">
                <Link href="/settings">
                  <Settings className="w-6 h-6 mb-2" />
                  System Settings
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
