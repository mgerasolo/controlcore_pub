"use client"

import { useState, useEffect } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Zap,
  Power,
  AlertCircle,
  CheckCircle,
  Clock,
  Activity,
  Wifi,
  Database,
  Send,
  Play,
  Pause,
  Settings,
  MessageSquare,
  BarChart3,
  RefreshCw,
} from "lucide-react"

interface SensorData {
  sensor_id: string
  sensor_type: string
  value: number
  unit: string
  pin: number
  timestamp: number
  source_id: string
}

interface StationData {
  station: string
  controller_id: string
  status: "online" | "offline" | "maintenance"
  sensors: SensorData[]
  lastUpdate: Date
}

interface MQTTMessage {
  id: string
  topic: string
  payload: string
  timestamp: Date
  qos: number
  retained: boolean
}

interface QuickButton {
  id: string
  name: string
  topic: string
  payload: string
  description: string
}

export default function StationsPage() {
  const [stations, setStations] = useState<StationData[]>([])
  const [selectedStation, setSelectedStation] = useState<string>("")
  const [mqttMessages, setMqttMessages] = useState<MQTTMessage[]>([])
  const [isSubscribed, setIsSubscribed] = useState(false)
  const [subscriptionTopic, setSubscriptionTopic] = useState("controlcore/data/#")
  const [publishTopic, setPublishTopic] = useState("controlcore/command/")
  const [publishPayload, setPublishPayload] = useState("")
  const [quickButtons, setQuickButtons] = useState<QuickButton[]>([
    {
      id: "1",
      name: "Emergency Stop",
      topic: "controlcore/command/emergency",
      payload: '{"action": "stop_all", "source": "web_app"}',
      description: "Stop all irrigation immediately",
    },
    {
      id: "2",
      name: "Status Check",
      topic: "controlcore/command/status",
      payload: '{"action": "get_status", "source": "web_app"}',
      description: "Request status from all controllers",
    },
    {
      id: "3",
      name: "Config Reload",
      topic: "controlcore/config/reload",
      payload: '{"action": "reload_config", "source": "web_app"}',
      description: "Reload configuration on all stations",
    },
    {
      id: "4",
      name: "Test Mode",
      topic: "controlcore/command/test",
      payload: '{"action": "test_mode", "duration": 30, "source": "web_app"}',
      description: "Enable test mode for 30 seconds",
    },
  ])
  const [realtimeData, setRealtimeData] = useState<{ [key: string]: number[] }>({})

  useEffect(() => {
    // Mock data based on your MQTT structure
    const mockStations: StationData[] = [
      {
        station: "garden-hydrant",
        controller_id: "uno-r4-wifi-primary",
        status: "online",
        sensors: [
          {
            sensor_id: "BeetsTomatoes-USSolid",
            sensor_type: "valve-state",
            value: 0,
            unit: "state",
            pin: -1,
            timestamp: Date.now() - 3000,
            source_id: "excessus-home_garden-hydrant_uno-r4-wifi-primary_valve-state_BeetsTomatoes-USSolid",
          },
          {
            sensor_id: "BeetsTomatoes-Foush",
            sensor_type: "water-pressure",
            value: 106,
            unit: "PSI",
            pin: 14,
            timestamp: Date.now() - 3000,
            source_id: "excessus-home_garden-hydrant_uno-r4-wifi-primary_water-pressure_BeetsTomatoes-Foush",
          },
          {
            sensor_id: "BeetsTomatoes-Grieda",
            sensor_type: "water-flow",
            value: 765,
            unit: "L/min",
            timestamp: Date.now() - 3000,
            pin: 2,
            source_id: "excessus-home_garden-hydrant_uno-r4-wifi-primary_water-flow_BeetsTomatoes-Grieda",
          },
        ],
        lastUpdate: new Date(Date.now() - 3000),
      },
      {
        station: "greenhouse-zone",
        controller_id: "esp32-greenhouse",
        status: "maintenance",
        sensors: [
          {
            sensor_id: "TomatoZone-TempSensor",
            sensor_type: "temperature",
            value: 24.5,
            unit: "°C",
            pin: 4,
            timestamp: Date.now() - 15000,
            source_id: "excessus-home_greenhouse-zone_esp32-greenhouse_temperature_TomatoZone-TempSensor",
          },
          {
            sensor_id: "TomatoZone-HumiditySensor",
            sensor_type: "humidity",
            value: 72,
            unit: "%",
            pin: 5,
            timestamp: Date.now() - 15000,
            source_id: "excessus-home_greenhouse-zone_esp32-greenhouse_humidity_TomatoZone-HumiditySensor",
          },
        ],
        lastUpdate: new Date(Date.now() - 15000),
      },
      {
        station: "north-field",
        controller_id: "arduino-field-01",
        status: "offline",
        sensors: [],
        lastUpdate: new Date(Date.now() - 900000),
      },
    ]

    setStations(mockStations)
    if (mockStations.length > 0) {
      setSelectedStation(mockStations[0].station)
    }

    // Simulate real-time MQTT messages every 3 seconds
    const interval = setInterval(() => {
      if (isSubscribed) {
        const mockMessage: MQTTMessage = {
          id: Date.now().toString(),
          topic: `controlcore/data/garden-hydrant/uno-r4-wifi-primary/water-pressure/BeetsTomatoes-Foush`,
          payload: JSON.stringify({
            sensor_id: "BeetsTomatoes-Foush",
            sensor_type: "water-pressure",
            value: 105 + Math.random() * 10,
            unit: "PSI",
            pin: 14,
            timestamp: Date.now(),
            source_id: "excessus-home_garden-hydrant_uno-r4-wifi-primary_water-pressure_BeetsTomatoes-Foush",
          }),
          timestamp: new Date(),
          qos: 0,
          retained: false,
        }

        setMqttMessages((prev) => [mockMessage, ...prev.slice(0, 49)]) // Keep last 50 messages

        // Update realtime data for charts
        setRealtimeData((prev) => {
          const key = "water-pressure"
          const newData = [...(prev[key] || []), 105 + Math.random() * 10]
          return {
            ...prev,
            [key]: newData.slice(-20), // Keep last 20 points (1 minute at 3-second intervals)
          }
        })
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [isSubscribed])

  const handleSubscribe = () => {
    setIsSubscribed(!isSubscribed)
    if (!isSubscribed) {
      setMqttMessages([
        {
          id: Date.now().toString(),
          topic: "system/status",
          payload: `Subscribed to ${subscriptionTopic}`,
          timestamp: new Date(),
          qos: 0,
          retained: false,
        },
      ])
    }
  }

  const handlePublish = () => {
    if (!publishTopic || !publishPayload) return

    const message: MQTTMessage = {
      id: Date.now().toString(),
      topic: publishTopic,
      payload: publishPayload,
      timestamp: new Date(),
      qos: 0,
      retained: false,
    }

    setMqttMessages((prev) => [message, ...prev])
    console.log("Published:", message)
  }

  const handleQuickButton = (button: QuickButton) => {
    const message: MQTTMessage = {
      id: Date.now().toString(),
      topic: button.topic,
      payload: button.payload,
      timestamp: new Date(),
      qos: 0,
      retained: false,
    }

    setMqttMessages((prev) => [message, ...prev])
    console.log("Quick action:", button.name, message)
  }

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

  const getSensorIcon = (sensorType: string) => {
    switch (sensorType) {
      case "valve-state":
        return "🚰"
      case "water-pressure":
        return "📊"
      case "water-flow":
        return "💧"
      case "temperature":
        return "🌡️"
      case "humidity":
        return "💨"
      default:
        return "📡"
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <div className="container mx-auto px-4 py-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">Station Monitor & MQTT Control</h1>
          <p className="text-muted-foreground">Real-time monitoring, MQTT integration, and system control</p>
        </div>

        <Tabs defaultValue="stations" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="stations">Stations</TabsTrigger>
            <TabsTrigger value="mqtt">MQTT Live</TabsTrigger>
            <TabsTrigger value="realtime">Real-time Data</TabsTrigger>
            <TabsTrigger value="config">Configuration</TabsTrigger>
          </TabsList>

          <TabsContent value="stations" className="space-y-6">
            <Tabs value={selectedStation} onValueChange={setSelectedStation} className="space-y-6">
              <TabsList className="grid w-full grid-cols-3">
                {stations.map((station) => {
                  const StatusIcon = getStatusIcon(station.status)
                  return (
                    <TabsTrigger key={station.station} value={station.station} className="flex items-center gap-2">
                      <div className={`h-2 w-2 rounded-full ${getStatusColor(station.status)}`}></div>
                      <span className="hidden sm:inline">{station.station}</span>
                      <span className="sm:hidden">{station.station.split("-")[0]}</span>
                    </TabsTrigger>
                  )
                })}
              </TabsList>

              {stations.map((station) => (
                <TabsContent key={station.station} value={station.station} className="space-y-6">
                  {/* Station Overview */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Activity className="w-5 h-5" />
                          Station Status
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Controller</span>
                            <Badge variant="outline">{station.controller_id}</Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Status</span>
                            <Badge variant={station.status === "online" ? "default" : "secondary"}>
                              {station.status}
                            </Badge>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Sensors</span>
                            <span className="text-sm">{station.sensors.length} active</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium">Last Update</span>
                            <span className="text-sm text-muted-foreground">
                              {station.lastUpdate.toLocaleTimeString()}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Wifi className="w-5 h-5" />
                          MQTT Topics
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          <div className="p-2 bg-muted rounded font-mono text-xs">
                            controlcore/data/{station.station}/#
                          </div>
                          <div className="p-2 bg-muted rounded font-mono text-xs">
                            controlcore/command/{station.station}
                          </div>
                          <div className="p-2 bg-muted rounded font-mono text-xs">
                            controlcore/config/{station.station}
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Power className="w-5 h-5" />
                          Quick Controls
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {station.sensors
                            .filter((s) => s.sensor_type === "valve-state")
                            .map((valve) => (
                              <div key={valve.sensor_id} className="space-y-2">
                                <div className="flex items-center justify-between">
                                  <span className="text-sm font-medium">{valve.sensor_id}</span>
                                  <Badge variant={valve.value > 0 ? "default" : "secondary"}>
                                    {valve.value > 0 ? "Open" : "Closed"}
                                  </Badge>
                                </div>
                                <div className="flex gap-2">
                                  <Button size="sm" variant="outline" disabled={station.status !== "online"}>
                                    Open 5min
                                  </Button>
                                  <Button size="sm" variant="outline" disabled={station.status !== "online"}>
                                    Close
                                  </Button>
                                </div>
                              </div>
                            ))}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Sensor Data */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Database className="w-5 h-5" />
                        Live Sensor Data
                      </CardTitle>
                      <CardDescription>Real-time data from {station.station} (3-second intervals)</CardDescription>
                    </CardHeader>
                    <CardContent>
                      {station.sensors.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {station.sensors.map((sensor) => {
                            const isStale = Date.now() - sensor.timestamp > 15000 // 15 seconds
                            const age = Math.floor((Date.now() - sensor.timestamp) / 1000)
                            return (
                              <Card
                                key={sensor.sensor_id}
                                className={isStale ? "border-yellow-200 bg-yellow-50" : "border-green-200 bg-green-50"}
                              >
                                <CardContent className="p-4">
                                  <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                      <span className="text-lg">{getSensorIcon(sensor.sensor_type)}</span>
                                      <span className="font-medium text-sm">{sensor.sensor_id}</span>
                                    </div>
                                    <Badge variant={isStale ? "secondary" : "default"} className="text-xs">
                                      {age}s ago
                                    </Badge>
                                  </div>
                                  <div className="space-y-2">
                                    <div className="text-2xl font-bold">
                                      {sensor.value} {sensor.unit}
                                    </div>
                                    <div className="text-xs text-muted-foreground">Type: {sensor.sensor_type}</div>
                                    <div className="text-xs text-muted-foreground">
                                      Pin: {sensor.pin >= 0 ? sensor.pin : "N/A"}
                                    </div>
                                    <div className="text-xs font-mono bg-muted p-1 rounded text-[10px]">
                                      {sensor.source_id}
                                    </div>
                                  </div>
                                </CardContent>
                              </Card>
                            )
                          })}
                        </div>
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                          <p>No sensor data available</p>
                          <p className="text-sm">Station may be offline or in maintenance mode</p>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}
            </Tabs>
          </TabsContent>

          <TabsContent value="mqtt" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-6">
                {/* MQTT Message Viewer */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <MessageSquare className="w-5 h-5" />
                      Live MQTT Messages
                      <Badge variant={isSubscribed ? "default" : "secondary"}>
                        {isSubscribed ? "Subscribed" : "Disconnected"}
                      </Badge>
                    </CardTitle>
                    <CardDescription>Real-time MQTT message stream (3-second intervals)</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex gap-2">
                        <Input
                          placeholder="controlcore/data/#"
                          value={subscriptionTopic}
                          onChange={(e) => setSubscriptionTopic(e.target.value)}
                          className="font-mono text-sm"
                        />
                        <Button onClick={handleSubscribe} variant={isSubscribed ? "destructive" : "default"}>
                          {isSubscribed ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                          {isSubscribed ? "Unsubscribe" : "Subscribe"}
                        </Button>
                      </div>

                      <ScrollArea className="h-96 border rounded-lg p-4">
                        <div className="space-y-2">
                          {mqttMessages.map((message) => (
                            <div
                              key={message.id}
                              className="border-l-2 border-blue-500 pl-3 py-2 bg-muted/50 rounded-r"
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="font-mono text-sm font-medium">{message.topic}</span>
                                <span className="text-xs text-muted-foreground">
                                  {message.timestamp.toLocaleTimeString()}
                                </span>
                              </div>
                              <pre className="text-xs bg-background p-2 rounded overflow-x-auto">
                                {JSON.stringify(JSON.parse(message.payload || "{}"), null, 2)}
                              </pre>
                            </div>
                          ))}
                          {mqttMessages.length === 0 && (
                            <div className="text-center py-8 text-muted-foreground">
                              <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
                              <p>No messages yet</p>
                              <p className="text-sm">Subscribe to a topic to see live data</p>
                            </div>
                          )}
                        </div>
                      </ScrollArea>
                    </div>
                  </CardContent>
                </Card>

                {/* MQTT Publisher */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Send className="w-5 h-5" />
                      MQTT Publisher
                    </CardTitle>
                    <CardDescription>Send commands and configuration updates</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <Label htmlFor="publish-topic">Topic</Label>
                        <Input
                          id="publish-topic"
                          placeholder="controlcore/command/garden-hydrant"
                          value={publishTopic}
                          onChange={(e) => setPublishTopic(e.target.value)}
                          className="font-mono"
                        />
                      </div>
                      <div>
                        <Label htmlFor="publish-payload">Payload (JSON)</Label>
                        <Textarea
                          id="publish-payload"
                          placeholder='{"action": "open_valve", "sensor_id": "BeetsTomatoes-USSolid", "duration": 300}'
                          value={publishPayload}
                          onChange={(e) => setPublishPayload(e.target.value)}
                          className="font-mono text-sm"
                          rows={4}
                        />
                      </div>
                      <Button onClick={handlePublish} className="w-full">
                        <Send className="w-4 h-4 mr-2" />
                        Publish Message
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                {/* Quick Action Buttons */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5" />
                      Quick Actions
                    </CardTitle>
                    <CardDescription>Pre-configured MQTT commands</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {quickButtons.map((button) => (
                        <div key={button.id} className="space-y-2">
                          <Button
                            variant="outline"
                            className="w-full justify-start bg-transparent"
                            onClick={() => handleQuickButton(button)}
                          >
                            <Power className="w-4 h-4 mr-2" />
                            {button.name}
                          </Button>
                          <p className="text-xs text-muted-foreground px-2">{button.description}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Connection Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="w-5 h-5" />
                      Connection Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm">MQTT Broker</span>
                        <Badge variant="default" className="bg-green-500">
                          Connected
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Database</span>
                        <Badge variant="default" className="bg-blue-500">
                          Online
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Update Rate</span>
                        <span className="text-sm">3 seconds</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm">Messages/min</span>
                        <span className="text-sm">~20</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="realtime" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Real-time Data Visualization
                </CardTitle>
                <CardDescription>
                  Live charts updating every 3 seconds, aggregated to 30-second intervals for trends
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h4 className="font-medium">Water Pressure (Last 60 seconds)</h4>
                    <div className="h-48 border rounded-lg flex items-center justify-center bg-muted/50">
                      <div className="text-center">
                        <BarChart3 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm text-muted-foreground">
                          Chart shows {realtimeData["water-pressure"]?.length || 0} data points
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Latest: {realtimeData["water-pressure"]?.slice(-1)[0]?.toFixed(1) || "N/A"} PSI
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h4 className="font-medium">Data Rate Monitor</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>MQTT Messages</span>
                        <span>{mqttMessages.length} received</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Update Frequency</span>
                        <span>Every 3 seconds</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Chart Aggregation</span>
                        <span>30-second intervals</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Data Retention</span>
                        <span>Last 20 points (1 minute)</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="config" className="space-y-6">
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="w-5 h-5" />
                    Quick Button Configuration
                  </CardTitle>
                  <CardDescription>Customize your MQTT quick action buttons</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {quickButtons.map((button, index) => (
                      <div key={button.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">Button {index + 1}</span>
                          <Button variant="ghost" size="sm">
                            <Settings className="w-4 h-4" />
                          </Button>
                        </div>
                        <div className="space-y-2">
                          <Input placeholder="Button Name" value={button.name} readOnly />
                          <Input placeholder="MQTT Topic" value={button.topic} readOnly className="font-mono text-sm" />
                          <Textarea
                            placeholder="JSON Payload"
                            value={button.payload}
                            readOnly
                            className="font-mono text-xs"
                            rows={2}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="w-5 h-5" />
                    Database Query Defaults
                  </CardTitle>
                  <CardDescription>Configure default queries for sensor data</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="default-query">Default Sensor Query</Label>
                      <Textarea
                        id="default-query"
                        value="SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 20;"
                        readOnly
                        className="font-mono text-sm"
                        rows={3}
                      />
                    </div>
                    <div>
                      <Label htmlFor="realtime-query">Real-time Data Query</Label>
                      <Textarea
                        id="realtime-query"
                        value="SELECT sensor_type, value, timestamp FROM sensor_data WHERE timestamp > NOW() - INTERVAL '1 minute' ORDER BY timestamp DESC;"
                        readOnly
                        className="font-mono text-sm"
                        rows={3}
                      />
                    </div>
                    <Button variant="outline" className="w-full bg-transparent">
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Test Query
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
