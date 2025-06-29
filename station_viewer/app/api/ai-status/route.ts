import { NextResponse } from 'next/server';
import { Client } from 'pg';

export async function GET() {
  const client = new Client({
    host: process.env.PG_HOST,
    port: Number(process.env.PG_PORT || 5432),
    user: process.env.CONTROLCORE_USER,
    password: process.env.CONTROLCORE_PW,
    database: 'controlcore',
  });

  try {
    await client.connect();
    const res = await client.query(
      'SELECT module_name, last_run_time, status, details FROM module_status ORDER BY module_name'
    );
    await client.end();
    return NextResponse.json(res.rows);
  } catch (err) {
    console.error('Failed to fetch ai status', err);
    return NextResponse.json({ error: 'failed' }, { status: 500 });
  }
}
