import { generateText } from 'ai'

export async function POST(request: Request) {
  const { prompt } = await request.json()
  if (typeof prompt !== 'string' || !prompt.trim()) return Response.json({ error: 'A prompt is required.' }, { status: 400 })
  const { text } = await generateText({ model: 'openai/o4-mini', system: 'You are Signal, a concise strategic thinking partner. Give practical, specific next steps. Keep responses under 120 words.', prompt })
  return Response.json({ text })
}
