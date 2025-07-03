"use client";

import { useEffect, useState } from "react";
import { Navigation } from "@/components/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { format } from "date-fns";

interface DailyRow {
  date: string;
  temperature_min: number;
  temperature_max: number;
  precipitation_total: number;
  wind_max_speed: number;
  humidity_afternoon: number;
}

interface ForecastRow {
  [key: string]: any;
}

interface OverviewRow {
  date: string;
  weather_overview: string;
  day: number;
}

export default function WeatherPage() {
  const [daily, setDaily] = useState<DailyRow[]>([]);
  const [forecast, setForecast] = useState<ForecastRow | null>(null);
  const [baseline, setBaseline] = useState<{
    value: number;
    unit: string | null;
  } | null>(null);
  const [overview, setOverview] = useState<OverviewRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const dailyRes = await fetch("/api/weather/daily-summary");
        const dailyData = await dailyRes.json();
        if (dailyData.success) {
          setDaily(dailyData.data);
        }
        const foreRes = await fetch("/api/weather/forecast");
        const foreData = await foreRes.json();
        if (foreData.success && foreData.data.length) {
          setForecast(foreData.data[0]);
        }
        const baseRes = await fetch("/api/weather/baseline");
        const baseData = await baseRes.json();
        if (baseData.success && baseData.data) {
          setBaseline(baseData.data);
        }
        const overRes = await fetch("/api/weather/overview");
        const overData = await overRes.json();
        if (overData.success) {
          setOverview(overData.data);
        }
      } catch (err) {
        console.error("Failed to load weather", err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const precipChart = daily
    .slice(0, 7)
    .map((d) => ({
      // convert epoch seconds to milliseconds for accurate Date objects
      date: format(new Date(d.date * 1000), "MMM d"),
      precipitation: d.precipitation_total || 0,
    }))
    .reverse();

  const statsFor = (days: number) => {
    const subset = daily.slice(0, days);
    if (!subset.length) return null;
    const count = subset.length;
    const sum = (key: keyof DailyRow) =>
      subset.reduce((acc, cur) => acc + (cur[key] || 0), 0);
    return {
      avgMax: sum("temperature_max") / count,
      avgMin: sum("temperature_min") / count,
      totalRain: sum("precipitation_total"),
      avgWind: sum("wind_max_speed") / count,
      avgRh: sum("humidity_afternoon") / count,
    };
  };

  const stats5 = statsFor(5);
  const stats15 = statsFor(15);

  const yesterday = daily[1];
  const today = daily[0];

  return (
    <div className="min-h-screen enhanced-bg">
      <Navigation />
      <div className="container mx-auto px-4 py-8 space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Now &amp; Recent Past</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="space-y-1">
                  <div className="font-semibold">Yesterday</div>
                  {yesterday ? (
                    <>
                      <div>High: {yesterday.temperature_max}°C</div>
                      <div>Low: {yesterday.temperature_min}°C</div>
                      <div>Rain: {yesterday.precipitation_total} mm</div>
                    </>
                  ) : (
                    <div>N/A</div>
                  )}
                </div>
                <div className="space-y-1">
                  <div className="font-semibold">Today</div>
                  {today ? (
                    <>
                      <div>High: {today.temperature_max}°C</div>
                      <div>Low: {today.temperature_min}°C</div>
                      <div>Rain: {today.precipitation_total} mm</div>
                    </>
                  ) : (
                    <div>N/A</div>
                  )}
                </div>
                <div className="space-y-1">
                  <div className="font-semibold">Right Now</div>
                  {baseline || forecast ? (
                    <>
                      <div>
                        Temp:{" "}
                        {baseline
                          ? `${baseline.value}${baseline.unit || ""}`
                          : `${forecast?.current_temp ?? "N/A"}°C`}
                      </div>
                      <div>
                        Wind: {forecast ? forecast.current_wind_speed : "N/A"}{" "}
                        m/s
                      </div>
                      <div>
                        RH: {forecast ? forecast.current_humidity : "N/A"}%
                      </div>
                    </>
                  ) : (
                    <div>N/A</div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Precipitation (Last 7 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={precipChart}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
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
            <CardTitle>Forecast Summary</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div>Loading...</div>
            ) : forecast ? (
              <div className="grid grid-cols-2 gap-4 text-sm">
                {Array.from({ length: 2 }).map((_, i) => {
                  const ts = forecast[`day_${i}_timestamptz`];
                  const high = forecast[`day_${i}_temp_max`];
                  const low = forecast[`day_${i}_temp_min`];
                  const pop = forecast[`day_${i}_pop`];
                  const desc = forecast[`day_${i}_weather_description`];
                  return (
                    <div key={i} className="space-y-1">
                      <div className="font-semibold">
                        {ts ? format(new Date(ts), "EEE") : `Day ${i}`}
                      </div>
                      <div>High: {high}°C</div>
                      <div>Low: {low}°C</div>
                      <div>
                        Rain: {pop != null ? Math.round(pop * 100) : 0}%
                      </div>
                      <div>{desc}</div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div>No forecast data.</div>
            )}
          </CardContent>
        </Card>

        {overview.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>AI Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {overview[0] && (
                <p className="text-sm whitespace-pre-line">
                  {overview[0].weather_overview}
                </p>
              )}
              {overview[1] && (
                <p className="text-sm whitespace-pre-line">
                  {overview[1].weather_overview}
                </p>
              )}
            </CardContent>
          </Card>
        )}

        {stats5 && stats15 && (
          <Card>
            <CardHeader>
              <CardTitle>Comparison Stats</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    <TableHead>Last 5 Days</TableHead>
                    <TableHead>Last 15 Days</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>Max Temp Avg</TableCell>
                    <TableCell>{stats5.avgMax.toFixed(1)}°C</TableCell>
                    <TableCell>{stats15.avgMax.toFixed(1)}°C</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Min Temp Avg</TableCell>
                    <TableCell>{stats5.avgMin.toFixed(1)}°C</TableCell>
                    <TableCell>{stats15.avgMin.toFixed(1)}°C</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Total Rain</TableCell>
                    <TableCell>{stats5.totalRain.toFixed(1)} mm</TableCell>
                    <TableCell>{stats15.totalRain.toFixed(1)} mm</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Wind Avg</TableCell>
                    <TableCell>{stats5.avgWind.toFixed(1)} m/s</TableCell>
                    <TableCell>{stats15.avgWind.toFixed(1)} m/s</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>RH Avg</TableCell>
                    <TableCell>{stats5.avgRh.toFixed(1)}%</TableCell>
                    <TableCell>{stats15.avgRh.toFixed(1)}%</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
