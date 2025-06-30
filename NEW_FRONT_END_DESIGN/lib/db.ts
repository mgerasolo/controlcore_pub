import { Pool } from 'pg'

const pool = new Pool({
  host: process.env.PG_HOST || 'localhost',
  port: parseInt(process.env.PG_PORT || '5432', 10),
  user: process.env.CONTROLCORE_USER || process.env.PG_USER,
  password: process.env.CONTROLCORE_PW || process.env.PG_PASSWORD,
  database: process.env.PG_DATABASE || 'controlcore',
})

export default pool
