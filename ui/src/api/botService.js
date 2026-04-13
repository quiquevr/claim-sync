const BASE_URL = 'http://localhost:5000'
const ACCOUNT_ID = 'acc_001'

export async function getStatus(botType) {
  const res = await fetch(`${BASE_URL}/bot/${botType}/account/${ACCOUNT_ID}/status`)
  if (!res.ok) throw new Error(`getStatus failed: ${res.status}`)
  return res.json()
}

export async function scheduleBOT(botType) {
  const res = await fetch(`${BASE_URL}/bot/${botType}/account/${ACCOUNT_ID}/schedule`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      schedule: { interval_minutes: 1, retry_attempts: 1, timeout_seconds: 30 },
      max_concurrent_jobs: 1,
      priority: 'high',
    }),
  })
  if (!res.ok) throw new Error(`schedule failed: ${res.status}`)
  return res.json()
}

export async function killBot(botType) {
  const res = await fetch(`${BASE_URL}/bot/${botType}/account/${ACCOUNT_ID}/kill`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error(`kill failed: ${res.status}`)
  return res.json()
}
