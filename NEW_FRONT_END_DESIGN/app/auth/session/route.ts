import { NextResponse } from "next/server";
import { getCurrentUser } from "@/lib/server/auth-server";

export async function GET(request: Request) {
  console.log("headers:", request.headers.get("cookie"));

  const user = await getCurrentUser();
  return NextResponse.json(user);
}
