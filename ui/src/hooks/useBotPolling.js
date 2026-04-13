import { useState, useEffect, useRef } from 'react'
import { getStatus } from '../api/botService'

const POLL_INTERVAL_MS = 3000
const MAX_FEED_ENTRIES = 50

export function useBotPolling(selectedJob) {
  const [status, setStatus] = useState(null)
  const [feed, setFeed] = useState([])
  const [error, setError] = useState(null)
  const intervalRef = useRef(null)

  // Clear feed whenever the selected job changes
  useEffect(() => {
    setFeed([])
    setStatus(null)
    setError(null)
  }, [selectedJob])

  useEffect(() => {
    if (!selectedJob) return

    const poll = async () => {
      try {
        const data = await getStatus(selectedJob)
        setStatus(data)
        setError(null)

        const timestamp = new Date().toLocaleTimeString()
        const line = `[${timestamp}] [BotScheduler] SchedulerWorker | loop TICK | type=${selectedJob} account=acc_001 status=${data.status} processed=${data.stats?.processed ?? 0}`

        setFeed(prev => [line, ...prev].slice(0, MAX_FEED_ENTRIES))
      } catch (err) {
        setError(err.message)
        const timestamp = new Date().toLocaleTimeString()
        const line = `[${new Date().toLocaleTimeString()}] [BotScheduler] ERROR | type=${selectedJob} | ${err.message}`
        setFeed(prev => [line, ...prev].slice(0, MAX_FEED_ENTRIES))
      }
    }

    poll()
    intervalRef.current = setInterval(poll, POLL_INTERVAL_MS)

    return () => clearInterval(intervalRef.current)
  }, [selectedJob])

  return { status, feed, error }
}
