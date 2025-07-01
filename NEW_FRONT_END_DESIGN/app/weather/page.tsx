"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from "recharts"
import { format } from "date-fns"

interface HistoricalRow {
  dt: number | string
  temp: number
  precipitation_total?: number
}

interface ForecastRow {
  [key: string]: any
}

export default function WeatherPage() {
  const [historical, setHistorical] = useState<HistoricalRow[]>([])
  const [forecast, setForecast] = useState<ForecastRow | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const histRes = await fetch("/api/weather/historical")
        const histData = await histRes.json()
        if (histData.success) {
          setHistorical(histData.data)
        }
        const foreRes = await fetch("/api/weather/forecast")
        const foreData = await foreRes.json()
        if (foreData.success && foreData.data.length) {
          setForecast(foreData.data[0])
        }
      } catch (err) {
        console.error("Failed to load weather", err)
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [])

  const tempData = historical
    .map((d) => ({
      time: format(new Date(typeof d.dt === "string" ? d.dt : d.dt * 1000), "HH:mm"),
      temp: d.temp,
    }))
    .reverse()

  const precData = historical
    .map((d) => ({
      time: format(new Date(typeof d.dt === "string" ? d.dt : d.dt * 1000), "HH:mm"),
      precipitation: d.precipitation_total || 0,
    }))
    .reverse()

  return (
    <div className="min-h-screen enhanced-bg">
      <Navigation />
      <div className="container mx-auto px-4 py-8 space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Historical Temperature</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={tempData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis dataKey="temp" unit="°C" />
                    <Tooltip />
                    <Line type="monotone" dataKey="temp" stroke="#8884d8" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Precipitation</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={precData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis dataKey="precipitation" unit="mm" />
                    <Tooltip />
                    <Bar dataKey="precipitation" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Forecast (Next 24h)</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : forecast ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Time</TableHead>
                    <TableHead>Temp</TableHead>
                    <TableHead>Precip %</TableHead>
                    <TableHead>Conditions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Array.from({ length: 24 }).map((_, i) => {
                    const ts = forecast[`hour_${i}_timestamptz`]
                    const temp = forecast[`hour_${i}_temp`]
                    const pop = forecast[`hour_${i}_pop`]
                    const desc = forecast[`hour_${i}_weather_description`]
                    if (temp === undefined) return null
                    return (
                      <TableRow key={i}>
                        <TableCell>{ts ? format(new Date(ts), "PPpp") : ""}</TableCell>
                        <TableCell>{temp != null ? `${temp}°C` : "-"}</TableCell>
                        <TableCell>{pop != null ? `${Math.round(pop * 100)}%` : "-"}</TableCell>
                        <TableCell>{desc}</TableCell>
                      </TableRow>
                    )
                  })}
                </TableBody>
              </Table>
            ) : (
              <div>No forecast data.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

