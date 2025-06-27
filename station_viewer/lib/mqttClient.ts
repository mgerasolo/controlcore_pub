// lib/mqttClient.ts
import mqtt from "mqtt"
import type { SensorReading } from "@/types/station"
import { parseSensorId } from "@/lib/sensorGrouping"

class MQTTClient {
  private client: mqtt.MqttClient | null = null
  private subscribers: ((reading: SensorReading) => void)[] = []
  private isConnected = false

  constructor() {
    if (typeof window !== "undefined") {
      this.initializeClient()
    }
  }

  private initializeClient() {
    this.client = mqtt.connect("ws://192.168.100.60:9001", {
      reconnectPeriod: 1000,
    })

    this.client.on("connect", () => {
      console.log("[MQTT] Connected to broker")
      this.isConnected = true

      this.client?.subscribe("controlcore/data/#", (err) => {
        if (err) {
          console.error("[MQTT] Subscribe failed:", err)
        } else {
          console.log("[MQTT] Subscribed to controlcore/data/#")
        }
      })
    })

    this.client.on("message", (topic, payload) => {
      if (!topic.startsWith("controlcore/data/")) {
        return
      }
      try {
        const raw = JSON.parse(payload.toString())
        const parsed = parseSensorId(raw.source_id || raw.sensor_id || "")
        const data = {
          ...raw,
          ...parsed,
          timestamp: new Date(Number(raw.timestamp) * 1000),
        }
        this.subscribers.forEach((cb) => cb(data))
      } catch (err) {
        console.error("Invalid MQTT payload:", err)
      }
    })
  }

  public subscribe(cb: (reading: SensorReading) => void): () => void {
    this.subscribers.push(cb)
    return () => {
      this.subscribers = this.subscribers.filter((fn) => fn !== cb)
    }
  }

  public publish(topic: string, message: string) {
    this.client?.publish(topic, message)
  }

  public getConnectionStatus(): boolean {
    return this.isConnected
  }
}

export const mqttClient = new MQTTClient()
