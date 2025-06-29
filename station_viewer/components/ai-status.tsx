"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface ModuleStatus {
  module_name: string;
  last_run_time: string;
  status: string;
  details: any;
}

export default function AiStatus() {
  const [data, setData] = useState<ModuleStatus[]>([]);

  useEffect(() => {
    fetch("/api/ai-status")
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch((err) => console.error("Failed to fetch AI status", err));
  }, []);

  if (data.length === 0) {
    return <p className="p-4 text-muted-foreground">No AI status data.</p>;
  }

  return (
    <div className="p-4 grid gap-4">
      {data.map((m) => (
        <Card key={m.module_name}>
          <CardHeader>
            <CardTitle className="capitalize">{m.module_name.replace("_", " ")}</CardTitle>
            <CardDescription>Last run: {new Date(m.last_run_time).toLocaleString()}</CardDescription>
          </CardHeader>
          <CardContent>
            <pre className="text-sm whitespace-pre-wrap">{JSON.stringify(m.details, null, 2)}</pre>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
