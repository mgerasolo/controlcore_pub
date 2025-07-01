import { NextRequest, NextResponse } from 'next/server'
import mqtt from 'mqtt'

const HOST = process.env.MQTT_HOST || 'localhost'
const PORT = Number(process.env.MQTT_PORT || '1883')

export async function POST(req: NextRequest) {
  try {
    const { topic, payload } = await req.json()
    if (!topic || payload === undefined) {
      return NextResponse.json(
        { success: false, error: 'Topic and payload required' },
        { status: 400 }
      )
    }

    return await new Promise<NextResponse>((resolve) => {
      const client = mqtt.connect(`mqtt://${HOST}:${PORT}`)
      client.on('connect', () => {
        const message = typeof payload === 'string' ? payload : JSON.stringify(payload)
        client.publish(topic, message, {}, (err) => {
          client.end()
          if (err) {
            console.error('MQTT publish error', err)
            resolve(NextResponse.json({ success: false, error: 'Publish failed' }, { status: 500 }))
          } else {
            resolve(NextResponse.json({ success: true }))
          }
        })
      })
      client.on('error', (err) => {
        console.error('MQTT connection error', err)
        client.end()
        resolve(NextResponse.json({ success: false, error: 'Connection failed' }, { status: 500 }))
      })
    })
  } catch (err) {
    console.error('publish api error', err)
    return NextResponse.json({ success: false, error: 'Invalid request' }, { status: 400 })
  }
}
