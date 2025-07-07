"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Brain, Send, Zap, TrendingUp, Droplets, AlertTriangle, CheckCircle, Cloud, Activity } from "lucide-react"

interface ChatMessage {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

interface AIInsight {
  id: string
  type: "optimization" | "alert" | "recommendation" | "weather"
  title: string
  description: string
  impact: "high" | "medium" | "low"
  source: "advisor" | "forecast_regression" | "weather_api" | "sensor_analysis"
  timestamp: Date
}

export default function AIPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your ControlCore AI assistant. I integrate data from your MQTT sensors, weather forecasts, and historical patterns to provide intelligent irrigation recommendations. How can I help optimize your agricultural operations today?",
      timestamp: new Date(),
    },
  ])
  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const [insights, setInsights] = useState<AIInsight[]>([
    {
      id: "1",
      type: "optimization",
      title: "Water Usage Optimization",
      description:
        "Reduce water consumption by 15% by adjusting irrigation schedule based on weather forecast and soil moisture readings",
      impact: "high",
      source: "advisor",
      timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
    },
    {
      id: "2",
      type: "weather",
      title: "Rain Forecast Alert",
      description: "Heavy rain expected tomorrow morning. Consider delaying scheduled watering for garden-hydrant zone",
      impact: "medium",
      source: "weather_api",
      timestamp: new Date(Date.now() - 3600000), // 1 hour ago
    },
    {
      id: "3",
      type: "alert",
      title: "Sensor Anomaly Detected",
      description:
        "BeetsTomatoes-Foush pressure sensor showing irregular readings. May require calibration or maintenance",
      impact: "medium",
      source: "sensor_analysis",
      timestamp: new Date(Date.now() - 7200000), // 2 hours ago
    },
    {
      id: "4",
      type: "recommendation",
      title: "Energy Efficiency Improvement",
      description: "Switch irrigation to off-peak hours (5-7 AM) to reduce energy costs by approximately $127/month",
      impact: "medium",
      source: "forecast_regression",
      timestamp: new Date(Date.now() - 10800000), // 3 hours ago
    },
  ])

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const text = inputMessage

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      })

      if (!res.ok) {
        throw new Error(`Request failed with status ${res.status}`)
      }

      const data = await res.json()
      const responseText =
        data.answer || data.response || data.message || JSON.stringify(data)

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: responseText,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, aiMessage])
    } catch (err) {
      console.error("AI chat error", err)
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, there was an error processing your request.",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case "optimization":
        return TrendingUp
      case "alert":
        return AlertTriangle
      case "recommendation":
        return CheckCircle
      case "weather":
        return Cloud
      default:
        return Brain
    }
  }

  const getInsightColor = (type: string) => {
    switch (type) {
      case "optimization":
        return "bg-green-100 text-green-600"
      case "alert":
        return "bg-red-100 text-red-600"
      case "recommendation":
        return "bg-blue-100 text-blue-600"
      case "weather":
        return "bg-orange-100 text-orange-600"
      default:
        return "bg-gray-100 text-gray-600"
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            ControlCore AI Assistant
          </h1>
          <p className="text-xl text-gray-600">
            Intelligent agricultural management powered by real-time data, weather integration, and machine learning
          </p>
        </div>

        <Tabs defaultValue="chat" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="chat" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              AI Chat
            </TabsTrigger>
            <TabsTrigger value="insights" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Insights
            </TabsTrigger>
            <TabsTrigger value="modules" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              AI Modules
            </TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="space-y-6">
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <Card className="h-[600px] flex flex-col">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5" />
                      AI Chat Assistant
                    </CardTitle>
                    <CardDescription>
                      Ask questions about irrigation, weather, scheduling, or system optimization
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    <ScrollArea className="flex-1 pr-4">
                      <div className="space-y-4">
                        {messages.map((message) => (
                          <div
                            key={message.id}
                            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
                          >
                            <div
                              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                                message.role === "user"
                                  ? "bg-gradient-to-r from-purple-500 to-blue-500 text-white"
                                  : "bg-gray-100 text-gray-900"
                              }`}
                            >
                              <div className="text-sm whitespace-pre-line">{message.content}</div>
                              <div
                                className={`text-xs mt-1 ${message.role === "user" ? "text-purple-100" : "text-gray-500"}`}
                              >
                                {message.timestamp.toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        ))}
                        {isLoading && (
                          <div className="flex justify-start">
                            <div className="bg-gray-100 rounded-lg px-4 py-2">
                              <div className="flex items-center space-x-2">
                                <div className="animate-pulse">AI is analyzing your data...</div>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </ScrollArea>
                    <div className="flex gap-2 mt-4">
                      <Input
                        value={inputMessage}
                        onChange={(e) => setInputMessage(e.target.value)}
                        placeholder="Ask about irrigation, weather, sensors, or optimization..."
                        onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                        disabled={isLoading}
                      />
                      <Button onClick={handleSendMessage} disabled={isLoading || !inputMessage.trim()}>
                        <Send className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Quick Actions</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent"
                      onClick={() => setInputMessage("Optimize my watering schedule")}
                    >
                      <Droplets className="w-4 h-4 mr-2" />
                      Optimize Watering
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent"
                      onClick={() => setInputMessage("Check weather forecast impact")}
                    >
                      <Cloud className="w-4 h-4 mr-2" />
                      Weather Analysis
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent"
                      onClick={() => setInputMessage("Review sensor health")}
                    >
                      <Activity className="w-4 h-4 mr-2" />
                      Sensor Health
                    </Button>
                    <Button
                      variant="outline"
                      className="w-full justify-start bg-transparent"
                      onClick={() => setInputMessage("Show energy efficiency tips")}
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      Energy Tips
                    </Button>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">System Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm">AI Advisor</span>
                      <Badge variant="default" className="bg-green-500">
                        Active
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Weather Integration</span>
                      <Badge variant="default" className="bg-blue-500">
                        Synced
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Forecast Regression</span>
                      <Badge variant="default" className="bg-purple-500">
                        Running
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm">Data Processing</span>
                      <Badge variant="default" className="bg-orange-500">
                        Real-time
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="insights" className="space-y-6">
            <div className="grid gap-4">
              {insights.map((insight) => {
                const Icon = getInsightIcon(insight.type)
                return (
                  <Card key={insight.id}>
                    <CardContent className="p-6">
                      <div className="flex items-start gap-4">
                        <div className={`p-2 rounded-lg ${getInsightColor(insight.type)}`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h3 className="font-semibold">{insight.title}</h3>
                            <div className="flex items-center gap-2">
                              <Badge variant={insight.impact === "high" ? "destructive" : "secondary"}>
                                {insight.impact} impact
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {insight.source}
                              </Badge>
                            </div>
                          </div>
                          <p className="text-gray-600 mb-2">{insight.description}</p>
                          <p className="text-xs text-gray-500">Generated {insight.timestamp.toLocaleString()}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })}
            </div>
          </TabsContent>

          <TabsContent value="modules" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Brain className="w-5 h-5" />
                    AI Advisor Module
                  </CardTitle>
                  <CardDescription>Core decision engine for irrigation optimization</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <Badge variant="default" className="bg-green-500">
                      Active
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Interval</span>
                    <span className="text-sm">30 minutes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Last Run</span>
                    <span className="text-sm">15 minutes ago</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Decisions Made</span>
                    <span className="text-sm">247 today</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Forecast Regression
                  </CardTitle>
                  <CardDescription>Predictive modeling for optimal scheduling</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <Badge variant="default" className="bg-blue-500">
                      Running
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Interval</span>
                    <span className="text-sm">60 minutes</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Model Accuracy</span>
                    <span className="text-sm">94.2%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Predictions</span>
                    <span className="text-sm">48-hour forecast</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cloud className="w-5 h-5" />
                    Weather Integration
                  </CardTitle>
                  <CardDescription>OpenWeather API data processing</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <Badge variant="default" className="bg-orange-500">
                      Synced
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Update Frequency</span>
                    <span className="text-sm">Every hour</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Last Update</span>
                    <span className="text-sm">23 minutes ago</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Forecast Range</span>
                    <span className="text-sm">5 days</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Master Controller
                  </CardTitle>
                  <CardDescription>Coordinates all AI modules and execution</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Status</span>
                    <Badge variant="default" className="bg-purple-500">
                      Running
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Execution Mode</span>
                    <span className="text-sm">Continuous</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Tasks Processed</span>
                    <span className="text-sm">1,247 today</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Uptime</span>
                    <span className="text-sm">99.8%</span>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Integration Architecture</CardTitle>
                <CardDescription>How AI modules connect with your ControlCore system</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Data Sources</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• MQTT sensor feeds</li>
                      <li>• PostgreSQL historical data</li>
                      <li>• OpenWeather API</li>
                      <li>• System health metrics</li>
                    </ul>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Processing</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Real-time analysis</li>
                      <li>• Pattern recognition</li>
                      <li>• Predictive modeling</li>
                      <li>• Anomaly detection</li>
                    </ul>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-medium mb-2">Outputs</h4>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• Watering schedules</li>
                      <li>• MQTT commands</li>
                      <li>• System alerts</li>
                      <li>• Optimization recommendations</li>
                    </ul>
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
