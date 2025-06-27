"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import type { SensorReading } from "@/types/station"
import type { ControlMessage } from "@/types/control"
import { mqttClient } from "@/lib/mqttClient"
import {
  groupSensorsPhysically,
  groupSensorsLogically,
  isDataFresh,
  getSensorTypeIcon,
  getSensorTypeLabel,
} from "@/lib/sensorGrouping"
import { Activity, Wifi, WifiOff, Clock } from "lucide-react"

export default function StationViewer() {
  const [sensors, setSensors] = useState<SensorReading[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [valveDurations, setValveDurations] = useState<Record<string, number>>({})

  useEffect(() => {
    const unsubscribe = mqttClient.subscribe((reading: SensorReading) => {
      setSensors((prev) => {
        // Remove old reading for the same sensor_id and add new one
        const filtered = prev.filter((s) => s.sensor_id !== reading.sensor_id)
        return [...filtered, reading].sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      })
    })

    // Check connection status periodically
    const connectionCheck = setInterval(() => {
      setIsConnected(mqttClient.getConnectionStatus())
    }, 1000)

    return () => {
      unsubscribe()
      clearInterval(connectionCheck)
    }
  }, [])

  const physicalGroups = groupSensorsPhysically(sensors)
  const logicalGroups = groupSensorsLogically(sensors)


  const handleValveCommand = (
    sensor: SensorReading,
    action: "open" | "close"
  ) => {
    const duration = valveDurations[sensor.sensor_id] ?? 300
    const payload: ControlMessage = {
      station: sensor.station,
      controller: sensor.controller,
      sensor_id: sensor.sensor_id,
      sensor_type: sensor.sensor_type,
      unit: action === "open" ? "seconds" : "state",
      value: action === "open" ? duration : 0,
      command: action,
      source: "manual_override",
      requestor_id: "web_app",
      timestamp: Math.floor(Date.now() / 1000),
    }
    mqttClient.publish(
      `controlcore/command/${sensor.sensor_id}`,
      JSON.stringify(payload)
    )
  }

  const SensorCard = ({ sensor }: { sensor: SensorReading }) => {
    const isFresh = isDataFresh(sensor.timestamp)
    const icon = getSensorTypeIcon(sensor.sensor_type)

    return (
      <Card
        className={`transition-all duration-300 ${isFresh ? "border-green-200 bg-green-50" : "border-gray-200 bg-gray-50 opacity-75"}`}
      >
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <span className="text-lg">{icon}</span>
              {sensor.enumeratorOrName || sensor.sensor_id}
            </CardTitle>
            <Badge variant={isFresh ? "default" : "secondary"} className="text-xs">
              {getSensorTypeLabel(sensor.sensor_type)}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="pt-0">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-2xl font-bold">{sensor.value}</span>
              <span className="text-sm text-muted-foreground">{sensor.unit}</span>
            </div>
            <div className="text-xs text-muted-foreground space-y-1">
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {sensor.timestamp.toLocaleTimeString()}
              </div>
              <div>Station: {sensor.station}</div>
              <div>Controller: {sensor.controller.split("_").pop()}</div>
              {sensor.pin !== -1 && <div>Pin: {sensor.pin}</div>}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">ControlCore Station Viewer</h1>
          <p className="text-muted-foreground">Real-time sensor monitoring and control</p>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <Badge variant="default" className="flex items-center gap-1">
              <Wifi className="w-3 h-3" />
              Connected
            </Badge>
          ) : (
            <Badge variant="destructive" className="flex items-center gap-1">
              <WifiOff className="w-3 h-3" />
              Disconnected
            </Badge>
          )}
          <Badge variant="outline" className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            {sensors.length} sensors
          </Badge>
        </div>
      </div>

      <Tabs defaultValue="physical" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="physical">Physical View</TabsTrigger>
          <TabsTrigger value="logical">Logical View</TabsTrigger>
          <TabsTrigger value="manual">Manual Overrides</TabsTrigger>
        </TabsList>

        <TabsContent value="physical" className="space-y-6">
          <div className="space-y-6">
            {Object.entries(physicalGroups).map(([station, controllers]) => (
              <Card key={station}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">🏭 Station: {station}</CardTitle>
                  <CardDescription>{Object.keys(controllers).length} controller(s)</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(controllers).map(([controller, sensorList]) => (
                    <div key={controller} className="space-y-3">
                      <h4 className="font-medium text-sm text-muted-foreground flex items-center gap-2">
                        🎛️ Controller: {controller.split("_").pop()}
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {sensorList.map((sensor) => (
                          <SensorCard key={sensor.sensor_id} sensor={sensor} />
                        ))}
                      </div>
                    </div>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
          {Object.keys(physicalGroups).length === 0 && (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="text-4xl">📡</div>
                  <p className="text-muted-foreground">No sensor data received yet</p>
                  <p className="text-sm text-muted-foreground">Waiting for MQTT messages on controlcore/#</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="logical" className="space-y-6">
          <div className="space-y-6">
            {Object.entries(logicalGroups).map(([sensorType, sensorList]) => (
              <Card key={sensorType}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <span className="text-xl">{getSensorTypeIcon(sensorType)}</span>
                    {getSensorTypeLabel(sensorType)}
                  </CardTitle>
                  <CardDescription>{sensorList.length} sensor(s) of this type</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {sensorList.map((sensor) => (
                      <SensorCard key={sensor.sensor_id} sensor={sensor} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
          {Object.keys(logicalGroups).length === 0 && (
            <Card>
              <CardContent className="flex items-center justify-center py-12">
                <div className="text-center space-y-2">
                  <div className="text-4xl">🔍</div>
                  <p className="text-muted-foreground">No sensor types detected yet</p>
                  <p className="text-sm text-muted-foreground">Sensors will be grouped by type as data arrives</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="manual" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Manual Controls</CardTitle>
              <CardDescription>
                Tap a button below to open or close a valve. Adjust how long to keep it open.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {sensors
                .filter((s) => s.sensor_type === "valve-state")
                .map((sensor) => (
                  <div key={sensor.sensor_id} className="space-y-2 border rounded-md p-4">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">
                        {sensor.enumeratorOrName || sensor.sensor_id}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {isDataFresh(sensor.timestamp) ? "" : "(stale)"}
                      </span>
                    </div>
                    <Slider
                      defaultValue={[5]}
                      min={1}
                      max={15}
                      step={1}
                      onValueChange={(v) =>
                        setValveDurations({
                          ...valveDurations,
                          [sensor.sensor_id]: v[0] * 60,
                        })
                      }
                    />
                    <div className="text-xs text-muted-foreground">
                      Duration: {(valveDurations[sensor.sensor_id] ?? 300) / 60} min
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleValveCommand(sensor, "open")}
                        disabled={!isConnected}
                      >
                        Open
                      </Button>
                      <Button
                        variant="secondary"
                        onClick={() => handleValveCommand(sensor, "close")}
                        disabled={!isConnected}
                      >
                        Close
                      </Button>
                    </div>
                  </div>
                ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
