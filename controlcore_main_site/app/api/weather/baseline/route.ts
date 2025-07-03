import { NextResponse } from "next/server";
import { fetchBaselineSensor } from "@/lib/weather";

export async function GET() {
  const sourceId = process.env.BASELINE_SENSOR_ID;
  if (!sourceId) {
    return NextResponse.json(
      { success: false, error: "Baseline sensor not configured" },
      { status: 500 },
    );
  }
  try {
    const data = await fetchBaselineSensor(sourceId);
    return NextResponse.json({ success: true, data });
  } catch (err) {
    console.error("baseline api error", err);
    return NextResponse.json(
      { success: false, error: "Internal server error" },
      { status: 500 },
    );
  }
}
