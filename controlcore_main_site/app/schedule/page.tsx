"use client"

import { useEffect, useState } from "react"
import { Navigation } from "@/components/navigation"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { format } from "date-fns"

type ScheduleItem = {
  id: number
  zone_id: string
  station: string
  controller_id: string
  start_time: string
  duration_seconds: number
  status: string
}

export default function SchedulePage() {
  const [items, setItems] = useState<ScheduleItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const res = await fetch("/api/schedule", { credentials: "include" })
        const data = await res.json()
        if (data.success) setItems(data.schedule)
      } catch (err) {
        console.error("Failed to load schedule:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchSchedule()
  }, [])

  return (
    <div className="min-h-screen enhanced-bg">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <Card>
          <CardHeader>
            <CardTitle>Watering Schedule</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : items.length === 0 ? (
              <div>No upcoming tasks.</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Start Time</TableHead>
                    <TableHead>Zone</TableHead>
                    <TableHead>Station</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{format(new Date(item.start_time), "PPpp")}</TableCell>
                      <TableCell>{item.zone_id}</TableCell>
                      <TableCell>{item.station}</TableCell>
                      <TableCell>{Math.round(item.duration_seconds / 60)} min</TableCell>
                      <TableCell>{item.status}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
