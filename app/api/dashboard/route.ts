import { generateInitialData } from '@/lib/dashboard'

export async function GET() {
  try {
    const data = generateInitialData()
    return Response.json(data)
  } catch {
    return new Response('Failed to generate dashboard data', { status: 500 })
  }
}
