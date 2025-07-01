import { cookies } from "next/headers";
import { jwtVerify } from "jose";
import pool from "../db";  // Adjust path if needed

const JWT_SECRET = process.env.JWT_SECRET!;
const encoder = new TextEncoder();

export async function getCurrentUser() {
  const token = cookies().get("auth-token")?.value;
  if (!token) return null;

  try {
    const { payload } = await jwtVerify(token, encoder.encode(JWT_SECRET));
    const { userId } = payload;

    const { rows } = await pool.query(
      "SELECT id, email, first_name, last_name, role, demo_mode FROM users WHERE id = $1",
      [userId]
    );
    return rows[0] ?? null;
  } catch {
    return null;
  }
}
