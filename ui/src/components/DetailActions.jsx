import { useState } from 'react'
import { scheduleBOT, killBot } from '../api/botService'

function formatTimestamp(ts) {
  if (!ts) return '—'
  const date = new Date(ts * 1000)
  const mm = String(date.getMonth() + 1).padStart(2, '0')
  const dd = String(date.getDate()).padStart(2, '0')
  const yyyy = date.getFullYear()
  return `${mm}-${dd}-${yyyy}`
}

export default function DetailActions({ selectedJob, status, onActionComplete }) {
  const [loading, setLoading] = useState(false)

  const isScheduled = status?.status === 'SCHEDULED'
  const isKilled    = !status || status?.status === 'KILLED'

  const startDisabled = !selectedJob || loading || isScheduled
  const stopDisabled  = !selectedJob || loading || isKilled

  async function handleStart() {
    setLoading(true)
    try {
      await scheduleBOT(selectedJob)
      onActionComplete?.()
    } catch (err) {
      console.error('Start failed:', err)
    } finally {
      setLoading(false)
    }
  }

  async function handleStop() {
    setLoading(true)
    try {
      await killBot(selectedJob)
      onActionComplete?.()
    } catch (err) {
      console.error('Stop failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const startedAt = status?.['next-exec-date']
    ? formatTimestamp(status['next-exec-date'])
    : '—'

  return (
    <div className="detail-actions">
      <span className="detail-start-time">
        Start time: <strong>{startedAt}</strong>
      </span>
      <div className="detail-buttons">
        <button
          className="btn btn-start"
          onClick={handleStart}
          disabled={startDisabled}
        >
          Start
        </button>
        <button
          className="btn btn-stop"
          onClick={handleStop}
          disabled={stopDisabled}
        >
          Stop
        </button>
      </div>
    </div>
  )
}
